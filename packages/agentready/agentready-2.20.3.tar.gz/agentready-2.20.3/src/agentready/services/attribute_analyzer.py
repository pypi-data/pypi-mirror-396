"""Attribute correlation analysis with Plotly Express heatmap."""

import json
from pathlib import Path
from typing import List

import pandas as pd
import plotly.express as px
from scipy.stats import pearsonr


class AttributeAnalyzer:
    """Analyze correlation between AgentReady attributes and SWE-bench performance."""

    def analyze(
        self,
        result_files: List[Path],
        output_file: Path = None,
        heatmap_file: Path = None,
    ) -> dict:
        """
        Analyze correlation and generate heatmap.

        Args:
            result_files: List of experiment result JSON files
            output_file: Where to save analysis.json
            heatmap_file: Where to save heatmap.html

        Returns:
            Analysis dict with correlation and top attributes
        """
        # Load all results
        results = []
        for f in result_files:
            with open(f) as fp:
                results.append(json.load(fp))

        # Calculate overall correlation
        agentready_scores = [r["agentready_score"] for r in results]
        swebench_scores = [r["swebench_score"] for r in results]

        correlation, p_value = pearsonr(agentready_scores, swebench_scores)

        # Create DataFrame for heatmap
        heatmap_data = {}
        for result in results:
            config = result["config_name"]
            agent = result["agent"]
            score = result["swebench_score"]

            if config not in heatmap_data:
                heatmap_data[config] = {}
            heatmap_data[config][agent] = score

        df = pd.DataFrame(heatmap_data)

        # Generate interactive heatmap
        if heatmap_file:
            self._create_experiment_heatmap(df, heatmap_file)

        # Prepare analysis output
        analysis = {
            "correlation": {
                "overall": round(correlation, 3),
                "p_value": round(p_value, 6),
            },
            "top_attributes": self._rank_attributes(results),
            "heatmap_path": str(heatmap_file) if heatmap_file else None,
        }

        if output_file:
            with open(output_file, "w") as f:
                json.dump(analysis, f, indent=2)

        return analysis

    def _create_experiment_heatmap(self, df: pd.DataFrame, output_path: Path):
        """Create interactive Plotly Express heatmap for SWE-bench experiments."""

        # Calculate deltas from baseline
        if "baseline" in df.columns:
            baseline = df["baseline"].values
            delta_df = df.copy()
            for col in df.columns:
                delta_df[col] = df[col] - baseline
        else:
            delta_df = df.copy()

        # Transpose: configs as rows, agents as columns
        df_t = df.T
        delta_t = delta_df.T

        # Create heatmap
        fig = px.imshow(
            df_t,
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=45,
            labels=dict(x="Agent", y="Configuration", color="Pass Rate (%)"),
            text_auto=".1f",
            aspect="auto",
            zmin=35,
            zmax=55,
        )

        # Add custom hover with deltas
        hover_text = []
        for i, config in enumerate(df_t.index):
            row_text = []
            for j, agent in enumerate(df_t.columns):
                score = df_t.iloc[i, j]
                delta = delta_t.iloc[i, j]
                text = (
                    f"<b>Agent:</b> {agent}<br>"
                    f"<b>Config:</b> {config}<br>"
                    f"<b>Score:</b> {score:.1f}%<br>"
                    f"<b>Delta from baseline:</b> {delta:+.1f}pp"
                )
                row_text.append(text)
            hover_text.append(row_text)

        fig.update_traces(
            hovertemplate="%{customdata}<extra></extra>", customdata=hover_text
        )

        # Customize layout
        fig.update_layout(
            title="SWE-bench Performance: AgentReady Configurations",
            xaxis_title="Agent",
            yaxis_title="Configuration",
            width=900,
            height=600,
            font=dict(size=12),
        )

        # Save standalone HTML
        fig.write_html(output_path)
        print(f"✓ Interactive heatmap saved to: {output_path}")

    def _rank_attributes(self, results: List[dict]) -> List[dict]:
        """Rank attributes by impact."""
        config_impacts = {}
        baseline_scores = {}

        for result in results:
            agent = result["agent"]
            config = result["config_name"]
            score = result["swebench_score"]

            if config == "baseline":
                baseline_scores[agent] = score
            elif agent in baseline_scores:
                delta = score - baseline_scores[agent]
                if config not in config_impacts:
                    config_impacts[config] = []
                config_impacts[config].append(delta)

        # Calculate average improvement per config
        ranked = []
        for config, deltas in config_impacts.items():
            avg_delta = sum(deltas) / len(deltas)
            ranked.append({"config": config, "avg_improvement": round(avg_delta, 1)})

        ranked.sort(key=lambda x: x["avg_improvement"], reverse=True)
        return ranked[:5]

    def analyze_batch(self, batch_assessment, heatmap_file: Path):
        """
        Generate heatmap visualization for batch assessment.

        Args:
            batch_assessment: BatchAssessment object with repository results
            heatmap_file: Where to save heatmap.html

        Creates interactive heatmap showing repos × attributes with scores.
        """
        # Prepare DataFrame
        df, hover_data, overall_scores = self._prepare_batch_dataframe(batch_assessment)

        # Generate heatmap
        self._create_batch_heatmap(df, hover_data, overall_scores, heatmap_file)

    def analyze_batch_from_json(self, batch_data: dict, heatmap_file: Path):
        """
        Generate heatmap visualization from batch assessment JSON data.

        Args:
            batch_data: Batch assessment as dictionary (from all-assessments.json)
            heatmap_file: Where to save heatmap.html

        Creates interactive heatmap showing repos × attributes with scores.
        Works directly with JSON data, bypassing deserialization.
        """
        # Prepare DataFrame from dict data
        df, hover_data, overall_scores = self._prepare_batch_dataframe_from_json(
            batch_data
        )

        # Generate heatmap
        self._create_batch_heatmap(df, hover_data, overall_scores, heatmap_file)

    def _prepare_batch_dataframe(self, batch_assessment):
        """
        Transform BatchAssessment into DataFrame for heatmap.

        Returns:
            tuple: (DataFrame, hover_data dict, overall_scores dict)
                - DataFrame: repos (rows) × attributes (cols), values = scores or NaN
                - hover_data: Nested dict with tooltip info per repo/attribute
                - overall_scores: Dict mapping repo name → (overall_score, certification)
        """
        # Collect successful assessments
        assessments = [r.assessment for r in batch_assessment.results if r.is_success()]

        if not assessments:
            raise ValueError("No successful assessments to visualize")

        # Build matrix and hover data
        matrix_data = {}
        hover_data = {}
        overall_scores = {}

        for assessment in assessments:
            repo_name = assessment.repository.name

            # Store overall score and certification
            overall_scores[repo_name] = (
                assessment.overall_score,
                assessment.certification_level,
            )

            matrix_data[repo_name] = {}
            hover_data[repo_name] = {}

            # Track seen attributes to handle duplicates (take first occurrence only)
            seen_attrs = set()

            for finding in assessment.findings:
                attr_id = finding.attribute.id

                # Skip duplicate attributes (assessor bug workaround)
                if attr_id in seen_attrs:
                    continue
                seen_attrs.add(attr_id)

                # Map status to score
                if finding.status in ("pass", "fail"):
                    score = finding.score
                elif finding.status == "not_applicable":
                    score = None  # Will become NaN in DataFrame (shown as gray)
                else:  # skipped, error
                    score = 0.0  # Show as red

                matrix_data[repo_name][attr_id] = score

                # Store hover metadata
                hover_data[repo_name][attr_id] = {
                    "attribute_name": finding.attribute.name,
                    "tier": finding.attribute.tier,
                    "status": finding.status,
                    "measured_value": finding.measured_value or "N/A",
                    "threshold": finding.threshold or "N/A",
                }

        # Convert to DataFrame (repos as rows, attributes as columns)
        df = pd.DataFrame(matrix_data).T

        # Sort repos by overall score (descending)
        df["_sort_score"] = df.index.map(lambda x: overall_scores[x][0])
        df = df.sort_values("_sort_score", ascending=False)
        df = df.drop("_sort_score", axis=1)

        # Sort attributes by tier, then alphabetically
        # Get tier mapping from first assessment
        attr_tiers = {
            finding.attribute.id: finding.attribute.tier
            for finding in assessments[0].findings
        }

        sorted_cols = sorted(df.columns, key=lambda x: (attr_tiers.get(x, 99), x))
        df = df[sorted_cols]

        return df, hover_data, overall_scores

    def _prepare_batch_dataframe_from_json(self, batch_data: dict):
        """
        Transform batch assessment JSON into DataFrame for heatmap.

        Args:
            batch_data: Batch assessment dictionary (from all-assessments.json)

        Returns:
            tuple: (DataFrame, hover_data dict, overall_scores dict)
                - DataFrame: repos (rows) × attributes (cols), values = scores or NaN
                - hover_data: Nested dict with tooltip info per repo/attribute
                - overall_scores: Dict mapping repo name → (overall_score, certification)
        """
        # Collect successful assessments
        assessments = [
            r["assessment"]
            for r in batch_data["results"]
            if r.get("assessment") is not None
        ]

        if not assessments:
            raise ValueError("No successful assessments to visualize")

        # Build matrix and hover data
        matrix_data = {}
        hover_data = {}
        overall_scores = {}

        for assessment in assessments:
            repo_name = assessment["repository"]["name"]

            # Store overall score and certification
            overall_scores[repo_name] = (
                assessment["overall_score"],
                assessment["certification_level"],
            )

            matrix_data[repo_name] = {}
            hover_data[repo_name] = {}

            # Track seen attributes to handle duplicates (take first occurrence only)
            seen_attrs = set()

            for finding in assessment["findings"]:
                attr_id = finding["attribute"]["id"]

                # Skip duplicate attributes (assessor bug workaround)
                if attr_id in seen_attrs:
                    continue
                seen_attrs.add(attr_id)

                # Map status to score
                if finding["status"] in ("pass", "fail"):
                    score = finding["score"]
                elif finding["status"] == "not_applicable":
                    score = None  # Will become NaN in DataFrame (shown as gray)
                else:  # skipped, error
                    score = 0.0  # Show as red

                matrix_data[repo_name][attr_id] = score

                # Store hover metadata
                hover_data[repo_name][attr_id] = {
                    "attribute_name": finding["attribute"]["name"],
                    "tier": finding["attribute"]["tier"],
                    "status": finding["status"],
                    "measured_value": finding.get("measured_value") or "N/A",
                    "threshold": finding.get("threshold") or "N/A",
                }

        # Convert to DataFrame (repos as rows, attributes as columns)
        df = pd.DataFrame(matrix_data).T

        # Sort repos by overall score (descending)
        df["_sort_score"] = df.index.map(lambda x: overall_scores[x][0])
        df = df.sort_values("_sort_score", ascending=False)
        df = df.drop("_sort_score", axis=1)

        # Sort attributes by tier, then alphabetically
        # Get tier mapping from first assessment
        attr_tiers = {
            finding["attribute"]["id"]: finding["attribute"]["tier"]
            for finding in assessments[0]["findings"]
        }

        sorted_cols = sorted(df.columns, key=lambda x: (attr_tiers.get(x, 99), x))
        df = df[sorted_cols]

        return df, hover_data, overall_scores

    def _create_batch_heatmap(
        self,
        df: pd.DataFrame,
        hover_data: dict,
        overall_scores: dict,
        output_path: Path,
    ):
        """
        Generate interactive Plotly heatmap for batch assessment.

        Features:
        - Color: RdYlGn gradient (0-100), gray for NaN (N/A attributes)
        - X-axis: Attributes (sorted by tier)
        - Y-axis: Repositories (sorted by overall score, descending)
        - Hover: Repo, attribute, tier, score, status, measured value, overall score
        - Annotations: Certification badges on left margin
        """
        # Handle NaN values for visualization
        # Replace NaN with -1 for custom colorscale (will show as gray)
        df_display = df.fillna(-1)

        # Custom discrete colorscale with gray for N/A (-1)
        colorscale = [
            [0.0, "#D3D3D3"],  # -1 (N/A) → Gray
            [0.001, "#D73027"],  # 0-39 → Red (Needs Improvement)
            [0.4, "#FEE08B"],  # 40-59 → Yellow (Bronze)
            [0.6, "#D9EF8B"],  # 60-74 → Light Green (Silver)
            [0.75, "#66BD63"],  # 75-89 → Green (Gold)
            [1.0, "#1A9850"],  # 90-100 → Dark Green (Platinum)
        ]

        # Create heatmap
        fig = px.imshow(
            df_display,
            color_continuous_scale=colorscale,
            zmin=-1,
            zmax=100,
            labels=dict(
                x="Attributes (sorted by tier)", y="Repositories", color="Score"
            ),
            aspect="auto",
        )

        # Build custom hover tooltips
        hover_text = []
        for i, repo_name in enumerate(df.index):
            row_text = []
            overall_score, cert_level = overall_scores[repo_name]

            for j, attr_id in enumerate(df.columns):
                score_val = df.iloc[i, j]
                attr_info = hover_data[repo_name][attr_id]

                if pd.isna(score_val):
                    score_display = "N/A"
                else:
                    score_display = f"{score_val:.1f}"

                text = (
                    f"<b>Repository:</b> {repo_name}<br>"
                    f"<b>Attribute:</b> {attr_info['attribute_name']}<br>"
                    f"<b>Tier:</b> {attr_info['tier']}<br>"
                    f"<b>Score:</b> {score_display}/100<br>"
                    f"<b>Status:</b> {attr_info['status']}<br>"
                    f"<b>Measured:</b> {attr_info['measured_value']}<br>"
                    f"<b>Overall:</b> {overall_score:.1f}/100 ({cert_level})<br>"
                )
                row_text.append(text)
            hover_text.append(row_text)

        fig.update_traces(
            hovertemplate="%{customdata}<extra></extra>", customdata=hover_text
        )

        # Add certification badge annotations on left margin
        cert_badges = {
            "Platinum": "💎",
            "Gold": "🥇",
            "Silver": "🥈",
            "Bronze": "🥉",
            "Needs Improvement": "⚠️",
        }

        annotations = []
        for i, repo_name in enumerate(df.index):
            overall_score, cert_level = overall_scores[repo_name]
            badge = cert_badges.get(cert_level, "")

            annotations.append(
                dict(
                    x=-0.5,  # Left of heatmap
                    y=i,
                    text=f"{badge} {overall_score:.1f}",
                    showarrow=False,
                    xanchor="right",
                    font=dict(size=10, color="#333"),
                )
            )

        # Customize layout
        fig.update_layout(
            title=f"AgentReady Batch Assessment: {len(df)} Repositories × {len(df.columns)} Attributes",
            xaxis_title="Attributes (sorted by tier, then alphabetically)",
            yaxis_title="Repositories (sorted by overall score, high → low)",
            width=max(1400, len(df.columns) * 40),  # Dynamic width
            height=max(600, len(df) * 25),  # Dynamic height
            font=dict(size=10),
            xaxis=dict(tickangle=45, side="bottom"),
            margin=dict(l=250, r=50, t=100, b=150),  # Space for labels and badges
            annotations=annotations,
        )

        # Save standalone HTML
        fig.write_html(output_path)
        print(f"✓ Interactive batch heatmap saved to: {output_path}")
