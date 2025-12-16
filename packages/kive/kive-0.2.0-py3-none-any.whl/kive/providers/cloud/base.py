"""Cloud provider base class"""
from abc import abstractmethod
from functools import wraps
from typing import Optional
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt
import httpx
import requests

from ..base import BaseProvider


# ===== Decorators =====

def retry_on_network_error(max_attempts: int = 3, min_wait: int = 1, max_wait: int = 10):
    """Retry decorator for network errors
    
    Args:
        max_attempts: Maximum retry attempts (default: 3)
        min_wait: Minimum wait seconds between retries (default: 1)
        max_wait: Maximum wait seconds between retries (default: 10)
    """
    return retry(
        retry=retry_if_exception_type((
            ConnectionError,
            TimeoutError,
            httpx.ConnectError,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.ConnectTimeout,
            httpx.NetworkError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        )),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        stop=stop_after_attempt(max_attempts),
        reraise=True
    )

def use_sync(func):
    """Ensure sync client is initialized before method call"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._sync_client is None:
            self.init_sync_client()
        return func(self, *args, **kwargs)
    return wrapper


def use_async(func):
    """Ensure async client is initialized before method call"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self._async_client is None:
            self.init_async_client()
        return await func(self, *args, **kwargs)
    return wrapper


class CloudProvider(BaseProvider):
    """Base class for cloud memory providers"""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize cloud provider
        
        Args:
            api_key: Provider API key
            **kwargs: Provider-specific config
        """
        self.api_key = api_key
        self.config = kwargs
        
        # Lazy-initialized clients
        self._sync_client = None
        self._async_client = None
    
    @abstractmethod
    def init_sync_client(self):
        """Initialize sync client"""
        pass
    
    @abstractmethod
    def init_async_client(self):
        """Initialize async client"""
        pass
