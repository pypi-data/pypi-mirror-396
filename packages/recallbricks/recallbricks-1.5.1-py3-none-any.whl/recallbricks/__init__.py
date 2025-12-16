"""
RecallBricks Python SDK
The Memory Layer for AI

Usage with API key (user-level access):
    >>> from recallbricks import RecallBricks
    >>> memory = RecallBricks(api_key="rb_dev_xxx")
    >>> memory.save("Important information to remember")
    >>> memories = memory.get_all()

Usage with service token (server-to-server access):
    >>> from recallbricks import RecallBricks
    >>> memory = RecallBricks(service_token="rbk_service_xxx")
    >>> memory.save("Important information to remember")
    >>> memories = memory.get_all()
"""

from .client import RecallBricks
from .exceptions import (
    RecallBricksError,
    AuthenticationError,
    RateLimitError,
    APIError,
    ValidationError,
    NotFoundError
)
from .types import (
    PredictedMemory,
    SuggestedMemory,
    LearningMetrics,
    LearningTrends,
    PatternAnalysis,
    WeightedSearchResult,
    # Phase 2B: Automatic Metatags types
    MemoryMetadata,
    CategorySummary,
    RecallMemory,
    RecallResponse,
    LearnedMemory,
    OrganizedRecallResult
)

__version__ = "1.5.1"
__all__ = [
    "RecallBricks",
    # Exceptions
    "RecallBricksError",
    "AuthenticationError",
    "RateLimitError",
    "APIError",
    "ValidationError",
    "NotFoundError",
    # Phase 2A types
    "PredictedMemory",
    "SuggestedMemory",
    "LearningMetrics",
    "LearningTrends",
    "PatternAnalysis",
    "WeightedSearchResult",
    # Phase 2B types
    "MemoryMetadata",
    "CategorySummary",
    "RecallMemory",
    "RecallResponse",
    "LearnedMemory",
    "OrganizedRecallResult"
]
