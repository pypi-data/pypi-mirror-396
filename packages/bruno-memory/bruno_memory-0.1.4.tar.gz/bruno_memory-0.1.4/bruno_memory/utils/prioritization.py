"""
Memory prioritization and scoring system for bruno-memory.

Provides automatic scoring, ranking, and pruning of memories based on:
- Recency: More recent memories score higher
- Frequency: Frequently accessed memories score higher
- Importance: User-marked or algorithmically detected importance
- Emotional significance: Detected from content
"""

import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from bruno_core.models import MemoryEntry

logger = logging.getLogger(__name__)


@dataclass
class MemoryScore:
    """Score breakdown for a memory."""

    memory_id: str
    recency_score: float
    frequency_score: float
    importance_score: float
    emotional_score: float
    total_score: float


class MemoryScorer:
    """
    Calculate priority scores for memories.

    Combines multiple signals to determine memory importance:
    - Recency: Exponential decay based on age
    - Frequency: Based on access count
    - Importance: User-marked or inferred
    - Emotional: Based on sentiment/significance
    """

    def __init__(
        self,
        recency_weight: float = 0.3,
        frequency_weight: float = 0.3,
        importance_weight: float = 0.3,
        emotional_weight: float = 0.1,
        recency_half_life_days: float = 7.0,
    ):
        """
        Initialize memory scorer.

        Args:
            recency_weight: Weight for recency score (0-1)
            frequency_weight: Weight for frequency score (0-1)
            importance_weight: Weight for importance score (0-1)
            emotional_weight: Weight for emotional score (0-1)
            recency_half_life_days: Days for recency score to decay to 50%
        """
        total = recency_weight + frequency_weight + importance_weight + emotional_weight
        self.recency_weight = recency_weight / total
        self.frequency_weight = frequency_weight / total
        self.importance_weight = importance_weight / total
        self.emotional_weight = emotional_weight / total
        self.recency_half_life = recency_half_life_days

        self.access_counts: Counter = Counter()
        logger.info("MemoryScorer initialized")

    def calculate_recency_score(
        self, memory: MemoryEntry, reference_time: datetime | None = None
    ) -> float:
        """
        Calculate recency score using exponential decay.

        Args:
            memory: Memory entry to score
            reference_time: Time to calculate from (default: now)

        Returns:
            Score from 0.0 to 1.0 (1.0 = most recent)
        """
        if not memory.created_at:
            return 0.5  # Neutral score if no timestamp

        ref_time = reference_time or datetime.now(memory.created_at.tzinfo)
        age_days = (ref_time - memory.created_at).total_seconds() / 86400

        # Exponential decay: score = 2^(-age/half_life)
        score = 2 ** (-age_days / self.recency_half_life)
        return min(1.0, score)

    def calculate_frequency_score(self, memory_id: str) -> float:
        """
        Calculate frequency score based on access count.

        Args:
            memory_id: Memory identifier

        Returns:
            Score from 0.0 to 1.0 (normalized by max access)
        """
        access_count = self.access_counts[memory_id]
        if not self.access_counts:
            return 0.5

        max_count = max(self.access_counts.values())
        if max_count == 0:
            return 0.5

        # Logarithmic scaling for diminishing returns
        if NUMPY_AVAILABLE:
            score = np.log1p(access_count) / np.log1p(max_count)
        else:
            import math

            score = math.log1p(access_count) / math.log1p(max_count)

        return score

    def calculate_importance_score(self, memory: MemoryEntry) -> float:
        """
        Calculate importance score from metadata.

        Args:
            memory: Memory entry to score

        Returns:
            Score from 0.0 to 1.0
        """
        if memory.metadata and hasattr(memory.metadata, "importance"):
            return float(memory.metadata.importance)
        return 0.5  # Neutral if not specified

    def calculate_emotional_score(self, memory: MemoryEntry) -> float:
        """
        Calculate emotional significance score.

        Uses simple heuristics to detect emotional content.
        Could be enhanced with sentiment analysis library.

        Args:
            memory: Memory entry to score

        Returns:
            Score from 0.0 to 1.0
        """
        # Simple keyword-based detection
        emotional_keywords = {
            "love",
            "hate",
            "fear",
            "joy",
            "sad",
            "angry",
            "happy",
            "excited",
            "worried",
            "amazing",
            "terrible",
            "wonderful",
            "awful",
            "fantastic",
            "horrible",
            "great",
            "bad",
            "!",
            "!!!",
        }

        content_lower = memory.content.lower()
        keyword_count = sum(1 for kw in emotional_keywords if kw in content_lower)

        # Check for multiple exclamation marks or caps
        exclamations = content_lower.count("!")
        caps_ratio = sum(1 for c in memory.content if c.isupper()) / max(len(memory.content), 1)

        # Combine signals
        keyword_score = min(keyword_count / 3.0, 1.0)
        exclamation_score = min(exclamations / 3.0, 1.0)
        caps_score = min(caps_ratio * 2.0, 1.0)

        score = (keyword_score + exclamation_score + caps_score) / 3.0
        return score

    def score_memory(
        self, memory: MemoryEntry, reference_time: datetime | None = None
    ) -> MemoryScore:
        """
        Calculate comprehensive score for a memory.

        Args:
            memory: Memory to score
            reference_time: Reference time for recency

        Returns:
            MemoryScore with breakdown
        """
        memory_id = str(memory.id)

        recency = self.calculate_recency_score(memory, reference_time)
        frequency = self.calculate_frequency_score(memory_id)
        importance = self.calculate_importance_score(memory)
        emotional = self.calculate_emotional_score(memory)

        total = (
            recency * self.recency_weight
            + frequency * self.frequency_weight
            + importance * self.importance_weight
            + emotional * self.emotional_weight
        )

        return MemoryScore(
            memory_id=memory_id,
            recency_score=recency,
            frequency_score=frequency,
            importance_score=importance,
            emotional_score=emotional,
            total_score=total,
        )

    def record_access(self, memory_id: str) -> None:
        """
        Record that a memory was accessed.

        Args:
            memory_id: Memory identifier
        """
        self.access_counts[memory_id] += 1

    def get_access_stats(self) -> dict[str, int]:
        """
        Get access count statistics.

        Returns:
            Dictionary of memory_id to access count
        """
        return dict(self.access_counts)


class MemoryPruner:
    """
    Automatic memory pruning based on priority scores.

    Helps manage memory usage by removing low-priority memories.
    """

    def __init__(
        self,
        scorer: MemoryScorer,
        min_score_threshold: float = 0.2,
        max_age_days: int | None = None,
    ):
        """
        Initialize memory pruner.

        Args:
            scorer: MemoryScorer instance
            min_score_threshold: Minimum score to keep
            max_age_days: Maximum age in days (None = no limit)
        """
        self.scorer = scorer
        self.min_score_threshold = min_score_threshold
        self.max_age_days = max_age_days
        logger.info(f"MemoryPruner initialized: threshold={min_score_threshold}")

    def should_prune(self, memory: MemoryEntry, reference_time: datetime | None = None) -> bool:
        """
        Determine if a memory should be pruned.

        Args:
            memory: Memory to evaluate
            reference_time: Reference time for age calculation

        Returns:
            True if memory should be pruned
        """
        # Check age limit
        if self.max_age_days and memory.created_at:
            ref_time = reference_time or datetime.now(memory.created_at.tzinfo)
            age_days = (ref_time - memory.created_at).total_seconds() / 86400
            if age_days > self.max_age_days:
                return True

        # Check score threshold
        score = self.scorer.score_memory(memory, reference_time)
        return score.total_score < self.min_score_threshold

    def get_prunable_memories(
        self, memories: list[MemoryEntry], reference_time: datetime | None = None
    ) -> list[MemoryEntry]:
        """
        Get list of memories that should be pruned.

        Args:
            memories: List of memories to evaluate
            reference_time: Reference time for calculations

        Returns:
            List of memories to prune
        """
        prunable = []
        for memory in memories:
            if self.should_prune(memory, reference_time):
                prunable.append(memory)

        logger.info(f"Identified {len(prunable)}/{len(memories)} memories for pruning")
        return prunable

    def rank_memories(
        self,
        memories: list[MemoryEntry],
        limit: int | None = None,
        reference_time: datetime | None = None,
    ) -> list[tuple[MemoryEntry, MemoryScore]]:
        """
        Rank memories by priority score.

        Args:
            memories: List of memories to rank
            limit: Maximum number to return (None = all)
            reference_time: Reference time for scoring

        Returns:
            List of (memory, score) tuples, sorted by score descending
        """
        scored = [(memory, self.scorer.score_memory(memory, reference_time)) for memory in memories]

        # Sort by total score descending
        ranked = sorted(scored, key=lambda x: x[1].total_score, reverse=True)

        if limit:
            ranked = ranked[:limit]

        return ranked


# Convenience functions
def score_memories(
    memories: list[MemoryEntry],
    recency_weight: float = 0.3,
    frequency_weight: float = 0.3,
    importance_weight: float = 0.3,
    emotional_weight: float = 0.1,
) -> list[MemoryScore]:
    """
    Quick scoring of memories.

    Args:
        memories: List of memories to score
        recency_weight: Weight for recency
        frequency_weight: Weight for frequency
        importance_weight: Weight for importance
        emotional_weight: Weight for emotional significance

    Returns:
        List of MemoryScore objects
    """
    scorer = MemoryScorer(
        recency_weight=recency_weight,
        frequency_weight=frequency_weight,
        importance_weight=importance_weight,
        emotional_weight=emotional_weight,
    )

    return [scorer.score_memory(mem) for mem in memories]


def prune_low_priority_memories(
    memories: list[MemoryEntry], threshold: float = 0.2, max_age_days: int | None = None
) -> tuple[list[MemoryEntry], list[MemoryEntry]]:
    """
    Split memories into keep and prune lists.

    Args:
        memories: List of memories to evaluate
        threshold: Minimum score to keep
        max_age_days: Maximum age in days

    Returns:
        Tuple of (keep_list, prune_list)
    """
    scorer = MemoryScorer()
    pruner = MemoryPruner(scorer, threshold, max_age_days)

    prunable = pruner.get_prunable_memories(memories)
    # Use IDs to identify prunable memories (MemoryEntry is not hashable)
    prunable_ids = {str(m.id) for m in prunable}
    keep = [m for m in memories if str(m.id) not in prunable_ids]
    prune = list(prunable)

    return keep, prune
