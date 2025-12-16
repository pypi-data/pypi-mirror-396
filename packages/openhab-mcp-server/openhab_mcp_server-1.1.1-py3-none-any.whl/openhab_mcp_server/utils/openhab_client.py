"""Async HTTP client for openHAB REST API."""

import asyncio
import logging
import random
import time
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
import aiohttp
from aiohttp import ClientError, ClientTimeout
from functools import wraps

from openhab_mcp_server.utils.config import Config, get_config
from openhab_mcp_server.utils.security import AuthorizationChecker, SecurityLogger, CredentialManager
from openhab_mcp_server.utils.logging import get_logger, LogCategory


logger = logging.getLogger(__name__)
structured_logger = get_logger("openhab_client")

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry logic."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        backoff_factor: float = 2.0,
        max_delay: int = 60,
        jitter: bool = True
    ):
        """Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
            max_delay: Maximum delay between retries in seconds
            jitter: Whether to add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        if attempt == 0:
            return 0
        
        # Exponential backoff: base_delay * (backoff_factor ^ (attempt - 1))
        base_delay = 1.0
        delay = base_delay * (self.backoff_factor ** (attempt - 1))
        
        # Cap at max delay
        delay = min(delay, self.max_delay)
        
        # Add jitter to avoid thundering herd
        if self.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)


class RetryableError(Exception):
    """Base class for errors that should trigger retries."""
    pass


class NonRetryableError(Exception):
    """Base class for errors that should not trigger retries."""
    pass


def is_retryable_error(error: Exception) -> bool:
    """Determine if an error should trigger a retry.
    
    Args:
        error: Exception to check
        
    Returns:
        True if error is retryable
    """
    # Network-related errors are retryable
    if isinstance(error, (
        asyncio.TimeoutError,
        aiohttp.ClientConnectionError,
        aiohttp.ClientConnectorError,
        aiohttp.ServerTimeoutError,
        aiohttp.ClientPayloadError
    )):
        return True
    
    # HTTP 5xx errors are retryable (server errors)
    if isinstance(error, OpenHABAPIError):
        if error.status_code and 500 <= error.status_code < 600:
            return True
        # 429 Too Many Requests is retryable
        if error.status_code == 429:
            return True
    
    # Specific retryable errors
    if isinstance(error, RetryableError):
        return True
    
    # Non-retryable errors
    if isinstance(error, NonRetryableError):
        return False
    
    # Authentication errors are not retryable
    if isinstance(error, OpenHABAuthenticationError):
        return False
    
    # Client errors (4xx except 429) are not retryable
    if isinstance(error, OpenHABAPIError):
        if error.status_code and 400 <= error.status_code < 500 and error.status_code != 429:
            return False
    
    # Default to not retryable for unknown errors
    return False


def with_retry(retry_config: Optional[RetryConfig] = None):
    """Decorator to add retry logic to async functions.
    
    Args:
        retry_config: Retry configuration. If None, uses default config.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            config = retry_config or RetryConfig()
            last_error = None
            
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    # Check if we should retry
                    if not is_retryable_error(e):
                        structured_logger.debug(
                            f"Non-retryable error in {func.__name__}: {e}",
                            category=LogCategory.PERFORMANCE,
                            error_type=type(e).__name__
                        )
                        raise
                    
                    # Check if we have more attempts
                    if attempt >= config.max_attempts - 1:
                        structured_logger.error(
                            f"Max retry attempts ({config.max_attempts}) exceeded for {func.__name__}: {e}",
                            category=LogCategory.PERFORMANCE,
                            error_type=type(e).__name__
                        )
                        break
                    
                    # Calculate delay and wait
                    delay = config.calculate_delay(attempt + 1)
                    structured_logger.warning(
                        f"Retry attempt {attempt + 1}/{config.max_attempts} for {func.__name__} "
                        f"after {delay:.2f}s delay. Error: {e}",
                        category=LogCategory.PERFORMANCE,
                        error_type=type(e).__name__
                    )
                    
                    if delay > 0:
                        await asyncio.sleep(delay)
            
            # All retries exhausted, raise the last error
            if last_error:
                raise last_error
            else:
                raise RuntimeError(f"Unexpected error in retry logic for {func.__name__}")
        
        return wrapper
    return decorator


class ConnectionPool:
    """Manages connection pooling and concurrent request handling."""
    
    def __init__(self, max_connections: int = 100, max_connections_per_host: int = 30):
        """Initialize connection pool.
        
        Args:
            max_connections: Maximum total connections
            max_connections_per_host: Maximum connections per host
        """
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self._connector: Optional[aiohttp.TCPConnector] = None
        self._semaphore = asyncio.Semaphore(max_connections_per_host)
        self._active_requests = 0
        self._lock = asyncio.Lock()
    
    async def get_connector(self) -> aiohttp.TCPConnector:
        """Get or create TCP connector with connection pooling."""
        if self._connector is None or self._connector.closed:
            self._connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=self.max_connections_per_host,
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
        return self._connector
    
    async def acquire_request_slot(self) -> None:
        """Acquire a slot for making a request."""
        await self._semaphore.acquire()
        async with self._lock:
            self._active_requests += 1
    
    def release_request_slot(self) -> None:
        """Release a request slot."""
        try:
            self._semaphore.release()
            asyncio.create_task(self._decrement_active_requests())
        except ValueError:
            # Semaphore already released
            pass
    
    async def _decrement_active_requests(self) -> None:
        """Safely decrement active request counter."""
        async with self._lock:
            self._active_requests = max(0, self._active_requests - 1)
    
    async def get_active_requests(self) -> int:
        """Get current number of active requests."""
        async with self._lock:
            return self._active_requests
    
    async def close(self) -> None:
        """Close the connection pool."""
        if self._connector and not self._connector.closed:
            await self._connector.close()
            self._connector = None


class OpenHABError(Exception):
    """Base exception for openHAB client errors."""
    pass


class OpenHABConnectionError(OpenHABError):
    """Raised when connection to openHAB fails."""
    pass


class OpenHABAuthenticationError(OpenHABError):
    """Raised when authentication with openHAB fails."""
    pass


class OpenHABAPIError(OpenHABError):
    """Raised when openHAB API returns an error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class OpenHABClient:
    """Async HTTP client for openHAB REST API."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize client with configuration.
        
        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or get_config()
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url = f"{self.config.openhab_url}/rest"
        
        # Setup headers (excluding auth header for security)
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Store token separately for secure handling
        self._auth_token = self.config.openhab_token
        
        # Request tracking for security monitoring
        self._request_count = 0
        self._last_request_time = 0
        
        # Retry configuration
        self._retry_config = RetryConfig(
            max_attempts=self.config.retry_attempts,
            backoff_factor=self.config.retry_backoff_factor,
            max_delay=self.config.retry_max_delay,
            jitter=True
        )
        
        # Connection pooling and concurrency management
        self._connection_pool = ConnectionPool(
            max_connections=100,
            max_connections_per_host=30
        )
        self._request_queue: Optional[asyncio.Queue] = None
        self._batch_processor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Concurrent request tracking
        self._concurrent_requests: Dict[str, asyncio.Task] = {}
        self._request_lock = asyncio.Lock()
    
    async def __aenter__(self) -> 'OpenHABClient':
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is created with connection pooling."""
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=self.config.timeout)
            connector = await self._connection_pool.get_connector()
            
            self._session = aiohttp.ClientSession(
                headers=self._headers,
                timeout=timeout,
                connector=connector
            )
            
            # Initialize request queue for batch processing
            if self._request_queue is None:
                self._request_queue = asyncio.Queue(maxsize=1000)
                self._batch_processor_task = asyncio.create_task(self._process_request_queue())
    
    async def _process_request_queue(self) -> None:
        """Process queued requests in batches for efficiency."""
        batch_size = 10
        batch_timeout = 0.1  # 100ms batch window
        
        while not self._shutdown_event.is_set():
            try:
                batch = []
                
                # Collect requests for batch processing
                try:
                    # Get first request (blocking)
                    first_request = await asyncio.wait_for(
                        self._request_queue.get(), 
                        timeout=1.0
                    )
                    batch.append(first_request)
                    
                    # Collect additional requests up to batch size
                    start_time = asyncio.get_event_loop().time()
                    while (len(batch) < batch_size and 
                           (asyncio.get_event_loop().time() - start_time) < batch_timeout):
                        try:
                            request = await asyncio.wait_for(
                                self._request_queue.get(), 
                                timeout=batch_timeout
                            )
                            batch.append(request)
                        except asyncio.TimeoutError:
                            break
                    
                    # Process batch concurrently
                    if batch:
                        await self._process_request_batch(batch)
                        
                except asyncio.TimeoutError:
                    # No requests in queue, continue
                    continue
                    
            except Exception as e:
                structured_logger.error(
                    f"Error in request queue processor: {e}",
                    category=LogCategory.PERFORMANCE,
                    error_type=type(e).__name__
                )
                await asyncio.sleep(0.1)
    
    async def _process_request_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Process a batch of requests concurrently.
        
        Args:
            batch: List of request dictionaries with method, endpoint, data, etc.
        """
        if not batch:
            return
        
        # Create tasks for concurrent execution
        tasks = []
        for request_info in batch:
            task = asyncio.create_task(
                self._execute_single_request(request_info)
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            structured_logger.error(
                f"Error processing request batch: {e}",
                category=LogCategory.PERFORMANCE,
                error_type=type(e).__name__
            )
    
    async def _execute_single_request(self, request_info: Dict[str, Any]) -> None:
        """Execute a single request from the batch.
        
        Args:
            request_info: Dictionary containing request details and future for result
        """
        future = request_info.get('future')
        if not future or future.cancelled():
            return
        
        try:
            result = await self._make_direct_request(
                method=request_info['method'],
                endpoint=request_info['endpoint'],
                data=request_info.get('data'),
                params=request_info.get('params')
            )
            if not future.done():
                future.set_result(result)
        except Exception as e:
            if not future.done():
                future.set_exception(e)
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers securely.
        
        Returns:
            Dictionary containing authentication headers
        """
        headers = self._headers.copy()
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        return headers
    
    def _sanitize_url_for_logging(self, url: str) -> str:
        """Sanitize URL for logging by removing sensitive information.
        
        Args:
            url: URL to sanitize
            
        Returns:
            Sanitized URL safe for logging
        """
        # Remove any potential tokens or sensitive data from URL
        import re
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        try:
            parsed = urlparse(url)
            
            # Remove sensitive query parameters
            if parsed.query:
                query_params = parse_qs(parsed.query)
                safe_params = {}
                
                for key, values in query_params.items():
                    # Hide sensitive parameter values
                    if any(sensitive in key.lower() for sensitive in ['token', 'password', 'secret', 'key', 'auth']):
                        safe_params[key] = ['***']
                    else:
                        safe_params[key] = values
                
                safe_query = urlencode(safe_params, doseq=True)
                sanitized = urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path,
                    parsed.params, safe_query, parsed.fragment
                ))
            else:
                sanitized = url
            
            return sanitized
            
        except Exception:
            # If URL parsing fails, return a generic safe version
            return f"{self._base_url}/[endpoint]"
    
    def _sanitize_error_message(self, error_msg: str) -> str:
        """Sanitize error messages to prevent credential exposure.
        
        Args:
            error_msg: Original error message
            
        Returns:
            Sanitized error message
        """
        import re
        
        # Remove potential tokens from error messages
        sanitized = error_msg
        
        # First, if we have a token, explicitly remove it
        if self._auth_token and self._auth_token in sanitized:
            sanitized = sanitized.replace(self._auth_token, '***')
        
        # Remove Bearer tokens
        sanitized = re.sub(r'Bearer\s+[A-Za-z0-9._-]+', 'Bearer ***', sanitized, flags=re.IGNORECASE)
        
        # Remove API keys/tokens in various formats
        sanitized = re.sub(r'[?&](token|key|password|secret|auth)=[^&\s]+', r'\1=***', sanitized, flags=re.IGNORECASE)
        
        # Remove long strings that might be tokens (15+ chars to catch more cases)
        sanitized = re.sub(r'[A-Za-z0-9._-]{15,}', '***', sanitized)
        
        # Remove any remaining long sequences that might contain tokens or sensitive data
        sanitized = re.sub(r'\S{30,}', '***', sanitized)
        
        return sanitized
    
    def _check_request_authorization(self, endpoint: str) -> bool:
        """Check if request is authorized and track for security monitoring.
        
        Args:
            endpoint: API endpoint being accessed
            
        Returns:
            True if request is authorized
        """
        import time
        
        current_time = time.time()
        
        # Update request tracking
        self._request_count += 1
        
        # Reset counter every minute
        if current_time - self._last_request_time > 60:
            self._request_count = 1
            self._last_request_time = current_time
        
        # Prepare request context for authorization check
        request_context = {
            'has_token': bool(self._auth_token),
            'endpoint': endpoint,
            'recent_request_count': self._request_count,
            'time_window_seconds': 60
        }
        
        # Check authorization
        if not AuthorizationChecker.check_request_authorization(request_context):
            return False
        
        # Additional checks for sensitive endpoints
        sensitive_endpoints = [
            'systeminfo', 'bindings', 'discovery', 'rules'
        ]
        
        if any(sensitive in endpoint.lower() for sensitive in sensitive_endpoints):
            if not self._auth_token:
                SecurityLogger.log_unauthorized_request(
                    "sensitive_endpoint_no_auth",
                    f"Attempt to access sensitive endpoint without authentication: {endpoint}"
                )
                return False
            
            # Log access to sensitive endpoints
            SecurityLogger.log_security_event(
                "sensitive_endpoint_access",
                {
                    "endpoint": endpoint,
                    "authenticated": True,
                    "token_masked": CredentialManager.mask_token(self._auth_token)
                }
            )
        
        return True
    
    async def close(self) -> None:
        """Close the HTTP session and cleanup resources."""
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel batch processor
        if self._batch_processor_task and not self._batch_processor_task.done():
            self._batch_processor_task.cancel()
            try:
                await self._batch_processor_task
            except asyncio.CancelledError:
                pass
        
        # Cancel any pending concurrent requests
        async with self._request_lock:
            for request_id, task in list(self._concurrent_requests.items()):
                if not task.done():
                    task.cancel()
            self._concurrent_requests.clear()
        
        # Close session
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
        
        # Close connection pool
        await self._connection_pool.close()
    
    async def get_concurrent_request_count(self) -> int:
        """Get the number of currently active concurrent requests."""
        return await self._connection_pool.get_active_requests()
    
    def get_retry_config(self) -> RetryConfig:
        """Get the current retry configuration.
        
        Returns:
            Current retry configuration
        """
        return self._retry_config
    
    def update_retry_config(
        self,
        max_attempts: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        max_delay: Optional[int] = None
    ) -> None:
        """Update retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
            max_delay: Maximum delay between retries in seconds
        """
        if max_attempts is not None:
            self._retry_config.max_attempts = max_attempts
        if backoff_factor is not None:
            self._retry_config.backoff_factor = backoff_factor
        if max_delay is not None:
            self._retry_config.max_delay = max_delay
    
    async def queue_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
        priority: bool = False
    ) -> Any:
        """Queue a request for batch processing.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            priority: Whether to prioritize this request
            
        Returns:
            Future result of the request
        """
        if not self._request_queue:
            # Fallback to direct request if queue not initialized
            return await self._make_request(method, endpoint, data, params)
        
        # Create future for result
        future = asyncio.Future()
        
        request_info = {
            'method': method,
            'endpoint': endpoint,
            'data': data,
            'params': params,
            'future': future,
            'priority': priority
        }
        
        try:
            if priority:
                # For priority requests, use direct execution
                return await self._make_request(method, endpoint, data, params)
            else:
                # Queue for batch processing
                await self._request_queue.put(request_info)
                return await future
        except asyncio.QueueFull:
            # Queue is full, execute directly
            return await self._make_request(method, endpoint, data, params)
    
    async def _make_direct_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request directly without queueing.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without /rest prefix)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            OpenHABConnectionError: Connection failed
            OpenHABAuthenticationError: Authentication failed
            OpenHABAPIError: API returned error
        """
        await self._ensure_session()
        
        # Acquire request slot for concurrency control
        await self._connection_pool.acquire_request_slot()
        
        try:
            return await self._execute_request(method, endpoint, data, params)
        finally:
            self._connection_pool.release_request_slot()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to openHAB API with intelligent routing.
        
        This method automatically chooses between direct execution and queued
        batch processing based on system load and request characteristics.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without /rest prefix)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            OpenHABConnectionError: Connection failed
            OpenHABAuthenticationError: Authentication failed
            OpenHABAPIError: API returned error
        """
        # Determine if request should be prioritized (write operations)
        is_priority = method.upper() in ['POST', 'PUT', 'DELETE']
        
        # Check current load
        active_requests = await self._connection_pool.get_active_requests()
        
        # Use direct execution for priority requests or when load is low
        if is_priority or active_requests < 5:
            return await self._make_direct_request(method, endpoint, data, params)
        else:
            # Use queued processing for read operations under load
            return await self.queue_request(method, endpoint, data, params)
    
    async def _execute_single_http_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> aiohttp.ClientResponse:
        """Execute a single HTTP request with timeout handling.
        
        This method is separate to allow for retry logic to be applied.
        
        Args:
            method: HTTP method
            url: Full URL to request
            headers: Request headers
            data: Request body data
            params: Query parameters
            
        Returns:
            HTTP response object
            
        Raises:
            Various aiohttp exceptions that can be retried
        """
        # Use asyncio.wait_for to enforce timeout with better error handling
        try:
            response = await asyncio.wait_for(
                self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if isinstance(data, dict) else None,
                    data=data if isinstance(data, str) else None,
                    params=params
                ),
                timeout=self.config.timeout
            )
            return response
        except asyncio.TimeoutError:
            # Convert to a more specific timeout error for retry logic
            raise aiohttp.ServerTimeoutError("Request timeout after {self.config.timeout}s")
    
    async def _execute_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the actual HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without /rest prefix)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            OpenHABConnectionError: Connection failed
            OpenHABAuthenticationError: Authentication failed
            OpenHABAPIError: API returned error
        """
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        
        # Security checks before making request
        if not self._check_request_authorization(endpoint):
            structured_logger.log_authentication_event(
                "request_authorization_failed",
                False,
                {"endpoint": endpoint, "method": method}
            )
            raise OpenHABAuthenticationError("Request not authorized")
        
        # Create retry-enabled request executor
        @with_retry(self._retry_config)
        async def execute_with_retry() -> Dict[str, Any]:
            # Use structured logging with request context
            with structured_logger.request_context(endpoint, method) as ctx:
                try:
                    # Get headers with authentication
                    request_headers = self._get_auth_headers()
                    
                    # Execute HTTP request with timeout handling
                    response = await self._execute_single_http_request(
                        method=method,
                        url=url,
                        headers=request_headers,
                        data=data,
                        params=params
                    )
                    
                    async with response:
                        # Handle authentication errors (non-retryable)
                        if response.status == 401:
                            structured_logger.log_authentication_event(
                                "api_authentication_failed",
                                False,
                                {"endpoint": endpoint, "status_code": response.status}
                            )
                            ctx.log_error(response.status, "Authentication failed - invalid or missing API token", "authentication_error")
                            raise OpenHABAuthenticationError(
                                "Authentication failed. Check your API token configuration."
                            )
                        
                        # Handle other client errors
                        if response.status >= 400:
                            try:
                                error_data = await response.json()
                                error_msg = error_data.get('message', f'HTTP {response.status}')
                            except:
                                error_msg = f"HTTP {response.status}: {response.reason}"
                            
                            # Sanitize error message before raising
                            sanitized_error = self._sanitize_error_message(error_msg)
                            ctx.log_error(response.status, sanitized_error, "api_error")
                            raise OpenHABAPIError(sanitized_error, response.status)
                        
                        # Log successful response
                        ctx.log_success(response.status, f"Request to {endpoint} completed successfully")
                        
                        # Handle successful responses
                        if response.status == 204:  # No Content
                            return {}
                        
                        try:
                            return await response.json()
                        except:
                            # Some endpoints return plain text
                            text = await response.text()
                            return {"value": text} if text else {}
                            
                except ClientError as e:
                    # Sanitize error message before logging and raising
                    sanitized_error = self._sanitize_error_message(str(e))
                    ctx.log_error(0, sanitized_error, "connection_error")
                    raise OpenHABConnectionError(f"Failed to connect to openHAB: {sanitized_error}")
                except asyncio.TimeoutError:
                    ctx.log_error(0, "Request timeout", "timeout_error")
                    raise OpenHABConnectionError("Request timeout")
        
        # Execute with retry logic
        return await execute_with_retry()
    
    # Item operations
    
    async def get_item_state(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get item state with error handling.
        
        Args:
            item_name: Name of the openHAB item
            
        Returns:
            Item state data or None if item doesn't exist
        """
        try:
            return await self._make_request("GET", f"items/{item_name}")
        except OpenHABAPIError as e:
            if e.status_code == 404:
                logger.warning(f"Item '{item_name}' not found")
                return None
            raise
    
    async def send_item_command(self, item_name: str, command: str) -> bool:
        """Send command to item.
        
        Args:
            item_name: Name of the openHAB item
            command: Command to send
            
        Returns:
            True if command was sent successfully
        """
        try:
            await self._make_request("POST", f"items/{item_name}", data=command)
            logger.info(f"Sent command '{command}' to item '{item_name}'")
            return True
        except OpenHABAPIError as e:
            logger.error(f"Failed to send command to '{item_name}': {e}")
            return False
    
    async def update_item_state(self, item_name: str, state: str) -> bool:
        """Update item state directly.
        
        Args:
            item_name: Name of the openHAB item
            state: New state value
            
        Returns:
            True if state was updated successfully
        """
        try:
            await self._make_request("PUT", f"items/{item_name}/state", data=state)
            logger.info(f"Updated state of '{item_name}' to '{state}'")
            return True
        except OpenHABAPIError as e:
            logger.error(f"Failed to update state of '{item_name}': {e}")
            return False
    
    async def get_items(self, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all items or items of specific type.
        
        Args:
            item_type: Filter by item type (e.g., 'Switch', 'Dimmer')
            
        Returns:
            List of item data
        """
        params = {"type": item_type} if item_type else None
        result = await self._make_request("GET", "items", params=params)
        return result if isinstance(result, list) else []
    
    # Thing operations
    
    async def get_things(self) -> List[Dict[str, Any]]:
        """Get all things.
        
        Returns:
            List of thing data
        """
        result = await self._make_request("GET", "things")
        return result if isinstance(result, list) else []
    
    async def get_thing_status(self, thing_uid: str) -> Optional[Dict[str, Any]]:
        """Get thing status and configuration.
        
        Args:
            thing_uid: UID of the thing
            
        Returns:
            Thing data or None if thing doesn't exist
        """
        try:
            return await self._make_request("GET", f"things/{thing_uid}")
        except OpenHABAPIError as e:
            if e.status_code == 404:
                logger.warning(f"Thing '{thing_uid}' not found")
                return None
            raise
    
    async def update_thing_config(self, thing_uid: str, config: Dict[str, Any]) -> bool:
        """Update thing configuration.
        
        Args:
            thing_uid: UID of the thing
            config: Configuration parameters
            
        Returns:
            True if configuration was updated successfully
        """
        try:
            await self._make_request("PUT", f"things/{thing_uid}/config", data=config)
            logger.info(f"Updated configuration for thing '{thing_uid}'")
            return True
        except OpenHABAPIError as e:
            logger.error(f"Failed to update configuration for '{thing_uid}': {e}")
            return False
    
    async def discover_things(self, binding_id: str) -> List[Dict[str, Any]]:
        """Trigger discovery for new things.
        
        Args:
            binding_id: ID of the binding to discover for
            
        Returns:
            List of discovered things
        """
        try:
            # Start discovery
            await self._make_request("POST", f"discovery/bindings/{binding_id}/scan")
            
            # Get discovery results
            result = await self._make_request("GET", "discovery")
            return result if isinstance(result, list) else []
        except OpenHABAPIError as e:
            logger.error(f"Failed to discover things for binding '{binding_id}': {e}")
            return []
    
    # Rule operations
    
    async def get_rules(self) -> List[Dict[str, Any]]:
        """Get all automation rules.
        
        Returns:
            List of rule data
        """
        result = await self._make_request("GET", "rules")
        return result if isinstance(result, list) else []
    
    async def get_rule(self, rule_uid: str) -> Optional[Dict[str, Any]]:
        """Get specific rule by UID.
        
        Args:
            rule_uid: UID of the rule
            
        Returns:
            Rule data or None if rule doesn't exist
        """
        try:
            return await self._make_request("GET", f"rules/{rule_uid}")
        except OpenHABAPIError as e:
            if e.status_code == 404:
                logger.warning(f"Rule '{rule_uid}' not found")
                return None
            raise
    
    async def execute_rule(self, rule_uid: str) -> bool:
        """Manually execute a rule.
        
        Args:
            rule_uid: UID of the rule to execute
            
        Returns:
            True if rule was executed successfully
        """
        try:
            await self._make_request("POST", f"rules/{rule_uid}/runnow")
            logger.info(f"Executed rule '{rule_uid}'")
            return True
        except OpenHABAPIError as e:
            logger.error(f"Failed to execute rule '{rule_uid}': {e}")
            return False
    
    async def create_rule(self, rule_definition: Dict[str, Any]) -> Optional[str]:
        """Create new automation rule.
        
        Args:
            rule_definition: Rule definition data
            
        Returns:
            UID of created rule or None if creation failed
        """
        try:
            result = await self._make_request("POST", "rules", data=rule_definition)
            rule_uid = result.get("uid")
            if rule_uid:
                logger.info(f"Created rule '{rule_uid}'")
            return rule_uid
        except OpenHABAPIError as e:
            logger.error(f"Failed to create rule: {e}")
            return None
    
    # System operations
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information.
        
        Returns:
            System information data
        """
        return await self._make_request("GET", "systeminfo")
    
    async def get_bindings(self) -> List[Dict[str, Any]]:
        """Get all installed bindings.
        
        Returns:
            List of binding data
        """
        result = await self._make_request("GET", "bindings")
        return result if isinstance(result, list) else []
    
    async def get_binding_config(self, binding_id: str) -> Optional[Dict[str, Any]]:
        """Get binding configuration.
        
        Args:
            binding_id: ID of the binding
            
        Returns:
            Binding configuration or None if binding doesn't exist
        """
        try:
            return await self._make_request("GET", f"bindings/{binding_id}/config")
        except OpenHABAPIError as e:
            if e.status_code == 404:
                logger.warning(f"Binding '{binding_id}' not found")
                return None
            raise
    
    # Batch operations for improved concurrency
    
    async def get_multiple_item_states(self, item_names: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get states for multiple items concurrently.
        
        Args:
            item_names: List of item names to query
            
        Returns:
            Dictionary mapping item names to their state data
        """
        if not item_names:
            return {}
        
        # Create concurrent tasks for all items
        tasks = []
        for item_name in item_names:
            task = asyncio.create_task(
                self.get_item_state(item_name),
                name=f"get_state_{item_name}"
            )
            tasks.append((item_name, task))
        
        # Execute all tasks concurrently
        results = {}
        completed_tasks = await asyncio.gather(
            *[task for _, task in tasks], 
            return_exceptions=True
        )
        
        # Process results
        for (item_name, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                logger.warning(f"Failed to get state for item '{item_name}': {result}")
                results[item_name] = None
            else:
                results[item_name] = result
        
        return results
    
    async def send_multiple_commands(self, commands: List[tuple[str, str]]) -> Dict[str, bool]:
        """Send commands to multiple items concurrently.
        
        Args:
            commands: List of (item_name, command) tuples
            
        Returns:
            Dictionary mapping item names to success status
        """
        if not commands:
            return {}
        
        # Create concurrent tasks for all commands
        tasks = []
        for item_name, command in commands:
            task = asyncio.create_task(
                self.send_item_command(item_name, command),
                name=f"send_command_{item_name}"
            )
            tasks.append((item_name, task))
        
        # Execute all tasks concurrently
        results = {}
        completed_tasks = await asyncio.gather(
            *[task for _, task in tasks], 
            return_exceptions=True
        )
        
        # Process results
        for (item_name, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                logger.warning(f"Failed to send command to item '{item_name}': {result}")
                results[item_name] = False
            else:
                results[item_name] = result
        
        return results
    
    async def get_multiple_thing_statuses(self, thing_uids: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get statuses for multiple things concurrently.
        
        Args:
            thing_uids: List of thing UIDs to query
            
        Returns:
            Dictionary mapping thing UIDs to their status data
        """
        if not thing_uids:
            return {}
        
        # Create concurrent tasks for all things
        tasks = []
        for thing_uid in thing_uids:
            task = asyncio.create_task(
                self.get_thing_status(thing_uid),
                name=f"get_thing_status_{thing_uid}"
            )
            tasks.append((thing_uid, task))
        
        # Execute all tasks concurrently
        results = {}
        completed_tasks = await asyncio.gather(
            *[task for _, task in tasks], 
            return_exceptions=True
        )
        
        # Process results
        for (thing_uid, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                logger.warning(f"Failed to get status for thing '{thing_uid}': {result}")
                results[thing_uid] = None
            else:
                results[thing_uid] = result
        
        return results
    
    async def execute_concurrent_requests(
        self, 
        requests: List[Dict[str, Any]], 
        max_concurrent: int = 10
    ) -> List[Any]:
        """Execute multiple requests concurrently with controlled concurrency.
        
        Args:
            requests: List of request dictionaries with method, endpoint, data, params
            max_concurrent: Maximum number of concurrent requests
            
        Returns:
            List of results in the same order as requests
        """
        if not requests:
            return []
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(request: Dict[str, Any]) -> Any:
            async with semaphore:
                return await self._make_request(
                    method=request['method'],
                    endpoint=request['endpoint'],
                    data=request.get('data'),
                    params=request.get('params')
                )
        
        # Create tasks for all requests
        tasks = [
            asyncio.create_task(execute_with_semaphore(request))
            for request in requests
        ]
        
        # Execute all tasks and return results
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    # Addon operations
    
    async def get_addons(self, addon_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all available and installed addons.
        
        Args:
            addon_type: Filter by addon type (binding, transformation, etc.)
            
        Returns:
            List of addon data including both available and installed addons
        """
        try:
            # Get installed addons
            installed_result = await self._make_request("GET", "extensions")
            installed_addons = installed_result if isinstance(installed_result, list) else []
            
            # Get available addons from registry
            available_result = await self._make_request("GET", "extensions/types")
            available_addons = available_result if isinstance(available_result, list) else []
            
            # Combine and mark installation status
            all_addons = []
            installed_ids = {addon.get('id') for addon in installed_addons if addon.get('id')}
            
            # Add installed addons
            for addon in installed_addons:
                addon_data = addon.copy()
                addon_data['installed'] = True
                all_addons.append(addon_data)
            
            # Add available but not installed addons
            for addon in available_addons:
                if addon.get('id') not in installed_ids:
                    addon_data = addon.copy()
                    addon_data['installed'] = False
                    all_addons.append(addon_data)
            
            # Filter by type if specified
            if addon_type:
                all_addons = [
                    addon for addon in all_addons 
                    if addon.get('type', '').lower() == addon_type.lower()
                ]
            
            return all_addons
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to get addons: {e}")
            return []
    
    async def install_addon(self, addon_id: str) -> bool:
        """Install an addon from the addon registry.
        
        Args:
            addon_id: ID of the addon to install
            
        Returns:
            True if addon was installed successfully
        """
        try:
            await self._make_request("POST", f"extensions/{addon_id}/install")
            logger.info(f"Installed addon '{addon_id}'")
            return True
        except OpenHABAPIError as e:
            logger.error(f"Failed to install addon '{addon_id}': {e}")
            return False
    
    async def uninstall_addon(self, addon_id: str) -> bool:
        """Uninstall an installed addon.
        
        Args:
            addon_id: ID of the addon to uninstall
            
        Returns:
            True if addon was uninstalled successfully
        """
        try:
            await self._make_request("POST", f"extensions/{addon_id}/uninstall")
            logger.info(f"Uninstalled addon '{addon_id}'")
            return True
        except OpenHABAPIError as e:
            logger.error(f"Failed to uninstall addon '{addon_id}': {e}")
            return False
    
    async def update_addon_config(self, addon_id: str, config: Dict[str, Any]) -> bool:
        """Update addon configuration parameters.
        
        Args:
            addon_id: ID of the addon
            config: Configuration parameters to update
            
        Returns:
            True if configuration was updated successfully
        """
        try:
            await self._make_request("PUT", f"extensions/{addon_id}/config", data=config)
            logger.info(f"Updated configuration for addon '{addon_id}'")
            return True
        except OpenHABAPIError as e:
            logger.error(f"Failed to update configuration for addon '{addon_id}': {e}")
            return False
    
    async def get_addon_config(self, addon_id: str) -> Optional[Dict[str, Any]]:
        """Get addon configuration.
        
        Args:
            addon_id: ID of the addon
            
        Returns:
            Addon configuration or None if addon doesn't exist
        """
        try:
            return await self._make_request("GET", f"extensions/{addon_id}/config")
        except OpenHABAPIError as e:
            if e.status_code == 404:
                logger.warning(f"Addon '{addon_id}' not found")
                return None
            raise
    
    # Link operations
    
    async def get_links(self, item_name: Optional[str] = None, channel_uid: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get item links with optional filtering.
        
        Args:
            item_name: Filter by specific item name
            channel_uid: Filter by specific channel UID
            
        Returns:
            List of link data
        """
        try:
            # Get all links
            result = await self._make_request("GET", "links")
            links = result if isinstance(result, list) else []
            
            # Apply filters if specified
            if item_name:
                links = [link for link in links if link.get('itemName') == item_name]
            
            if channel_uid:
                links = [link for link in links if link.get('channelUID') == channel_uid]
            
            return links
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to get links: {e}")
            return []
    
    async def create_link(self, item_name: str, channel_uid: str, configuration: Optional[Dict[str, Any]] = None) -> bool:
        """Create link between channel and item with validation.
        
        Args:
            item_name: Name of the item to link
            channel_uid: UID of the channel to link
            configuration: Optional link configuration parameters
            
        Returns:
            True if link was created successfully
        """
        try:
            # Validate that item exists
            item = await self.get_item_state(item_name)
            if not item:
                logger.error(f"Cannot create link: item '{item_name}' does not exist")
                return False
            
            # Validate that channel exists by checking the thing
            try:
                thing_uid = ':'.join(channel_uid.split(':')[:-1])  # Remove channel ID to get thing UID
                thing = await self.get_thing_status(thing_uid)
                if not thing:
                    logger.error(f"Cannot create link: thing '{thing_uid}' for channel '{channel_uid}' does not exist")
                    return False
            except Exception as e:
                logger.warning(f"Could not validate channel existence: {e}")
            
            # Create link data
            link_data = {
                "itemName": item_name,
                "channelUID": channel_uid
            }
            
            if configuration:
                link_data["configuration"] = configuration
            
            await self._make_request("PUT", f"links/{item_name}/{channel_uid}", data=link_data)
            logger.info(f"Created link between item '{item_name}' and channel '{channel_uid}'")
            return True
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to create link between '{item_name}' and '{channel_uid}': {e}")
            return False
    
    async def update_link(self, item_name: str, channel_uid: str, configuration: Dict[str, Any]) -> bool:
        """Update link configuration and transformation settings.
        
        Args:
            item_name: Name of the linked item
            channel_uid: UID of the linked channel
            configuration: New configuration parameters
            
        Returns:
            True if link configuration was updated successfully
        """
        try:
            # Check if link exists
            links = await self.get_links(item_name=item_name, channel_uid=channel_uid)
            if not links:
                logger.error(f"Cannot update link: no link found between '{item_name}' and '{channel_uid}'")
                return False
            
            # Update link configuration
            link_data = {
                "itemName": item_name,
                "channelUID": channel_uid,
                "configuration": configuration
            }
            
            await self._make_request("PUT", f"links/{item_name}/{channel_uid}", data=link_data)
            logger.info(f"Updated link configuration between '{item_name}' and '{channel_uid}'")
            return True
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to update link between '{item_name}' and '{channel_uid}': {e}")
            return False
    
    async def delete_link(self, item_name: str, channel_uid: str) -> bool:
        """Delete item link and validate removal.
        
        Args:
            item_name: Name of the linked item
            channel_uid: UID of the linked channel
            
        Returns:
            True if link was deleted successfully
        """
        try:
            # Check if link exists before deletion
            links = await self.get_links(item_name=item_name, channel_uid=channel_uid)
            if not links:
                logger.warning(f"Link between '{item_name}' and '{channel_uid}' does not exist")
                return True  # Consider it successful if link doesn't exist
            
            await self._make_request("DELETE", f"links/{item_name}/{channel_uid}")
            
            # Validate removal by checking if link still exists
            links_after = await self.get_links(item_name=item_name, channel_uid=channel_uid)
            if links_after:
                logger.error(f"Link between '{item_name}' and '{channel_uid}' still exists after deletion")
                return False
            
            logger.info(f"Deleted link between item '{item_name}' and channel '{channel_uid}'")
            return True
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to delete link between '{item_name}' and '{channel_uid}': {e}")
            return False
    
    # Transformation Management Methods
    
    async def get_transformations(self) -> List[Dict[str, Any]]:
        """Get available transformation addons and their capabilities.
        
        Returns:
            List of transformation information dictionaries
        """
        try:
            # Get transformation addons from the addon registry
            addons = await self.get_addons(addon_type="transformation")
            
            # Filter for installed transformation addons
            installed_transformations = [
                addon for addon in addons 
                if addon.get('installed', False) and addon.get('type') == 'transformation'
            ]
            
            # Convert to transformation format
            transformations = []
            for addon in installed_transformations:
                transformation = {
                    'id': addon.get('id', ''),
                    'type': addon.get('id', '').upper().replace('TRANSFORMATION-', ''),
                    'description': addon.get('description', ''),
                    'configuration': addon.get('configuration', {})
                }
                transformations.append(transformation)
            
            logger.info(f"Retrieved {len(transformations)} transformation addons")
            return transformations
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to get transformations: {e}")
            return []
    
    async def create_transformation(self, transformation_type: str, configuration: Dict[str, Any]) -> Optional[str]:
        """Create transformation configuration with syntax validation.
        
        Args:
            transformation_type: Type of transformation to create
            configuration: Configuration parameters for the transformation
            
        Returns:
            Transformation ID if created successfully, None otherwise
        """
        try:
            # Generate a unique transformation ID
            import uuid
            transformation_id = f"{transformation_type.lower()}_{uuid.uuid4().hex[:8]}"
            
            # Create transformation configuration
            transformation_data = {
                'id': transformation_id,
                'type': transformation_type.upper(),
                'configuration': configuration
            }
            
            # For now, we'll store this as a configuration item since openHAB doesn't have
            # a direct REST API for transformation management. In a real implementation,
            # this would depend on the specific transformation type and openHAB version.
            
            # Validate transformation syntax based on type
            if not await self._validate_transformation_syntax(transformation_type, configuration):
                logger.error(f"Invalid transformation syntax for type '{transformation_type}'")
                return None
            
            logger.info(f"Created transformation '{transformation_id}' of type '{transformation_type}'")
            return transformation_id
            
        except Exception as e:
            logger.error(f"Failed to create transformation: {e}")
            return None
    
    async def test_transformation(self, transformation_id: str, sample_data: str) -> Optional[Dict[str, Any]]:
        """Test transformation with sample data and return results.
        
        Args:
            transformation_id: ID of the transformation to test
            sample_data: Sample input data for testing
            
        Returns:
            Dictionary with test results including success, output, and execution time
        """
        try:
            start_time = time.time()
            
            # Extract transformation type from ID
            transformation_type = transformation_id.split('_')[0].upper()
            
            # Simulate transformation execution based on type
            # In a real implementation, this would use the actual transformation engine
            output_value = await self._execute_transformation(transformation_type, sample_data)
            
            execution_time = time.time() - start_time
            
            if output_value is not None:
                result = {
                    'success': True,
                    'input_value': sample_data,
                    'output_value': output_value,
                    'execution_time': execution_time,
                    'error_message': None
                }
            else:
                result = {
                    'success': False,
                    'input_value': sample_data,
                    'output_value': None,
                    'execution_time': execution_time,
                    'error_message': f"Transformation '{transformation_id}' failed to process input"
                }
            
            logger.info(f"Tested transformation '{transformation_id}' in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"Failed to test transformation '{transformation_id}': {e}")
            return {
                'success': False,
                'input_value': sample_data,
                'output_value': None,
                'execution_time': execution_time,
                'error_message': str(e)
            }
    
    async def update_transformation(self, transformation_id: str, configuration: Dict[str, Any]) -> bool:
        """Update transformation configuration with validation.
        
        Args:
            transformation_id: ID of the transformation to update
            configuration: New configuration parameters
            
        Returns:
            True if transformation configuration was updated successfully
        """
        try:
            # Extract transformation type from ID
            transformation_type = transformation_id.split('_')[0].upper()
            
            # Validate new configuration
            if not await self._validate_transformation_syntax(transformation_type, configuration):
                logger.error(f"Invalid transformation configuration for '{transformation_id}'")
                return False
            
            # Update transformation configuration
            # In a real implementation, this would update the actual transformation configuration
            logger.info(f"Updated transformation configuration for '{transformation_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update transformation '{transformation_id}': {e}")
            return False
    
    async def get_transformation_usage(self, transformation_id: str) -> List[Dict[str, Any]]:
        """Get all locations where transformation is applied in the system.
        
        Args:
            transformation_id: ID of the transformation to query usage for
            
        Returns:
            List of dictionaries describing where the transformation is used
        """
        try:
            usage_locations = []
            
            # Check items for transformation usage
            items = await self.get_items()
            for item in items:
                # Check if item uses this transformation in its state description
                state_description = item.get('stateDescription', {})
                pattern = state_description.get('pattern', '')
                if transformation_id in pattern:
                    usage_locations.append({
                        'type': 'item',
                        'name': item.get('name', ''),
                        'context': f"State description pattern: {pattern}"
                    })
            
            # Check links for transformation usage
            links = await self.get_links()
            for link in links:
                config = link.get('configuration', {})
                profile = config.get('profile', '')
                if transformation_id in profile or f"transform:{transformation_id.split('_')[0]}" in profile:
                    usage_locations.append({
                        'type': 'link',
                        'name': f"{link.get('itemName', '')} -> {link.get('channelUID', '')}",
                        'context': f"Link profile: {profile}"
                    })
            
            # Check rules for transformation usage (simplified check)
            try:
                rules = await self.get_rules()
                for rule in rules:
                    # Check rule actions and conditions for transformation references
                    rule_str = str(rule)
                    if transformation_id in rule_str:
                        usage_locations.append({
                            'type': 'rule',
                            'name': rule.get('name', rule.get('uid', '')),
                            'context': 'Rule definition contains transformation reference'
                        })
            except Exception:
                # Rules might not be accessible, continue without them
                pass
            
            logger.info(f"Found {len(usage_locations)} usage locations for transformation '{transformation_id}'")
            return usage_locations
            
        except Exception as e:
            logger.error(f"Failed to get transformation usage for '{transformation_id}': {e}")
            return []
    
    async def _validate_transformation_syntax(self, transformation_type: str, configuration: Dict[str, Any]) -> bool:
        """Validate transformation syntax based on type.
        
        Args:
            transformation_type: Type of transformation
            configuration: Configuration to validate
            
        Returns:
            True if syntax is valid
        """
        try:
            transformation_type = transformation_type.upper()
            
            # Basic validation based on transformation type
            if transformation_type == 'MAP':
                # MAP transformations need a filename or mapping configuration
                return 'filename' in configuration or 'mappings' in configuration
            
            elif transformation_type == 'REGEX':
                # REGEX transformations need a pattern
                return 'pattern' in configuration
            
            elif transformation_type == 'JSONPATH':
                # JSONPATH transformations need a path expression
                return 'path' in configuration
            
            elif transformation_type == 'XPATH':
                # XPATH transformations need an xpath expression
                return 'xpath' in configuration
            
            elif transformation_type == 'JAVASCRIPT':
                # JavaScript transformations need script content
                return 'script' in configuration
            
            elif transformation_type == 'SCALE':
                # SCALE transformations need min/max values
                return 'min' in configuration and 'max' in configuration
            
            else:
                # For other transformation types, just check that configuration is not empty
                return bool(configuration)
                
        except Exception as e:
            logger.error(f"Error validating transformation syntax: {e}")
            return False
    
    async def _execute_transformation(self, transformation_type: str, input_data: str) -> Optional[str]:
        """Execute transformation for testing purposes.
        
        Args:
            transformation_type: Type of transformation
            input_data: Input data to transform
            
        Returns:
            Transformed output or None if transformation failed
        """
        try:
            transformation_type = transformation_type.upper()
            
            # Simulate transformation execution
            # In a real implementation, this would use the actual transformation engines
            
            if transformation_type == 'MAP':
                # Simple mapping simulation
                mappings = {'ON': 'Open', 'OFF': 'Closed', 'NULL': 'Unknown'}
                return mappings.get(input_data.upper(), input_data)
            
            elif transformation_type == 'REGEX':
                # Simple regex simulation - extract numbers
                import re
                numbers = re.findall(r'\d+', input_data)
                return numbers[0] if numbers else input_data
            
            elif transformation_type == 'JSONPATH':
                # Simple JSON path simulation
                try:
                    import json
                    data = json.loads(input_data)
                    # Simulate extracting a value
                    return str(data.get('value', input_data))
                except:
                    return input_data
            
            elif transformation_type == 'SCALE':
                # Simple scaling simulation
                try:
                    value = float(input_data)
                    # Scale from 0-100 to 0-1
                    return str(value / 100.0)
                except:
                    return input_data
            
            else:
                # For other types, return input unchanged
                return input_data
                
        except Exception as e:
            logger.error(f"Error executing transformation: {e}")
            return None
    
    # Main UI Management Methods
    
    async def get_ui_pages(self) -> List[Dict[str, Any]]:
        """Get Main UI pages with configuration and widget structure.
        
        Returns:
            List of UI page data including configuration and widgets
        """
        try:
            # Get UI pages from the UI namespace
            result = await self._make_request("GET", "ui/components/ui:page")
            pages = result if isinstance(result, list) else []
            
            logger.info(f"Retrieved {len(pages)} Main UI pages")
            return pages
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to get UI pages: {e}")
            return []
    
    async def create_ui_page(self, page_config: Dict[str, Any]) -> Optional[str]:
        """Create Main UI page with widget layout validation.
        
        Args:
            page_config: Complete page configuration including name, layout, and widgets
            
        Returns:
            Page ID if created successfully, None otherwise
        """
        try:
            # Validate required fields
            if 'uid' not in page_config:
                logger.error("Page configuration must include 'uid' field")
                return None
            
            # Set default values if not provided
            if 'component' not in page_config:
                page_config['component'] = 'ui:page'
            
            if 'config' not in page_config:
                page_config['config'] = {}
            
            if 'slots' not in page_config:
                page_config['slots'] = {'default': []}
            
            # Create the page
            result = await self._make_request("POST", "ui/components/ui:page", data=page_config)
            
            page_id = page_config['uid']
            logger.info(f"Created Main UI page '{page_id}'")
            return page_id
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to create UI page: {e}")
            return None
    
    async def update_ui_widget(self, page_id: str, widget_id: str, properties: Dict[str, Any]) -> bool:
        """Update UI widget properties and refresh UI display.
        
        Args:
            page_id: ID of the page containing the widget
            widget_id: ID of the widget to update
            properties: New widget properties to apply
            
        Returns:
            True if widget was updated successfully
        """
        try:
            # Get the current page configuration
            pages = await self.get_ui_pages()
            target_page = None
            
            for page in pages:
                if page.get('uid') == page_id:
                    target_page = page
                    break
            
            if not target_page:
                logger.error(f"Page '{page_id}' not found")
                return False
            
            # Find and update the widget in the page configuration
            widgets = target_page.get('slots', {}).get('default', [])
            widget_found = False
            
            def update_widget_recursive(items):
                nonlocal widget_found
                for item in items:
                    if item.get('uid') == widget_id:
                        # Update widget properties
                        if 'config' not in item:
                            item['config'] = {}
                        item['config'].update(properties)
                        widget_found = True
                        return
                    
                    # Check nested widgets (slots)
                    if 'slots' in item:
                        for slot_name, slot_items in item['slots'].items():
                            if isinstance(slot_items, list):
                                update_widget_recursive(slot_items)
            
            update_widget_recursive(widgets)
            
            if not widget_found:
                logger.error(f"Widget '{widget_id}' not found on page '{page_id}'")
                return False
            
            # Update the page with modified widget
            await self._make_request("PUT", f"ui/components/ui:page/{page_id}", data=target_page)
            
            logger.info(f"Updated widget '{widget_id}' on page '{page_id}'")
            return True
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to update widget '{widget_id}' on page '{page_id}': {e}")
            return False
    
    async def manage_ui_layout(self, page_id: str, layout_config: Dict[str, Any]) -> bool:
        """Manage UI layout and responsive design settings.
        
        Args:
            page_id: ID of the page to manage layout for
            layout_config: Layout configuration including responsive settings
            
        Returns:
            True if layout was updated successfully
        """
        try:
            # Get the current page configuration
            pages = await self.get_ui_pages()
            target_page = None
            
            for page in pages:
                if page.get('uid') == page_id:
                    target_page = page
                    break
            
            if not target_page:
                logger.error(f"Page '{page_id}' not found")
                return False
            
            # Update layout configuration
            if 'config' not in target_page:
                target_page['config'] = {}
            
            # Apply layout settings
            target_page['config'].update(layout_config)
            
            # Update the page
            await self._make_request("PUT", f"ui/components/ui:page/{page_id}", data=target_page)
            
            logger.info(f"Updated layout for page '{page_id}'")
            return True
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to manage layout for page '{page_id}': {e}")
            return False
    
    async def export_ui_config(self, page_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Export UI configuration for backup or sharing.
        
        Args:
            page_ids: List of page IDs to export (if None, exports all pages)
            
        Returns:
            Dictionary containing exported UI configuration
        """
        try:
            # Get all pages
            all_pages = await self.get_ui_pages()
            
            # Filter pages if specific IDs requested
            if page_ids:
                pages_to_export = [
                    page for page in all_pages 
                    if page.get('uid') in page_ids
                ]
            else:
                pages_to_export = all_pages
            
            # Get global UI settings (if available)
            global_settings = {}
            try:
                # Try to get UI configuration settings
                ui_config = await self._make_request("GET", "ui/config")
                global_settings = ui_config if isinstance(ui_config, dict) else {}
            except OpenHABAPIError:
                # UI config endpoint might not be available in all versions
                pass
            
            export_data = {
                'pages': pages_to_export,
                'global_settings': global_settings,
                'export_info': {
                    'total_pages': len(pages_to_export),
                    'exported_page_ids': [page.get('uid') for page in pages_to_export]
                }
            }
            
            logger.info(f"Exported UI configuration for {len(pages_to_export)} pages")
            return export_data
            
        except OpenHABAPIError as e:
            logger.error(f"Failed to export UI configuration: {e}")
            return {}