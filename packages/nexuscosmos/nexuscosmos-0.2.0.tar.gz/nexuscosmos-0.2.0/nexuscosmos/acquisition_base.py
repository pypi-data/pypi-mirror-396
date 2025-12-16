"""
Generic base classes for data acquisition from any astronomical data source.

These abstract base classes define the interface that dataset-specific clients
must implement. This allows plugging in different data sources (Horizons, MPC,
GAIA, custom APIs) while reusing cache, rate-limiting, and configuration logic.

Example (Quick custom API):
    from nexuscosmos import GenericAcquisitionClient, QueryConfig
    
    # Just provide the base URL
    client = GenericAcquisitionClient(base_url="https://my-api.com/endpoint")
    
    config = QueryConfig(
        object_id="target",
        start_time="2025-01-01",
        stop_time="2025-01-31"
    )
    
    result = client.fetch_data(config)

Example (Advanced - Custom implementation):
    class MinorPlanetCenterClient(BaseAcquisitionClient):
        def fetch_data(self, query_config):
            # Implement MPC-specific logic with your own base_url
            url = self.build_url(query_config)
            response = self._rate_limited_request(url)
            return self.parser.parse_mpc_response(response)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union
from dataclasses import dataclass
import logging

from .utils import RateLimiter, ExponentialBackoff
from .cache import FileCache

logger = logging.getLogger(__name__)


class BaseAcquisitionClient(ABC):
    """Abstract base for astronomical data acquisition clients.
    
    Provides common functionality (rate limiting, caching, retries) that
    dataset-specific clients inherit. Each subclass implements data-source-specific
    logic: URL construction, request handling, and response parsing.
    
    Attributes:
        rate_limiter: RateLimiter instance for request throttling
        backoff: ExponentialBackoff instance for retry delays
        cache: FileCache instance for response caching
    """
    
    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        backoff: Optional[ExponentialBackoff] = None,
        cache: Optional[FileCache] = None,
        timeout_seconds: float = 30.0,
    ):
        """Initialize base client with optional rate limiting and caching.
        
        Args:
            rate_limiter: RateLimiter instance (default: no rate limiting)
            backoff: ExponentialBackoff instance (default: exponential backoff)
            cache: FileCache instance (default: no caching)
            timeout_seconds: HTTP request timeout
        """
        self.rate_limiter = rate_limiter
        self.backoff = backoff or ExponentialBackoff()
        self.cache = cache
        self.timeout_seconds = timeout_seconds
    
    @abstractmethod
    def fetch_data(self, query_config: Any) -> Any:
        """Fetch data from source using query configuration.
        
        This method must be implemented by subclasses. It should:
        1. Check cache if available
        2. Build data-source-specific request
        3. Enforce rate limiting
        4. Perform request with retry/backoff logic
        5. Cache response if applicable
        6. Return parsed data
        
        Args:
            query_config: Configuration object (e.g., HorizonsQueryConfig)
        
        Returns:
            Parsed response data (format depends on subclass)
        
        Raises:
            ConnectionError: If request fails after retries
            ValueError: If query config is invalid
        """
        pass
    
    def fetch_batch(self, configs: List[Any]) -> List[Any]:
        """Fetch data for multiple configurations (batch operation).
        
        Default implementation fetches sequentially. Subclasses can override for
        parallel/async execution.
        
        Args:
            configs: List of configuration objects
        
        Returns:
            List of results (one per config)
        """
        return [self.fetch_data(config) for config in configs]
    
    def _rate_limited_request(self, key: str, timeout: Optional[float] = None) -> bool:
        """Check if request is allowed under rate limits.
        
        Args:
            key: Rate limit key (e.g., 'horizons_api' or 'mpc')
            timeout: How long to wait if rate limited (seconds)
        
        Returns:
            True if request allowed; False if rate limited
        """
        if self.rate_limiter is None:
            return True
        
        if not self.rate_limiter.is_allowed(key):
            if timeout:
                retry_after = self.rate_limiter.get_retry_after(key)
                print(f"Rate limited. Retry after {retry_after:.1f}s")
            return False
        return True
    
    def _build_cache_key(self, query_config: Any) -> str:
        """Build deterministic cache key from query configuration.
        
        Subclasses should override to produce dataset-specific keys.
        
        Args:
            query_config: Configuration object
        
        Returns:
            Cache key string
        """
        return f"{self.__class__.__name__}_{str(query_config)}"
    
    def get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Retrieve data from cache if available.
        
        Args:
            cache_key: Cache key string
        
        Returns:
            Cached data or None if not found/expired
        """
        if self.cache is None:
            return None
        return self.cache.get(cache_key)
    
    def cache_data(self, cache_key: str, data: Any) -> None:
        """Store data in cache.
        
        Args:
            cache_key: Cache key string
            data: Data to cache
        """
        if self.cache is None:
            return
        self.cache.set(cache_key, data)


class BaseParser(ABC):
    """Abstract base for parsing astronomical data from various sources.
    
    Different data sources return different formats (JPL Horizons uses $$SOE/$$EOE
    markers; MPC uses CSV; GAIA returns JSON). Subclasses implement parsing for
    their specific format, returning standardized data structures.
    """
    
    @abstractmethod
    def parse(self, raw_response: Any) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Parse raw response from data source.
        
        Args:
            raw_response: Raw response from data source (string, JSON, etc.)
        
        Returns:
            Parsed data as dict (single record) or list of dicts (multiple records)
        """
        pass
    
    @staticmethod
    def _safe_float(value: str, default: Optional[float] = None) -> Optional[float]:
        """Safely convert string to float, handling missing/invalid values.
        
        Args:
            value: String value to convert
            default: Value to return if conversion fails
        
        Returns:
            Parsed float or default
        """
        if value is None or str(value).strip() in ("", "n/a", "N/A", "*"):
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def _safe_str(value: Any, default: str = "") -> str:
        """Safely convert value to string.
        
        Args:
            value: Value to convert
            default: Default string if value is None
        
        Returns:
            String representation
        """
        if value is None:
            return default
        return str(value).strip()


class GenericAcquisitionClient(BaseAcquisitionClient):
    """Simple generic client for any REST API without writing a custom class.
    
    Handles all boilerplate: caching, rate limiting, retries. Users just
    provide a base URL and the client builds requests from QueryConfig.
    
    Example:
        client = GenericAcquisitionClient(
            base_url="https://my-api.com/query",
            enforce_rate_limit=True,
            max_requests_per_minute=10
        )
        config = QueryConfig(object_id="target", start_time="2025-01-01", stop_time="2025-01-31")
        result = client.fetch_data(config)
    """
    
    def __init__(
        self,
        base_url: str,
        rate_limiter: Optional[RateLimiter] = None,
        backoff: Optional[ExponentialBackoff] = None,
        cache: Optional[FileCache] = None,
        timeout_seconds: float = 30.0,
        request_delay_seconds: float = 1.0,
        enforce_rate_limit: bool = True,
        max_requests_per_minute: int = 10,
        debug: bool = False,
        fallback_to_cache: bool = True,
        show_progress: bool = False,
    ):
        """Initialize generic client.
        
        Args:
            base_url: API endpoint URL
            rate_limiter: Custom RateLimiter (default: 10 req/min if enforce_rate_limit=True)
            backoff: Custom ExponentialBackoff
            cache: Custom FileCache
            timeout_seconds: HTTP request timeout
            request_delay_seconds: Minimum delay between requests
            enforce_rate_limit: Whether to enforce rate limiting
            max_requests_per_minute: Rate limit threshold
            debug: Enable debug logging
            fallback_to_cache: Use stale cache if request fails
            show_progress: Show progress bar for batch operations (requires tqdm)
        """
        import requests
        
        if rate_limiter is None and enforce_rate_limit:
            rate_limiter = RateLimiter(
                max_attempts=max_requests_per_minute,
                window_minutes=1
            )
        
        super().__init__(
            rate_limiter=rate_limiter,
            backoff=backoff,
            cache=cache,
            timeout_seconds=timeout_seconds,
        )
        
        self.base_url = base_url
        self.request_delay_seconds = request_delay_seconds
        self.last_request_time = 0.0
        self.debug = debug
        self.fallback_to_cache = fallback_to_cache
        self.show_progress = show_progress
        self._requests = requests
        
        # Request inspection attributes
        self.last_request_url = None
        self.last_request_params = None
        self.last_request_headers = None
        self.last_response_status = None
        self.last_response_time = None
        self.last_error = None
        
        # Debug logging
        if self.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug(f"GenericAcquisitionClient initialized with base_url={base_url}")
            logger.debug(f"Fallback to cache: {self.fallback_to_cache}")
    
    def _log_debug(self, message: str) -> None:
        """Log debug message if debug mode enabled."""
        if self.debug:
            logger.debug(message)
    
    def fetch_batch(self, configs: List[Any], show_progress: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Fetch data for multiple configurations (batch operation).
        
        Args:
            configs: List of QueryConfig instances
            show_progress: Override default show_progress setting (None = use default)
        
        Returns:
            List of result dicts (one per config, same structure as fetch_data)
        """
        import time
        
        self._log_debug(f"Starting batch operation with {len(configs)} configs")
        results = []
        
        # Determine if progress bar should be shown
        use_progress = show_progress if show_progress is not None else self.show_progress
        
        # Try to use tqdm for progress bar
        progress_bar = None
        if use_progress:
            try:
                from tqdm import tqdm
                progress_bar = tqdm(
                    total=len(configs),
                    desc="Fetching data",
                    unit="obj",
                    ncols=80,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
                )
            except ImportError:
                # tqdm not installed, use simple text progress
                self._log_debug("tqdm not installed, using simple progress")
                print(f"Progress: 0/{len(configs)}...", end="", flush=True)
        
        start_time = time.time()
        successes = 0
        
        for i, config in enumerate(configs):
            self._log_debug(f"Batch [{i+1}/{len(configs)}] Fetching {config.object_id}")
            result = self.fetch_data(config)
            results.append(result)
            
            if result.get('success'):
                successes += 1
            
            # Update progress
            if progress_bar is not None:
                progress_bar.update(1)
                progress_bar.set_postfix({"ok": successes, "fail": i + 1 - successes})
            elif use_progress and (i + 1) % max(1, len(configs) // 10) == 0:
                # Simple progress without tqdm (every 10%)
                pct = (i + 1) * 100 // len(configs)
                print(f"\rProgress: {i+1}/{len(configs)} ({pct}%)...", end="", flush=True)
        
        # Finish progress
        if progress_bar is not None:
            progress_bar.close()
        elif use_progress:
            elapsed = time.time() - start_time
            print(f"\rProgress: {len(configs)}/{len(configs)} (100%) - Done in {elapsed:.1f}s")
        
        self._log_debug(f"Batch operation complete. Successes: {successes}/{len(configs)}")
        return results
    
    def fetch_data(self, query_config: Any) -> Dict[str, Any]:
        """Fetch data from API using query configuration.
        
        Args:
            query_config: QueryConfig instance with object_id, start_time, stop_time, etc.
        
        Returns:
            Dict with keys: success, data, timestamp, (error if failed)
            If fallback_to_cache=True and request fails, returns cached data with from_cache=True
        """
        import time
        
        self._log_debug(f"Fetching data for object_id={query_config.object_id}")
        
        # Check cache
        cache_key = self._build_cache_key(query_config)
        cached = self.get_cached_data(cache_key)
        if cached is not None:
            self._log_debug(f"Cache hit for {query_config.object_id}")
            return cached
        
        self._log_debug(f"Cache miss for {query_config.object_id}, fetching from API")
        
        # Rate limiting
        if self.rate_limiter and not self.rate_limiter.is_allowed("generic_api"):
            self._log_debug("Rate limited")
            self.last_error = "Rate limited"
            return {
                "success": False,
                "error": "Rate limited"
            }
        
        # Enforce request delay
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.request_delay_seconds:
            time.sleep(self.request_delay_seconds - elapsed)
        self.last_request_time = time.time()
        
        # Build request with retry/backoff
        attempt = 0
        while attempt < 3:  # max 3 retries
            try:
                self._log_debug(f"Attempt {attempt + 1}: Requesting {self.base_url}")
                
                params = {
                    'object_id': query_config.object_id,
                    'start_time': query_config.start_time,
                    'stop_time': query_config.stop_time,
                    'step_size': query_config.step_size,
                }
                
                # Store request details for inspection
                self.last_request_url = self.base_url
                self.last_request_params = params
                request_start = time.time()
                
                response = self._requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout_seconds
                )
                
                # Store response details for inspection
                self.last_response_time = time.time() - request_start
                self.last_response_status = response.status_code
                self.last_error = None
                
                response.raise_for_status()
                
                self._log_debug(f"Request successful, status code: {response.status_code}, time: {self.last_response_time:.2f}s")
                
                result = {
                    "success": True,
                    "data": response.json() if response.headers.get('content-type') == 'application/json' else response.text,
                    "timestamp": time.time()
                }
                
                # Cache result
                self.cache_data(cache_key, result)
                self._log_debug(f"Data cached for {query_config.object_id}")
                return result
                
            except Exception as e:
                attempt += 1
                error_msg = str(e)
                self.last_error = error_msg
                self._log_debug(f"Attempt {attempt} failed: {error_msg}")
                
                if attempt < 3:
                    delay = self.backoff.get_delay(attempt)
                    self._log_debug(f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    self._log_debug(f"All {attempt} attempts failed. Checking fallback cache...")
                    
                    # Try fallback to cache if enabled
                    if self.fallback_to_cache and self.cache is not None:
                        try:
                            cached_fallback = self.get_cached_data(cache_key)
                            if cached_fallback is not None:
                                self._log_debug(f"Using stale cache as fallback for {query_config.object_id}")
                                return {
                                    **cached_fallback,
                                    "from_cache": True,
                                    "warning": "Using stale cached data (API unreachable)"
                                }
                        except Exception as cache_err:
                            self._log_debug(f"Fallback cache lookup failed: {cache_err}")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "timestamp": time.time()
                    }


class AsyncGenericAcquisitionClient(GenericAcquisitionClient):
    """Async version of GenericAcquisitionClient for concurrent requests.
    
    Inherits all functionality from GenericAcquisitionClient but provides
    async methods for concurrent data fetching. Rate limiting is maintained
    across parallel requests to respect API limits.
    
    Example (Fetch 100 objects in parallel):
        import asyncio
        from nexuscosmos import AsyncGenericAcquisitionClient, QueryConfig
        
        client = AsyncGenericAcquisitionClient(
            base_url="https://api.example.com/data",
            max_concurrent=10  # Max 10 parallel requests
        )
        
        configs = [
            QueryConfig(object_id=f"object_{i}", start_time="2025-01-01", stop_time="2025-01-31")
            for i in range(100)
        ]
        
        # Fetch all in parallel (3-10x faster than sequential)
        results = asyncio.run(client.fetch_data_async_batch(configs))
        # Results arrive as they complete, not in original order
        
        # Or keep order:
        results = asyncio.run(client.fetch_data_async_batch_ordered(configs))
    """
    
    def __init__(
        self,
        base_url: str,
        rate_limiter: Optional[RateLimiter] = None,
        backoff: Optional[ExponentialBackoff] = None,
        cache: Optional[FileCache] = None,
        timeout_seconds: float = 30.0,
        request_delay_seconds: float = 0.1,
        enforce_rate_limit: bool = True,
        max_requests_per_minute: int = 600,  # 10 req/sec for async
        debug: bool = False,
        fallback_to_cache: bool = True,
        max_concurrent: int = 5,  # Max parallel requests
    ):
        """Initialize async client.
        
        Args:
            base_url: API endpoint URL
            max_concurrent: Maximum concurrent requests (default: 5)
            Other args: See GenericAcquisitionClient
        """
        super().__init__(
            base_url=base_url,
            rate_limiter=rate_limiter,
            backoff=backoff,
            cache=cache,
            timeout_seconds=timeout_seconds,
            request_delay_seconds=request_delay_seconds,
            enforce_rate_limit=enforce_rate_limit,
            max_requests_per_minute=max_requests_per_minute,
            debug=debug,
            fallback_to_cache=fallback_to_cache,
        )
        self.max_concurrent = max_concurrent
        self._log_debug(f"AsyncGenericAcquisitionClient initialized with max_concurrent={max_concurrent}")
    
    async def fetch_data_async(self, query_config: Any) -> Dict[str, Any]:
        """Async version of fetch_data for concurrent requests.
        
        Args:
            query_config: QueryConfig instance
        
        Returns:
            Dict with same structure as fetch_data()
        """
        import asyncio
        import aiohttp
        import time
        
        self._log_debug(f"[ASYNC] Fetching data for object_id={query_config.object_id}")
        
        # Check cache
        cache_key = self._build_cache_key(query_config)
        cached = self.get_cached_data(cache_key)
        if cached is not None:
            self._log_debug(f"[ASYNC] Cache hit for {query_config.object_id}")
            return cached
        
        self._log_debug(f"[ASYNC] Cache miss for {query_config.object_id}")
        
        # Rate limiting check
        if self.rate_limiter and not self.rate_limiter.is_allowed("async_api"):
            self._log_debug("[ASYNC] Rate limited")
            self.last_error = "Rate limited"
            return {
                "success": False,
                "error": "Rate limited"
            }
        
        # Build request params
        params = {
            'object_id': query_config.object_id,
            'start_time': query_config.start_time,
            'stop_time': query_config.stop_time,
            'step_size': query_config.step_size,
        }
        
        attempt = 0
        while attempt < 3:
            try:
                self._log_debug(f"[ASYNC] Attempt {attempt + 1}: Requesting {self.base_url}")
                
                # Use aiohttp for async requests
                async with aiohttp.ClientSession() as session:
                    self.last_request_url = self.base_url
                    self.last_request_params = params
                    request_start = time.time()
                    
                    async with session.get(
                        self.base_url,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)
                    ) as response:
                        self.last_response_time = time.time() - request_start
                        self.last_response_status = response.status
                        self.last_error = None
                        
                        if response.status == 200:
                            self._log_debug(f"[ASYNC] Request successful, status: {response.status}, time: {self.last_response_time:.2f}s")
                            
                            content_type = response.headers.get('content-type', '')
                            if 'application/json' in content_type:
                                data = await response.json()
                            else:
                                data = await response.text()
                            
                            result = {
                                "success": True,
                                "data": data,
                                "timestamp": time.time()
                            }
                            
                            # Cache result
                            self.cache_data(cache_key, result)
                            self._log_debug(f"[ASYNC] Data cached for {query_config.object_id}")
                            return result
                        else:
                            raise Exception(f"HTTP {response.status}")
                        
            except Exception as e:
                attempt += 1
                error_msg = str(e)
                self.last_error = error_msg
                self._log_debug(f"[ASYNC] Attempt {attempt} failed: {error_msg}")
                
                if attempt < 3:
                    delay = self.backoff.get_delay(attempt)
                    self._log_debug(f"[ASYNC] Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    self._log_debug(f"[ASYNC] All {attempt} attempts failed. Checking fallback cache...")
                    
                    # Fallback to cache
                    if self.fallback_to_cache and self.cache is not None:
                        try:
                            cached_fallback = self.get_cached_data(cache_key)
                            if cached_fallback is not None:
                                self._log_debug(f"[ASYNC] Using stale cache as fallback for {query_config.object_id}")
                                return {
                                    **cached_fallback,
                                    "from_cache": True,
                                    "warning": "Using stale cached data (API unreachable)"
                                }
                        except Exception as cache_err:
                            self._log_debug(f"[ASYNC] Fallback cache lookup failed: {cache_err}")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "timestamp": time.time()
                    }
    
    async def fetch_data_async_batch(
        self,
        configs: List[Any],
        return_as_completed: bool = True,
        show_progress: Optional[bool] = None
    ) -> Union[List[Dict[str, Any]], List[tuple]]:
        """Fetch data for multiple configs concurrently.
        
        Args:
            configs: List of QueryConfig instances
            return_as_completed: If True, return results as they complete (list of dicts).
                                If False, return (config, result) tuples as completed.
            show_progress: Override default show_progress setting (None = use default)
        
        Returns:
            List of result dicts (if return_as_completed=True)
            List of (config, result) tuples (if return_as_completed=False)
        """
        import asyncio
        import time
        
        self._log_debug(f"[ASYNC] Starting async batch with {len(configs)} configs, max_concurrent={self.max_concurrent}")
        
        # Determine if progress bar should be shown
        use_progress = show_progress if show_progress is not None else self.show_progress
        
        # Set up progress tracking
        progress_bar = None
        completed_count = 0
        successes = 0
        start_time = time.time()
        
        if use_progress:
            try:
                from tqdm.asyncio import tqdm as async_tqdm
                progress_bar = async_tqdm(
                    total=len(configs),
                    desc="Fetching (async)",
                    unit="obj",
                    ncols=80,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
                )
            except ImportError:
                # tqdm not installed, use simple text progress
                self._log_debug("[ASYNC] tqdm not installed, using simple progress")
                print(f"[ASYNC] Progress: 0/{len(configs)}...", end="", flush=True)
        
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def fetch_with_semaphore(config, index):
            nonlocal completed_count, successes
            async with semaphore:
                result = await self.fetch_data_async(config)
                completed_count += 1
                
                if result.get('success'):
                    successes += 1
                
                # Update progress
                if progress_bar is not None:
                    progress_bar.update(1)
                    progress_bar.set_postfix({"ok": successes, "fail": completed_count - successes})
                elif use_progress and completed_count % max(1, len(configs) // 10) == 0:
                    pct = completed_count * 100 // len(configs)
                    print(f"\\r[ASYNC] Progress: {completed_count}/{len(configs)} ({pct}%)...", end="", flush=True)
                
                return result
        
        tasks = [fetch_with_semaphore(config, i) for i, config in enumerate(configs)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Finish progress
        if progress_bar is not None:
            progress_bar.close()
        elif use_progress:
            elapsed = time.time() - start_time
            print(f"\\r[ASYNC] Progress: {len(configs)}/{len(configs)} (100%) - Done in {elapsed:.1f}s")
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "timestamp": time.time()
                })
            else:
                processed_results.append(result)
        
        successes = sum(1 for r in processed_results if r.get('success'))
        self._log_debug(f"[ASYNC] Batch complete. Successes: {successes}/{len(configs)}")
        
        return processed_results
    
    async def fetch_data_async_batch_ordered(
        self,
        configs: List[Any],
        show_progress: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Fetch data for multiple configs concurrently, maintaining original order.
        
        Same as fetch_data_async_batch but guarantees results in original config order.
        
        Args:
            configs: List of QueryConfig instances
            show_progress: Override default show_progress setting (None = use default)
        
        Returns:
            List of result dicts in same order as input configs
        """
        results = await self.fetch_data_async_batch(configs, return_as_completed=False, show_progress=show_progress)
        
        # Results from gather() are already in order, just return them
        return results
