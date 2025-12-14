"""
Rate Limiting and Security Module for TTS Service
"""

import time
import hashlib
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for the given identifier
        
        Args:
            identifier: Unique identifier (IP, API key, etc.)
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    def get_reset_time(self, identifier: str) -> float:
        """Get time until rate limit resets for identifier"""
        if not self.requests[identifier]:
            return 0
        
        oldest_request = self.requests[identifier][0]
        return oldest_request + self.window_seconds - time.time()

class APIKeyValidator:
    def __init__(self, valid_keys: Optional[Dict[str, Dict]] = None):
        """
        Initialize API key validator
        
        Args:
            valid_keys: Dict of valid API keys with metadata
        """
        self.valid_keys = valid_keys or {}
    
    def validate_key(self, api_key: str) -> Optional[Dict]:
        """
        Validate API key and return metadata
        
        Args:
            api_key: API key to validate
            
        Returns:
            Key metadata if valid, None otherwise
        """
        return self.valid_keys.get(api_key)
    
    def add_key(self, api_key: str, metadata: Dict):
        """Add a new API key"""
        self.valid_keys[api_key] = metadata
    
    def remove_key(self, api_key: str):
        """Remove an API key"""
        self.valid_keys.pop(api_key, None)

class SecurityMiddleware:
    def __init__(self, 
                 rate_limiter: Optional[RateLimiter] = None,
                 api_validator: Optional[APIKeyValidator] = None,
                 require_api_key: bool = False):
        """
        Initialize security middleware
        
        Args:
            rate_limiter: Rate limiter instance
            api_validator: API key validator instance
            require_api_key: Whether to require API key for all requests
        """
        self.rate_limiter = rate_limiter or RateLimiter()
        self.api_validator = api_validator or APIKeyValidator()
        self.require_api_key = require_api_key
    
    async def check_request(self, request: Request) -> Dict:
        """
        Check request security and rate limiting
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dict with security check results
            
        Raises:
            HTTPException: If request is not allowed
        """
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
        
        # Determine identifier for rate limiting
        identifier = api_key if api_key else client_ip
        
        # API key validation
        key_metadata = None
        if api_key:
            key_metadata = self.api_validator.validate_key(api_key)
            if not key_metadata:
                logger.warning(f"Invalid API key used: {api_key[:8]}...")
                raise HTTPException(status_code=401, detail="Invalid API key")
        elif self.require_api_key:
            raise HTTPException(status_code=401, detail="API key required")
        
        # Rate limiting
        if not self.rate_limiter.is_allowed(identifier):
            reset_time = self.rate_limiter.get_reset_time(identifier)
            logger.warning(f"Rate limit exceeded for {identifier}")
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limit exceeded. Try again in {int(reset_time)} seconds",
                headers={"Retry-After": str(int(reset_time))}
            )
        
        return {
            "client_ip": client_ip,
            "api_key": api_key,
            "key_metadata": key_metadata,
            "identifier": identifier
        }

def sanitize_text(text: str, max_length: int = 5000) -> str:
    """
    Sanitize input text for TTS processing
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        ValueError: If text is invalid
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    # Remove or replace potentially problematic characters
    text = text.strip()
    
    # Length check
    if len(text) > max_length:
        raise ValueError(f"Text too long. Maximum {max_length} characters allowed")
    
    # Basic content filtering (can be extended)
    forbidden_patterns = [
        # Add patterns for content you want to block
        # Example: r'\b(spam|abuse)\b'
    ]
    
    import re
    for pattern in forbidden_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Text contains forbidden content")
    
    return text

def generate_api_key(prefix: str = "tts") -> str:
    """
    Generate a new API key
    
    Args:
        prefix: Prefix for the API key
        
    Returns:
        Generated API key
    """
    import secrets
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"

# Usage tracking
class UsageTracker:
    def __init__(self):
        self.stats = defaultdict(lambda: {
            "requests": 0,
            "characters": 0,
            "audio_files": 0,
            "errors": 0,
            "last_request": None
        })
    
    def record_request(self, identifier: str, character_count: int, success: bool = True):
        """Record a request for usage tracking"""
        stats = self.stats[identifier]
        stats["requests"] += 1
        stats["characters"] += character_count
        stats["last_request"] = time.time()
        
        if success:
            stats["audio_files"] += 1
        else:
            stats["errors"] += 1
    
    def get_stats(self, identifier: str) -> Dict:
        """Get usage statistics for an identifier"""
        return dict(self.stats[identifier])
    
    def get_all_stats(self) -> Dict:
        """Get all usage statistics"""
        return dict(self.stats)
