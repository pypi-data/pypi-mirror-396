"""Scorer service for calculating weighted scores and certification levels."""

from pathlib import Path

import yaml

from ..models.assessment import Assessment
from ..models.config import Config
from ..models.finding import Finding


class Scorer:
    """Calculates weighted scores and determines certification levels.

    Implements tier-based weight distribution with heavy penalties for
    missing essentials (especially CLAUDE.md at 10% weight).
    """

    def __init__(self, default_weights_path: Path | None = None):
        """Initialize scorer with default weights.

        Args:
            default_weights_path: Path to default-weights.yaml
                                 (defaults to package data directory)
        """
        if default_weights_path is None:
            data_dir = Path(__file__).parent.parent / "data"
            default_weights_path = data_dir / "default-weights.yaml"

        self.default_weights = self._load_weights(default_weights_path)

    def _load_weights(self, path: Path) -> dict[str, float]:
        """Load default weights from YAML file.

        Args:
            path: Path to weights YAML file

        Returns:
            Dictionary mapping attribute ID to weight

        Raises:
            FileNotFoundError: If weights file not found
            ValueError: If weights are invalid
        """
        if not path.exists():
            raise FileNotFoundError(f"Weights file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            weights = yaml.safe_load(f)

        # Validate weights sum to 1.0
        total = sum(weights.values())
        tolerance = 0.001

        if abs(total - 1.0) > tolerance:
            raise ValueError(
                f"Default weights must sum to 1.0 (got {total:.4f}, "
                f"difference: {total - 1.0:+.4f})"
            )

        return weights

    def merge_and_rescale_weights(self, config: Config | None) -> dict[str, float]:
        """Merge config overrides with tier defaults and rescale to sum to 1.0.

        Args:
            config: User configuration with weight overrides (or None)

        Returns:
            Final weights dictionary (complete, sums to 1.0)

        Algorithm:
        1. Start with tier defaults
        2. Override with config values
        3. Rescale to sum to 1.0
        """
        # Start with tier defaults
        final_weights = self.default_weights.copy()

        # Override with config values
        if config and config.weights:
            final_weights.update(config.weights)

        # Rescale to sum to 1.0
        total = sum(final_weights.values())
        rescaled = {attr: w / total for attr, w in final_weights.items()}

        return rescaled

    def calculate_overall_score(
        self, findings: list[Finding], config: Config | None = None
    ) -> float:
        """Calculate weighted overall score from findings.

        Args:
            findings: List of assessment findings
            config: User configuration with custom weights (optional)

        Returns:
            Overall score 0-100

        Per FR-027: Only include successfully evaluated attributes in score.
        Skipped/error attributes are excluded from denominator.

        Edge Cases:
            - If all attributes are skipped/error/not_applicable, returns 0.0
              (total_weight = 0, no attributes successfully assessed)
            - If findings list is empty, returns 0.0
            - If an attribute has no score (score=None), it's excluded from calculation
            - Scores are rounded to 1 decimal place for consistency

        Semantic Note:
            A score of 0.0 can mean either:
            1. Repository scored 0 (assessed but failed all attributes), OR
            2. Repository was not assessable (all attributes skipped)

            To distinguish these cases, check assessment.attributes_assessed:
            - attributes_assessed = 0 → not assessable
            - attributes_assessed > 0 → actually scored 0
        """
        weights = self.merge_and_rescale_weights(config)

        # Calculate weighted score
        total_score = 0.0
        total_weight = 0.0

        for finding in findings:
            attr_id = finding.attribute.id

            # Skip attributes that weren't assessed
            if finding.status in ("skipped", "error", "not_applicable"):
                continue

            # Get weight for this attribute
            weight = weights.get(attr_id, finding.attribute.default_weight)

            # Add to weighted score
            if finding.score is not None:
                total_score += finding.score * weight
                total_weight += weight

        # Normalize score (divide by total weight of assessed attributes)
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            normalized_score = 0.0

        return round(normalized_score, 1)

    def count_assessed_attributes(self, findings: list[Finding]) -> tuple[int, int]:
        """Count assessed and skipped attributes.

        Args:
            findings: List of assessment findings

        Returns:
            Tuple of (assessed_count, skipped_count)
        """
        assessed = sum(1 for f in findings if f.status in ("pass", "fail"))

        skipped = sum(
            1 for f in findings if f.status in ("skipped", "error", "not_applicable")
        )

        return assessed, skipped

    def determine_certification_level(self, score: float) -> str:
        """Determine certification level based on score.

        Uses Assessment.determine_certification_level() for consistency.

        Args:
            score: Overall score 0-100

        Returns:
            Certification level string
        """
        return Assessment.determine_certification_level(score)
