"""
Rate Limiter - A Python library for rate limiting in FastAPI and Flask applications.
"""

from .core import RateLimiter, RateLimitExceeded
from .fastapi_integration import FastAPIRateLimiter, rate_limit
from .flask_integration import FlaskRateLimiter

__version__ = "0.1.0"
__all__ = [
    "RateLimiter",
    "RateLimitExceeded",
    "FastAPIRateLimiter",
    "rate_limit",
    "FlaskRateLimiter",
]

