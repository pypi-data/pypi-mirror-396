"""
Parallelism and Rate Limiting Manager for Task Processing

This module provides resource-level concurrency control and rate limiting for processing
entities/items in a controlled manner.

Key Concepts:
- parallelism_max: Maximum number of entities being processed simultaneously at any moment
- parallelism_throttle: Maximum rate (entities/second) at which new processing can start
- ProcessResult: Future-like result objects that store either values or exceptions

Classes:
- ThreadExecutor: For I/O-bound tasks (API calls, file I/O) - uses ThreadPoolExecutor
- LoopExecutor: For CPU/GPU-bound tasks (OCR, models) - uses sequential for-loop
- BatchExecutor: For batch operations (NER, inference) - processes in batches

Example:
    >>> # I/O-bound task
    >>> config = ParallelismConfig(max_parallel=4, throttle=10)
    >>> executor = ThreadExecutor(config)
    >>> results = executor.process(files, extract_text)
    >>> for r in results:
    ...     if r.successful():
    ...         data = r.result()
    >>> 
    >>> # CPU/GPU-bound task
    >>> processor = LoopExecutor(config)
    >>> results = processor.process(images, ocr_process)
"""

import time
import threading
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Callable, Any, TypeVar, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


@dataclass
class ParallelismConfig:
    """
    Configuration for controlling parallelism and throughput.
    
    Attributes:
        max_parallel: Maximum number of entities being processed simultaneously.
                     Acts as a concurrency limit (semaphore).
                     None = unlimited concurrency
        
        throttle: Maximum rate of entities starting processing per second.
                 Acts as a rate limiter.
                 None = unlimited rate
    
    Examples:
        >>> # At most 4 entities processed at once, no rate limit
        >>> config = ParallelismConfig(max_parallel=4, throttle=None)
        
        >>> # Unlimited concurrency, but max 10 entities/second
        >>> config = ParallelismConfig(max_parallel=None, throttle=10)
        
        >>> # Max 2 concurrent, max 5/second rate
        >>> config = ParallelismConfig(max_parallel=2, throttle=5)
    """
    max_parallel: Optional[int] = None
    throttle: Optional[int] = None
    
    def __post_init__(self):
        """Validate configuration values"""
        if self.max_parallel is not None and self.max_parallel < 1:
            raise ValueError(f"max_parallel must be >= 1, got {self.max_parallel}")
        if self.throttle is not None and self.throttle < 1:
            raise ValueError(f"throttle must be >= 1, got {self.throttle}")
    
    def has_limits(self) -> bool:
        """Check if any limits are configured"""
        return self.max_parallel is not None or self.throttle is not None
    
    def should_use_threading(self) -> bool:
        """
        Determine if threading should be used based on config.
        
        Threading only makes sense if max_parallel > 1.
        """
        return self.max_parallel is not None and self.max_parallel > 1


class RateLimiter:
    """
    Token bucket rate limiter.
    
    Allows up to `rate` operations per second, smoothing out bursts.
    
    Attributes:
        rate: Maximum operations per second
    
    Example:
        >>> limiter = RateLimiter(rate=10)
        >>> limiter.acquire()  # Blocks until a token is available
    """
    
    def __init__(self, rate: int):
        """
        Initialize rate limiter.
        
        Args:
            rate: Maximum operations per second (must be >= 1)
        
        Raises:
            ValueError: If rate < 1
        """
        if rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate}")
        
        self.rate = rate
        self.tokens = 1.0  # Start with 1 token, not full bucket
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def acquire(self) -> None:
        """
        Acquire a token, blocking until one is available.
        
        Uses token bucket algorithm: tokens regenerate at `rate` per second,
        up to a maximum of `rate` tokens.
        """
        while True:
            with self.lock:
                now = time.time()
                elapsed = now - self.last_update
                
                # Add tokens based on elapsed time
                self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
                self.last_update = now
                
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
            
            # Wait a bit before trying again
            # Sleep time is calculated to minimize busy waiting
            time.sleep(1.0 / (self.rate * 10))


class ParallelismController:
    """
    Controls concurrency and rate limiting for entity processing.
    
    This ensures:
    1. No more than `max_parallel` entities are processing at any moment (if set)
    2. Entities start processing at most `throttle` per second (if set)
    
    Works with any execution model: for-loops, ThreadPools, async, etc.
    
    Example:
        >>> config = ParallelismConfig(max_parallel=4, throttle=10)
        >>> controller = ParallelismController(config)
        >>> 
        >>> # Use as context manager
        >>> with controller:
        ...     process_entity()  # Automatically acquires/releases
        >>> 
        >>> # Or manually
        >>> controller.acquire()
        >>> try:
        ...     process_entity()
        >>> finally:
        ...     controller.release()
    """
    
    def __init__(self, config: ParallelismConfig):
        """
        Initialize controller with given config.
        
        Args:
            config: ParallelismConfig instance
        """
        self.config = config
        self._semaphore: Optional[threading.Semaphore] = None
        self._rate_limiter: Optional[RateLimiter] = None
        
        # Initialize semaphore for concurrency control
        if config.max_parallel is not None:
            self._semaphore = threading.Semaphore(config.max_parallel)
            logger.debug(f"Initialized semaphore with {config.max_parallel} permits")
        
        # Initialize rate limiter
        if config.throttle is not None:
            self._rate_limiter = RateLimiter(config.throttle)
            logger.debug(f"Initialized rate limiter at {config.throttle}/second")
    
    def acquire(self) -> None:
        """
        Acquire permission to process an entity.
        
        Blocks until:
        1. A concurrency slot is available (if max_parallel is set)
        2. Rate limit allows (if throttle is set)
        
        The order matters: we acquire semaphore first, then wait for rate limit.
        This prevents holding a semaphore slot while waiting for rate limit.
        """
        # Wait for rate limit first (doesn't hold resources)
        if self._rate_limiter:
            self._rate_limiter.acquire()
        
        # Then acquire semaphore (holds a concurrency slot)
        if self._semaphore:
            self._semaphore.acquire()
    
    def release(self) -> None:
        """
        Release concurrency slot.
        
        Note: Only semaphore needs releasing; rate limiter is one-way.
        """
        if self._semaphore:
            self._semaphore.release()
    
    def __enter__(self):
        """Context manager entry - acquire permits"""
        self.acquire()
        return self
    
    def __exit__(self, *args):
        """Context manager exit - release permits"""
        self.release()


class ProcessResult:
    """
    A Future-like result object that stores either a successful result or an exception.
    
    Mimics the concurrent.futures.Future interface for result retrieval.
    
    Attributes:
        _result: The successful result value (if no exception)
        _exception: The exception that occurred (if failed)
    
    Example:
        >>> result = ProcessResult(value=42)
        >>> result.result()  # Returns 42
        >>> 
        >>> result = ProcessResult(exception=ValueError("Error"))
        >>> result.result()  # Raises ValueError
    """
    
    def __init__(self, value: Any = None, exception: Optional[Exception] = None):
        """
        Initialize a ProcessResult.
        
        Args:
            value: The successful result value (mutually exclusive with exception)
            exception: The exception that occurred (mutually exclusive with value)
        """
        if value is not None and exception is not None:
            raise ValueError("Cannot specify both value and exception")
        
        self._result = value
        self._exception = exception
    
    def result(self) -> Any:
        """
        Return the result or raise the exception.
        
        Returns:
            The result value if successful
        
        Raises:
            The stored exception if processing failed
        """
        if self._exception is not None:
            raise self._exception
        return self._result
    
    def exception(self) -> Optional[Exception]:
        """
        Return the exception without raising it.
        
        Returns:
            The exception if one occurred, None otherwise
        """
        return self._exception
    
    def successful(self) -> bool:
        """
        Check if the result was successful.
        
        Returns:
            True if no exception occurred, False otherwise
        """
        return self._exception is None
    
    def __repr__(self) -> str:
        if self._exception is not None:
            return f"ProcessResult(exception={self._exception!r})"
        return f"ProcessResult(value={self._result!r})"


class Executor(ABC):
    """
    Abstract base class for all executors.
    
    Provides a common interface for processing items with different execution strategies.
    All executors support:
    - Parallelism control (max concurrent operations)
    - Rate limiting (max operations per second)
    - Exception handling (stores exceptions, doesn't stop processing)
    """
    
    def __init__(self, config: ParallelismConfig):
        """
        Initialize executor with given config.
        
        Args:
            config: ParallelismConfig instance
        """
        self.config = config
    
    @abstractmethod
    def process(
        self, 
        items: List[T], 
        process_fn: Callable[[T], R],
        **kwargs
    ) -> List[ProcessResult]:
        """
        Process items and return ProcessResult objects.
        
        Args:
            items: List of items to process
            process_fn: Function to apply to each item
            **kwargs: Additional executor-specific parameters
        
        Returns:
            List of ProcessResult objects in same order as items.
            Call .result() on each to get value or raise exception.
        """
        pass


class ThreadExecutor(Executor):
    """
    Executes items using ThreadPoolExecutor with parallelism and rate limiting.
    
    Use for I/O-bound tasks (API calls, file I/O, network requests).
    Respects both max_parallel (concurrency limit) and throttle (rate limit).
    
    Example:
        >>> config = ParallelismConfig(max_parallel=4, throttle=10)
        >>> executor = ThreadExecutor(config)
        >>> 
        >>> def fetch_data(url):
        ...     return requests.get(url).text
        >>> 
        >>> results = executor.process(urls, fetch_data)
        >>> for r in results:
        ...     if r.successful():
        ...         print(r.result())
    """
    
    def __init__(self, config: ParallelismConfig):
        """
        Initialize thread executor with given config.
        
        Args:
            config: ParallelismConfig instance
        """
        super().__init__(config)
        self.controller = ParallelismController(config)
    
    def process(
        self, 
        items: List[T], 
        process_fn: Callable[[T], R]
    ) -> List[ProcessResult]:
        """
        Process items using ThreadPoolExecutor with parallelism control.
        
        Args:
            items: List of items to process
            process_fn: Function to apply to each item. Should take one item
                       and return a result. Exceptions are caught and stored.
        
        Returns:
            List of ProcessResult objects in same order as items.
            Call .result() on each to get value or raise stored exception.
        
        Example:
            >>> results = executor.process(files, extract_text_with_tika)
            >>> for r in results:
            ...     try:
            ...         text = r.result()
            ...     except Exception as e:
            ...         print(f"Failed: {e}")
        """
        if not items:
            return []
        
        # If no limits configured, use fastest method
        if not self.config.has_limits():
            logger.debug(f"Processing {len(items)} items with ThreadPool (no limits)")
            return self._process_unlimited(items, process_fn)
        
        # With limits
        logger.debug(
            f"Processing {len(items)} items with ThreadPool: "
            f"max_parallel={self.config.max_parallel}, "
            f"throttle={self.config.throttle}"
        )
        return self._process_limited(items, process_fn)
    
    def _process_unlimited(
        self, 
        items: List[T], 
        process_fn: Callable[[T], R]
    ) -> List[ProcessResult]:
        """
        Process with ThreadPool without limits.
        
        Uses a reasonable default thread count based on item count.
        """
        # Use reasonable thread count (not too many)
        max_workers = min(len(items), 10)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_fn, item) for item in items]
            results = []
            for i, future in enumerate(futures):
                try:
                    result_value = future.result()
                    results.append(ProcessResult(value=result_value))
                except Exception as e:
                    logger.error(f"Processing error on item {i+1}: {e}", exc_info=True)
                    results.append(ProcessResult(exception=e))
        return results
    
    def _process_limited(
        self, 
        items: List[T], 
        process_fn: Callable[[T], R]
    ) -> List[ProcessResult]:
        """
        Process with ThreadPool respecting limits.
        
        Each thread acquires permits before processing, ensuring we respect
        both concurrency and rate limits across all threads.
        """
        # Use parallelism_max as thread pool size
        max_workers = self.config.max_parallel or 5
        
        def wrapped_fn(item_with_idx):
            idx, item = item_with_idx
            # Each thread acquires permits before processing
            with self.controller:
                try:
                    result = process_fn(item)
                    logger.debug(f"Thread processed item {idx+1}/{len(items)}")
                    return (idx, ProcessResult(value=result))
                except Exception as e:
                    logger.error(f"Processing error on item {idx+1}: {e}", exc_info=True)
                    return (idx, ProcessResult(exception=e))
        
        # Initialize results list with placeholder ProcessResults
        results = [ProcessResult(value=None)] * len(items)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks with their indices
            futures = [
                executor.submit(wrapped_fn, (idx, item)) 
                for idx, item in enumerate(items)
            ]
            
            # Collect results as they complete
            for future in as_completed(futures):
                idx, result = future.result()
                results[idx] = result
        
        return results


class LoopExecutor(Executor):
    """
    Executes items sequentially using a for-loop with rate limiting.
    
    Use for CPU/GPU-bound tasks (OCR, model inference) where parallelism
    doesn't help or hurts performance (e.g., single GPU).
    
    Only respects throttle (rate limit), not max_parallel (already sequential).
    
    Example:
        >>> config = ParallelismConfig(max_parallel=None, throttle=10)
        >>> processor = LoopExecutor(config)
        >>> 
        >>> def ocr_image(image):
        ...     return easyocr_reader.readtext(image)
        >>> 
        >>> results = processor.process(images, ocr_image)
        >>> for r in results:
        ...     if r.successful():
        ...         print(r.result())
    """
    
    def __init__(self, config: ParallelismConfig):
        """
        Initialize loop processor with given config.
        
        Args:
            config: ParallelismConfig instance (only throttle is used)
        """
        super().__init__(config)
        # Create controller with only rate limiting (no semaphore for sequential)
        rate_limit_only_config = ParallelismConfig(
            max_parallel=None,  # Ignore concurrency for sequential processing
            throttle=config.throttle
        )
        self.controller = ParallelismController(rate_limit_only_config)
    
    def process(
        self, 
        items: List[T], 
        process_fn: Callable[[T], R]
    ) -> List[ProcessResult]:
        """
        Process items sequentially with rate limiting.
        
        Args:
            items: List of items to process
            process_fn: Function to apply to each item. Should take one item
                       and return a result. Exceptions are caught and stored.
        
        Returns:
            List of ProcessResult objects in same order as items.
            Call .result() on each to get value or raise stored exception.
        
        Example:
            >>> results = processor.process(images, ocr_process)
            >>> for r in results:
            ...     try:
            ...         text = r.result()
            ...     except Exception as e:
            ...         print(f"Failed: {e}")
        """
        if not items:
            return []
        
        # If no rate limit configured, use fastest method
        if self.config.throttle is None:
            logger.debug(f"Processing {len(items)} items sequentially (no rate limit)")
            return self._process_unlimited(items, process_fn)
        
        # With rate limiting
        logger.debug(
            f"Processing {len(items)} items sequentially with rate limit: "
            f"throttle={self.config.throttle}/sec"
        )
        return self._process_limited(items, process_fn)
    
    def _process_unlimited(
        self, 
        items: List[T], 
        process_fn: Callable[[T], R]
    ) -> List[ProcessResult]:
        """Process items sequentially without limits (fastest path)"""
        results = []
        for i, item in enumerate(items):
            try:
                results.append(ProcessResult(value=process_fn(item)))
            except Exception as e:
                logger.error(f"Processing error on item {i+1}: {e}", exc_info=True)
                results.append(ProcessResult(exception=e))
        return results
    
    def _process_limited(
        self, 
        items: List[T], 
        process_fn: Callable[[T], R]
    ) -> List[ProcessResult]:
        """
        Process items sequentially with rate limiting.
        
        Each item acquires permits before processing, ensuring we never
        exceed the rate limit.
        """
        results = []
        for i, item in enumerate(items):
            # Acquire rate limit permit (blocks if necessary)
            with self.controller:
                try:
                    result = process_fn(item)
                    results.append(ProcessResult(value=result))
                    logger.debug(f"Processed item {i+1}/{len(items)}")
                except Exception as e:
                    logger.error(f"Processing error on item {i+1}: {e}", exc_info=True)
                    results.append(ProcessResult(exception=e))
        return results


class BatchExecutor(Executor):
    """
    Process items in batches with parallelism control.
    
    Useful for model inference where batching improves throughput
    (e.g., neural network inference, OCR, NER).
    
    Example:
        >>> config = ParallelismConfig(max_parallel=None, throttle=10)
        >>> processor = BatchExecutor(config)
        >>> 
        >>> def process_batch(texts):
        ...     # Process batch of texts together
        ...     return model.predict(texts)
        >>> 
        >>> results = processor.process(
        ...     all_texts,
        ...     process_batch,
        ...     batch_size=10
        ... )
    """
    
    def __init__(self, config: ParallelismConfig):
        """
        Initialize batch processor with given config.
        
        Args:
            config: ParallelismConfig instance
        """
        super().__init__(config)
        self.controller = ParallelismController(config)
    
    def process(
        self, 
        items: List[T], 
        batch_fn: Callable[[List[T]], List[R]],
        batch_size: int = 1
    ) -> List[ProcessResult]:
        """
        Process items in batches.
        
        Args:
            items: List of items to process
            batch_fn: Function that takes a batch (list) and returns a list of results.
                     The function should return results in the same order as input.
                     Length of output must match length of input batch.
            batch_size: Size of each batch. Should be tuned based on model capacity
                       and memory constraints.
        
        Returns:
            List of ProcessResult objects in same order as items.
            Call .result() on each to get value or raise stored exception.
        
        Note:
            If a batch fails, all items in that batch will have the same exception.
            The entire batch is processed atomically (acquires permits once per batch,
            not once per item), since batching assumes the batch is processed together.
        
        Example:
            >>> # Process texts in batches of 10
            >>> def ner_batch(texts):
            ...     return ner_model.process_batch(texts)
            >>> 
            >>> results = processor.process(
            ...     texts,
            ...     ner_batch,
            ...     batch_size=10
            ... )
            >>> for r in results:
            ...     try:
            ...         entities = r.result()
            ...     except Exception as e:
            ...         print(f"Failed: {e}")
        """
        if not items:
            return []
        
        if batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {batch_size}")
        
        results = []
        num_batches = (len(items) + batch_size - 1) // batch_size
        
        logger.debug(
            f"Processing {len(items)} items in {num_batches} batches "
            f"(batch_size={batch_size})"
        )
        
        for batch_idx in range(0, len(items), batch_size):
            batch = items[batch_idx:batch_idx + batch_size]
            batch_num = (batch_idx // batch_size) + 1
            
            # Acquire permits for the entire batch
            # This ensures we don't exceed concurrency limits
            if self.config.has_limits():
                with self.controller:
                    try:
                        batch_results = batch_fn(batch)
                        
                        # Validate batch results
                        if len(batch_results) != len(batch):
                            logger.error(
                                f"Batch {batch_num}: Expected {len(batch)} results, "
                                f"got {len(batch_results)}. Padding with None."
                            )
                            # Pad or truncate to match expected length
                            if len(batch_results) < len(batch):
                                batch_results.extend([None] * (len(batch) - len(batch_results)))
                            else:
                                batch_results = batch_results[:len(batch)]
                        
                        # Wrap each result in ProcessResult
                        results.extend([ProcessResult(value=r) for r in batch_results])
                        logger.debug(f"Processed batch {batch_num}/{num_batches}")
                    except Exception as e:
                        logger.error(f"Batch processing error on batch {batch_num}: {e}", exc_info=True)
                        # All items in failed batch get the same exception
                        results.extend([ProcessResult(exception=e) for _ in batch])
            else:
                # No limits, process directly
                try:
                    batch_results = batch_fn(batch)
                    
                    # Validate batch results
                    if len(batch_results) != len(batch):
                        logger.error(
                            f"Batch {batch_num}: Expected {len(batch)} results, "
                            f"got {len(batch_results)}. Padding with None."
                        )
                        if len(batch_results) < len(batch):
                            batch_results.extend([None] * (len(batch) - len(batch_results)))
                        else:
                            batch_results = batch_results[:len(batch)]
                    
                    # Wrap each result in ProcessResult
                    results.extend([ProcessResult(value=r) for r in batch_results])
                except Exception as e:
                    logger.error(f"Batch processing error on batch {batch_num}: {e}", exc_info=True)
                    # All items in failed batch get the same exception
                    results.extend([ProcessResult(exception=e) for _ in batch])
        
        return results


# Convenience functions for simple use cases
def process_with_threads(
    items: List[T],
    process_fn: Callable[[T], R],
    max_parallel: Optional[int] = None,
    throttle: Optional[int] = None
) -> List[ProcessResult]:
    """
    Convenience function to process items with ThreadPool.
    
    Use for I/O-bound tasks (API calls, file I/O, network requests).
    
    Args:
        items: List of items to process
        process_fn: Function to apply to each item
        max_parallel: Maximum concurrent threads (None = unlimited)
        throttle: Maximum operations per second (None = unlimited)
    
    Returns:
        List of ProcessResult objects in same order as items
    
    Example:
        >>> results = process_with_threads(
        ...     urls,
        ...     fetch_url,
        ...     max_parallel=4,
        ...     throttle=10
        ... )
        >>> for r in results:
        ...     if r.successful():
        ...         print(r.result())
    """
    config = ParallelismConfig(max_parallel=max_parallel, throttle=throttle)
    executor = ThreadExecutor(config)
    return executor.process(items, process_fn)


def process_with_loop(
    items: List[T],
    process_fn: Callable[[T], R],
    throttle: Optional[int] = None
) -> List[ProcessResult]:
    """
    Convenience function to process items sequentially with rate limiting.
    
    Use for CPU/GPU-bound tasks (OCR, model inference).
    
    Args:
        items: List of items to process
        process_fn: Function to apply to each item
        throttle: Maximum operations per second (None = unlimited)
    
    Returns:
        List of ProcessResult objects in same order as items
    
    Example:
        >>> results = process_with_loop(
        ...     images,
        ...     ocr_process,
        ...     throttle=10
        ... )
        >>> for r in results:
        ...     if r.successful():
        ...         print(r.result())
    """
    config = ParallelismConfig(max_parallel=None, throttle=throttle)
    processor = LoopExecutor(config)
    return processor.process(items, process_fn)

