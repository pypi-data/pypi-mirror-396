import re
import logging
from spacy_download import load_spacy
from flair.data import Sentence
from flair.models import SequenceTagger
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.utils import get_stop_words
import itertools
import numpy as np
import math
import nltk
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

SPACY_NER_MODELS = {
    "english": lambda: load_spacy(
        "en_core_web_sm",
        disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"],
    )
}
FLAIR_NER_MODELS = {"english": lambda: SequenceTagger.load("flair/ner-english")}
REGEX_NER_MODELS = {
    "IP_ADDRESS": [
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::(?:[0-9]|[1-9][0-9]{1,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))?\b",
    ],
    "PHONE": r"(?:(?:\+(?:\d{1,3}[ .-]?)?(?:\(\d{1,3}\)[ .-]?)?)(?:\d{2,5}[ .-]?){1,3}|\d{2,5}[ .-]\d{2,5}(?:[ .-]\d{2,5}){0,2})\b",
    "EMAIL": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)+\b",
    "URL": r"\b(?:(?:https?|ftp|sftp|ftps|ssh|file|mailto|git|onion|ipfs|ipns):\/\/|www\.)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}(?::\d+)?(?:\/(?:[-a-z0-9\/_.,~%+:@]|(?:%[0-9a-f]{2}))*)?(?:\?(?:[-a-z0-9\/_.,~%+:@=&]|(?:%[0-9a-f]{2}))*)?(?:#(?:[-a-z0-9\/_.,~%+:@=&]|(?:%[0-9a-f]{2}))*)?|(?:https?:\/\/)?[a-z2-7]{16,56}\.onion(?:\/(?:[-a-z0-9\/_.,~%+:@]|(?:%[0-9a-f]{2}))*)?(?:\?(?:[-a-z0-9\/_.,~%+:@=&]|(?:%[0-9a-f]{2}))*)?(?:#(?:[-a-z0-9\/_.,~%+:@=&]|(?:%[0-9a-f]{2}))*)\b",
}

BASE_TO_ONTONOTES_LABELMAP = {"PER": "PERSON"}
BASE_ALLOWED_LABELS = ["PERSON", "ORG", "LOC", "NORP", "GPE", "PRODUCT", "DATE", "PHONE", "IP_ADDRESS", "EMAIL", "URL"]


def _sumy__get_best_sentences(sentences, rating, *args, **kwargs):
    from operator import attrgetter
    from sumy.summarizers._summarizer import SentenceInfo

    rate = rating
    if isinstance(rating, dict):
        assert not args and not kwargs
        rate = lambda s: rating[s]
    infos = (SentenceInfo(s, o, rate(s, *args, **kwargs)) for o, s in enumerate(sentences))
    infos = sorted(infos, key=attrgetter("rating"), reverse=True)
    return tuple((i.sentence, i.rating, i.order) for i in infos)


def _sumy__luhn_call(summarizer, document):
    words = summarizer._get_significant_words(document.words)
    return _sumy__get_best_sentences(document.sentences, summarizer.rate_sentence, words)


def _sumy__lsa_call(summarizer, document):
    summarizer._ensure_dependecies_installed()
    dictionary = summarizer._create_dictionary(document)
    if not dictionary:
        return ()
    matrix = summarizer._create_matrix(document, dictionary)
    matrix = summarizer._compute_term_frequency(matrix)
    from numpy.linalg import svd as singular_value_decomposition

    u, sigma, v = singular_value_decomposition(matrix, full_matrices=False)
    ranks = iter(summarizer._compute_ranks(sigma, v))
    return _sumy__get_best_sentences(document.sentences, lambda s: next(ranks))


def get_nltk_tokenizer(language: str) -> Tokenizer:
    nltk.data.find("tokenizers/punkt")
    return Tokenizer(language)


class NERObject(BaseModel):
    name: str
    label: str
    score: float = 0.0
    start: int
    count: int
    context: str | None = None
    comentions: list[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")

    def __repr__(self):
        return f"NERObject(label={self.label},name={self.name})"


def postprocess_ner(entities: list[NERObject], whitelisted_labels=None, max_entities=None):
    if whitelisted_labels is not None:
        entities = [e for e in entities if e.label in whitelisted_labels]
    entities = sorted(entities, key=lambda x: x.name)
    final_entities = []
    for _, group in itertools.groupby(entities, key=lambda x: x.name):
        group = list(group)
        best_entity = max(group, key=lambda x: x.score * x.count)
        merged_data = {
            "name": best_entity.name,
            "label": best_entity.label,
            "score": best_entity.score,
            "context": best_entity.context,
            "count": sum(e.count for e in group),
            "start": best_entity.start,
        }
        all_fields = best_entity.model_fields.keys()
        for field in all_fields:
            if field in merged_data:
                continue
            values = [getattr(e, field, None) for e in group if getattr(e, field, None) is not None]
            if not values:
                continue
            if isinstance(values[0], list):
                merged_data[field] = list(set(itertools.chain.from_iterable(values or [])))
            else:
                merged_data[field] = getattr(best_entity, field, None)
        final_entities.append(NERObject(**merged_data))
    final_entities = sorted(final_entities, key=lambda x: x.score * x.count, reverse=True)
    if max_entities and len(final_entities) > max_entities:
        final_entities = final_entities[:max_entities]
    return final_entities


def compute_ner(
    language,
    sentences,
    spacy_model,
    flair_model=None,
    context_width=150,
    with_scores=True,
    with_comentions=True,
    with_context=True,
):
    sentence_starts = [0] + [len(s[0]) + 1 for s in sentences]
    del sentence_starts[-1]
    sentence_starts = list(np.cumsum(sentence_starts))
    text = "\n".join([s[0] for s in sentences])
    min_score = 1.0
    entities: list[NERObject] = []

    # FLAIR model (if not fast)
    if flair_model:
        input = [Sentence(sentence[0]) for sentence in sentences]
        flair_model.predict(input)
        output = [e for sentence in input for e in sentence.get_spans("ner")]
        flair_entities = [
            NERObject(
                name=entity.text,
                label=BASE_TO_ONTONOTES_LABELMAP.get(
                    entity.annotation_layers["ner"][0].value,
                    entity.annotation_layers["ner"][0].value,
                ),
                score=entity.score,
                start=sentence_starts[input.index(entity[0].sentence)] + entity[0].start_position,
                count=1,
            )
            for entity in output
        ]
        min_score = min([min_score] + [e.score for e in flair_entities])
        entities += flair_entities
        del flair_entities

    # REGEX model
    for label, regexes in REGEX_NER_MODELS.items():
        if not isinstance(regexes, list):
            regexes = [regexes]
        for regex in regexes:
            regex_entities = [
                NERObject(
                    name=match.group(),
                    label=label,
                    score=min_score - 0.5,
                    count=1,
                    start=match.start(),
                )
                for match in re.finditer(regex, text)
            ]
            entities += regex_entities
    min_score = min([min_score] + [e.score for e in regex_entities])

    # SPACY model
    chunks = []
    chunk_start_offsets = []
    current_chunk = []
    current_length = 0
    offset = 0
    for sentence, _ in sentences:
        sentence_len = len(sentence) + 1
        if sentence_len > spacy_model.max_length:
            truncated = sentence[: spacy_model.max_length - 1]
            chunks.append(truncated)
            chunk_start_offsets.append(offset)
            offset += sentence_len
            continue
        if current_length + sentence_len > spacy_model.max_length:
            chunks.append("\n".join(current_chunk))
            chunk_start_offsets.append(offset - current_length)
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_len
        offset += sentence_len
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        chunk_start_offsets.append(offset - current_length)
    for i, chunk in enumerate(chunks):
        doc = spacy_model(chunk)
        chunk_offset = chunk_start_offsets[i]
        for entity in doc.ents:
            entities.append(
                NERObject(
                    name=entity.text,
                    label=BASE_TO_ONTONOTES_LABELMAP.get(entity.label_, entity.label_),
                    score=min_score - 0.5,
                    start=chunk_offset + entity.start_char,
                    count=1,
                )
            )

    # Reformatting for consistency
    if not entities:
        return []
    if with_scores:
        min_entity_score = min([e.score for e in entities])
        max_entity_score = max([e.score for e in entities])
        entity_score_range = 1 if min_entity_score == max_entity_score else (max_entity_score - min_entity_score)
        for e in entities:
            e.score = (e.score - min_entity_score) / entity_score_range
        scores = list(np.searchsorted(sentence_starts, [e.start + 1 for e in entities]))
        scores = [sentences[i - 1][1] for i in scores]
        scores = [scores[i] + 10 * entities[i].score for i in range(len(entities))]
        for i in range(len(entities)):
            entities[i].score = scores[i]
    else:
        for i in range(len(entities)):
            entities[i].score = 0.0
    if with_comentions:
        for i in range(len(entities)):
            entity = entities[i]
            comentions = [
                entities[j].name
                for j in range(len(entities))
                if j != i and abs(entities[j].start - entity.start) < math.ceil(context_width / 2)
            ]
            entities[i].comentions = comentions
    if with_context:
        for i in range(len(entities)):
            entity = entities[i]
            if entity.start >= 0 and entity.start < len(text):
                left = max(0, entity.start - math.floor(context_width / 2))
                right = min(len(text), entity.start + math.ceil(context_width / 2))
                context = ("[..]" if left > 0 else "") + text[left:right] + ("[..]" if right < len(text) else "")
                entities[i].context = context
    return entities


def _compress_by_frequency(text, language, target_chars):
    tokenizer = get_nltk_tokenizer(language)
    parser = PlaintextParser.from_string(text, tokenizer)
    sentences = parser.document.sentences
    if not sentences:
        return text
    current_size = len(text)
    if current_size <= target_chars:
        return text
    word_freq = {}
    for sentence in sentences:
        for word in sentence.words:
            word_str = str(word)
            normalized = word_str.lower()
            word_freq[normalized] = word_freq.get(normalized, 0) + 1
    sentence_scores = []
    for sentence in sentences:
        score = 0
        for word in sentence.words:
            try:
                word_str = word.value if hasattr(word, 'value') else str(word)
            except (AttributeError, TypeError):
                word_str = str(word)
            normalized = word_str.lower()
            score += word_freq.get(normalized, 0)
        sentence_scores.append((sentence._text, score, sentence))
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    selected = []
    current_chars = 0
    for sent_text, score, sent_obj in sentence_scores:
        if current_chars < target_chars:
            selected.append((sent_obj, sent_text))
            current_chars += len(sent_text) + 1
    selected.sort(key=lambda x: sentences.index(x[0]))
    result = " ".join([s[1] for s in selected])
    return result


def _run_single_summarizer(text, language, max_chars, method, with_scores=False):
    text_len = len(text)
    logger.debug(f"  Tokenizing {text_len:,} chars for {method} summarization...")
    tokenizer = get_nltk_tokenizer(language)
    stemmer = Stemmer(language)
    parser = PlaintextParser.from_string(text, tokenizer)
    if method == "luhn":
        summarizer = LuhnSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)
        scored_sentences = iter(_sumy__luhn_call(summarizer, parser.document))
    elif method == "lsa":
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)
        scored_sentences = iter(_sumy__lsa_call(summarizer, parser.document))
    else:
        raise ValueError(f"Unknown method: {method}. Use 'luhn' or 'lsa'")
    summary = []
    summary_chars = 0
    summary_chars_penultimate = 0
    sentence_count = 0
    while summary_chars < max_chars:
        try:
            next_sentence = next(scored_sentences)
            summary.append(next_sentence)
            summary_chars_penultimate = summary_chars
            summary_chars += len(" " + next_sentence[0]._text)
            sentence_count += 1
        except StopIteration:
            break
    summary = sorted(summary, key=lambda x: x[2])
    summary = [(sentence[0]._text, sentence[1]) for sentence in summary]
    if summary_chars > max_chars:
        final_chars = max_chars - summary_chars_penultimate
        summary[-1] = (
            summary[-1][0][:final_chars],
            summary[-1][1],
        )
    if not with_scores:
        summary = " ".join([s[0] for s in summary])
    else:
        min_score = min([s[1] for s in summary]) if summary else 0
        max_score = max([min_score] + [s[1] for s in summary])
        score_range = 1 if min_score == max_score else (max_score - min_score)
        summary = [(s[0], (s[1] - min_score) / score_range) for s in summary]
    final_size = len(summary) if isinstance(summary, str) else sum(len(s[0]) + 1 for s in summary)
    logger.debug(f"  Final summary size: {final_size:,} chars")
    return summary


def get_extractive_summary(text, language, max_chars, fast=False, with_scores=False):
    """
    Perform extractive summarization using bracket-based algorithm selection.
    
    Each summarizer handles a specific character range bracket:
    - FREQUENCY: [∞, 1M] - Fast O(n) algorithm for texts over 1M chars
    - LUHN/LSA: [1M, 0] - Quality algorithms for texts up to 1M chars
    Args:
        text: Input text to summarize
        language: Language for tokenization
        max_chars: Maximum characters in final summary
        fast: If True, use luhn (faster); if False, use lsa (more accurate) for <=1M texts
        with_scores: Return scores with sentences
    Returns:
        String text if with_scores=False, or list of (sentence, score) tuples if with_scores=True
    """
    text_len = len(text)
    current_text = text
    summarization_done = False
    if text_len > 1_000_000:
        stage_target = max(1_000_000, max_chars)
        method = "freqanalysis"
        logger.debug(f"Compressing with {method.upper()} from {text_len:,} chars to {stage_target:,}")
        current_text = _compress_by_frequency(current_text, language, stage_target)
        text_len = len(current_text)
        summarization_done = True
    if text_len <= 1_000_000:
        if max_chars < text_len:
            stage_target = max_chars
            final_method = "luhn" if fast else "lsa"
            logger.debug(f"Compressing with {final_method.upper()} from {text_len:,} chars to {stage_target:,}")
            result = _run_single_summarizer(current_text, language, stage_target, final_method, with_scores=with_scores)
            logger.debug(f"<<< STAGE 2 COMPLETE")
            return result
        else:
            logger.debug(f"\n⊘ Stage 2 skipped: max_chars {max_chars:,} ≥ current text {text_len:,}")         
            if summarization_done:
                if with_scores:
                    final_method = "luhn" if fast else "lsa"
                    result = _run_single_summarizer(current_text, language, text_len, final_method, with_scores=True)
                else:
                    result = current_text
                return result
            else:
                if with_scores:
                    final_method = "luhn" if fast else "lsa"
                    result = _run_single_summarizer(current_text, language, text_len, final_method, with_scores=True)
                else:
                    result = current_text
                return result
    else:
        if with_scores:
            final_method = "luhn" if fast else "lsa"
            result = _run_single_summarizer(current_text, language, max_chars, final_method, with_scores=True)
        else:
            result = current_text
        return result

def ner_pipe(
    text,
    language,
    spacy_model,
    flair_model=None,
    fast=False,
    compression_ratio="auto",
    with_scores=True,
    with_comentions=True,
    with_context=True,
):
    """
    Perform NER on text with optional extractive summarization.
    
    Uses progressive refinement for large texts:
    - Stage 1: If text >1M chars, use frequency-based scoring (O(n)) to reduce to ~100K
    - Stage 2: Use luhn or lsa for final high-quality selection
    
    Args:
        text: Input text
        language: Language code
        spacy_model: Loaded spacy model
        flair_model: Optional flair model for better accuracy
        fast: If True, use faster methods (luhn vs lsa for summarization)
        compression_ratio: Ratio to compress text with summarization (auto = dynamic based on size)
        with_scores: Include confidence scores
        with_comentions: Include co-mentioned entities
        with_context: Include context windows
    
    Returns:
        List of NERObject entities
    """
    if compression_ratio == "auto":
        compression_ratio = max(1.0, len(text) / 15000) if fast else 1.0
    sentences = get_extractive_summary(
        text, 
        language, 
        int(len(text) / compression_ratio), 
        fast=fast,
        with_scores=True
    )
    ner = compute_ner(language, sentences, spacy_model, flair_model, 150, with_scores, with_comentions, with_context)
    return ner


def get_ner_handler(language, fast=False):
    """
    Get a configured NER handler function.
    Args:
        language: Language code
        fast: If True, skip Flair model and use faster summarization
    Returns:
        A function that performs NER on text
    """
    try:
        get_nltk_tokenizer(language)
    except LookupError:
        language = "english"
    spacy_model = SPACY_NER_MODELS.get(language, SPACY_NER_MODELS["english"])()
    flair_model = None if fast else FLAIR_NER_MODELS.get(language, FLAIR_NER_MODELS["english"])()
    return lambda text, compression_ratio="auto", with_scores=True, with_comentions=True, with_context=True: ner_pipe(
        text, language, spacy_model, flair_model, fast, compression_ratio, with_scores, with_comentions, with_context
    )