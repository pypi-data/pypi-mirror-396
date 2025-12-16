"""
RecallBricks SDK Type Definitions
Phase 2A Metacognition Features
Phase 2B Automatic Metatags Features
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


@dataclass
class PredictedMemory:
    """Represents a predicted memory that might be useful"""
    id: str
    content: str
    confidence_score: float
    reasoning: str
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PredictedMemory':
        """Create PredictedMemory from API response"""
        return cls(
            id=data.get('id', ''),
            content=data.get('content', ''),
            confidence_score=data.get('confidence_score', 0.0),
            reasoning=data.get('reasoning', ''),
            metadata=data.get('metadata')
        )


@dataclass
class SuggestedMemory:
    """Represents a suggested memory based on context"""
    id: str
    content: str
    confidence: float
    reasoning: str
    relevance_context: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SuggestedMemory':
        """Create SuggestedMemory from API response"""
        return cls(
            id=data.get('id', ''),
            content=data.get('content', ''),
            confidence=data.get('confidence', 0.0),
            reasoning=data.get('reasoning', ''),
            relevance_context=data.get('relevance_context', '')
        )


@dataclass
class LearningTrends:
    """Trends in learning metrics"""
    helpfulness_trend: str = 'stable'
    usage_trend: str = 'stable'
    growth_rate: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningTrends':
        """Create LearningTrends from API response"""
        return cls(
            helpfulness_trend=data.get('helpfulness_trend', 'stable'),
            usage_trend=data.get('usage_trend', 'stable'),
            growth_rate=data.get('growth_rate', 0.0)
        )


@dataclass
class LearningMetrics:
    """Learning metrics for memory usage analysis"""
    avg_helpfulness: float
    total_usage: int
    active_memories: int
    total_memories: int
    trends: LearningTrends

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningMetrics':
        """Create LearningMetrics from API response"""
        trends_data = data.get('trends', {})
        return cls(
            avg_helpfulness=data.get('avg_helpfulness', 0.0),
            total_usage=data.get('total_usage', 0),
            active_memories=data.get('active_memories', 0),
            total_memories=data.get('total_memories', 0),
            trends=LearningTrends.from_dict(trends_data) if trends_data else LearningTrends()
        )


@dataclass
class PatternAnalysis:
    """Pattern analysis results for memory usage"""
    summary: str
    most_useful_tags: List[str] = field(default_factory=list)
    frequently_accessed_together: List[List[str]] = field(default_factory=list)
    underutilized_memories: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatternAnalysis':
        """Create PatternAnalysis from API response"""
        return cls(
            summary=data.get('summary', ''),
            most_useful_tags=data.get('most_useful_tags', []),
            frequently_accessed_together=data.get('frequently_accessed_together', []),
            underutilized_memories=data.get('underutilized_memories', [])
        )


@dataclass
class WeightedSearchResult:
    """Search result with relevance and usage weights"""
    # Memory fields
    id: str
    text: str
    source: str = "api"
    project_id: str = "default"
    tags: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    # Weight fields
    relevance_score: float = 0.0
    usage_boost: float = 0.0
    helpfulness_boost: float = 0.0
    recency_boost: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeightedSearchResult':
        """Create WeightedSearchResult from API response"""
        return cls(
            id=data.get('id', ''),
            text=data.get('text', ''),
            source=data.get('source', 'api'),
            project_id=data.get('project_id', 'default'),
            tags=data.get('tags', []),
            metadata=data.get('metadata'),
            created_at=data.get('created_at'),
            relevance_score=data.get('relevance_score', 0.0),
            usage_boost=data.get('usage_boost', 0.0),
            helpfulness_boost=data.get('helpfulness_boost', 0.0),
            recency_boost=data.get('recency_boost', 0.0)
        )


# Phase 2B: Automatic Metatags TypedDict definitions

class MemoryMetadata(TypedDict, total=False):
    """Metadata auto-generated or user-provided for a memory"""
    tags: List[str]
    category: str
    entities: List[str]
    importance: float
    summary: str


class CategorySummary(TypedDict):
    """Summary information for a category of memories"""
    count: int
    avg_score: float
    summary: str


class RecallMemory(TypedDict, total=False):
    """A memory item returned from recall"""
    id: str
    text: str
    metadata: MemoryMetadata
    score: float
    created_at: str
    source: str
    project_id: str


class RecallResponse(TypedDict, total=False):
    """Response from the enhanced recall endpoint"""
    memories: List[RecallMemory]
    categories: Dict[str, CategorySummary]
    total: int
    count: int  # backward compatibility


@dataclass
class LearnedMemory:
    """Represents a memory saved with auto-generated metadata"""
    id: str
    text: str
    metadata: MemoryMetadata
    created_at: str
    source: str = "python-sdk"
    project_id: str = "default"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearnedMemory':
        """Create LearnedMemory from API response"""
        metadata = data.get('metadata', {})
        return cls(
            id=data.get('id', ''),
            text=data.get('text', ''),
            metadata=MemoryMetadata(
                tags=metadata.get('tags', []),
                category=metadata.get('category', ''),
                entities=metadata.get('entities', []),
                importance=metadata.get('importance', 0.0),
                summary=metadata.get('summary', '')
            ),
            created_at=data.get('created_at', ''),
            source=data.get('source', 'python-sdk'),
            project_id=data.get('project_id', 'default')
        )


@dataclass
class OrganizedRecallResult:
    """Represents organized recall results with category summaries"""
    memories: List[RecallMemory]
    categories: Dict[str, CategorySummary]
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrganizedRecallResult':
        """Create OrganizedRecallResult from API response"""
        return cls(
            memories=data.get('memories', []),
            categories=data.get('categories', {}),
            total=data.get('total', data.get('count', 0))
        )
