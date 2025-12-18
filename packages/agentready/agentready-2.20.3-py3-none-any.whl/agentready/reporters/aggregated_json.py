"""Aggregated JSON reporter for batch assessments."""

import json
from pathlib import Path

from ..models.batch_assessment import BatchAssessment


class AggregatedJSONReporter:
    """Generates single JSON file with all batch assessment data.

    Structure:
    - schema_version: Data format version
    - batch_id: Unique identifier for this batch
    - timestamp: When batch started
    - summary: Aggregated statistics
    - results: Individual repository results (including assessments)
    - total_duration_seconds: Total time for entire batch
    - agentready_version: Version used for assessment
    """

    def generate(self, batch_assessment: BatchAssessment, output_path: Path) -> Path:
        """Generate aggregated JSON file.

        Args:
            batch_assessment: Complete batch assessment with all results
            output_path: Path where JSON file should be saved

        Returns:
            Path to generated JSON file

        Raises:
            IOError: If JSON cannot be written
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(batch_assessment.to_dict(), f, indent=2, default=str)

        return output_path
