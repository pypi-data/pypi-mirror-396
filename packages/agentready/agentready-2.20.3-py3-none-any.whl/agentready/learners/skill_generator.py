"""Skill generation from discovered patterns."""

from pathlib import Path

from agentready.models import DiscoveredSkill


class SkillGenerator:
    """Generates Claude Code skills from discovered patterns.

    Handles file I/O and format conversion for skill proposals.
    """

    def __init__(self, output_dir: Path | str = ".skills-proposals"):
        """Initialize skill generator.

        Args:
            output_dir: Directory to write generated skills
        """
        self.output_dir = Path(output_dir)

    def generate_skill_file(self, skill: DiscoveredSkill) -> Path:
        """Generate a SKILL.md file from a discovered skill.

        Args:
            skill: The discovered skill to generate

        Returns:
            Path to the generated SKILL.md file
        """
        # Create skill directory
        skill_dir = self.output_dir / skill.skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Generate SKILL.md content
        skill_content = skill.to_skill_md()

        # Write to file
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_content, encoding="utf-8")

        return skill_file

    def generate_github_issue(self, skill: DiscoveredSkill) -> Path:
        """Generate a GitHub issue template from a discovered skill.

        Args:
            skill: The discovered skill to generate

        Returns:
            Path to the generated issue template file
        """
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate issue content
        issue_content = skill.to_github_issue()

        # Write to file
        issue_file = self.output_dir / f"skill-{skill.skill_id}.md"
        issue_file.write_text(issue_content, encoding="utf-8")

        return issue_file

    def generate_markdown_report(self, skill: DiscoveredSkill) -> Path:
        """Generate a detailed markdown report for a skill.

        Args:
            skill: The discovered skill to document

        Returns:
            Path to the generated markdown report
        """
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate markdown content
        markdown_content = self._create_markdown_report(skill)

        # Write to file
        report_file = self.output_dir / f"{skill.skill_id}-report.md"
        report_file.write_text(markdown_content, encoding="utf-8")

        return report_file

    def generate_all_formats(self, skill: DiscoveredSkill) -> dict[str, Path]:
        """Generate all output formats for a skill.

        Args:
            skill: The discovered skill to generate

        Returns:
            Dictionary mapping format name to file path
        """
        return {
            "skill_md": self.generate_skill_file(skill),
            "github_issue": self.generate_github_issue(skill),
            "markdown_report": self.generate_markdown_report(skill),
        }

    def generate_batch(
        self, skills: list[DiscoveredSkill], output_format: str = "skill_md"
    ) -> list[Path]:
        """Generate multiple skills in batch.

        Args:
            skills: List of discovered skills to generate
            output_format: Format to generate (skill_md, github_issue, markdown_report, all)

        Returns:
            List of generated file paths
        """
        generated_files = []

        for skill in skills:
            if output_format == "skill_md":
                generated_files.append(self.generate_skill_file(skill))
            elif output_format == "github_issue":
                generated_files.append(self.generate_github_issue(skill))
            elif output_format == "markdown_report":
                generated_files.append(self.generate_markdown_report(skill))
            elif output_format == "all":
                results = self.generate_all_formats(skill)
                generated_files.extend(results.values())

        return generated_files

    def _create_markdown_report(self, skill: DiscoveredSkill) -> str:
        """Create a detailed markdown report for a skill.

        Args:
            skill: The skill to document

        Returns:
            Markdown report content
        """
        report = f"""# Skill Report: {skill.name}

## Overview

**Skill ID**: `{skill.skill_id}`
**Confidence**: {skill.confidence}%
**Impact**: +{skill.impact_score} pts
**Reusability**: {skill.reusability_score}%
**Source Attribute**: {skill.source_attribute_id}

---

## Description

{skill.description}

---

## Pattern Summary

{skill.pattern_summary}

---

## Implementation Guidance

### When to Use This Skill

Use this skill when you need to apply the pattern described above to your repository.

### Code Examples

"""

        if skill.code_examples:
            for idx, example in enumerate(skill.code_examples, 1):
                report += f"\n#### Example {idx}\n\n```\n{example}\n```\n"
        else:
            report += "_No code examples available_\n"

        report += "\n---\n\n## Research Citations\n\n"

        if skill.citations:
            for citation in skill.citations:
                url_part = f" - [Link]({citation.url})" if citation.url else ""
                report += f"### {citation.source}: {citation.title}{url_part}\n\n"
                report += f"**Relevance**: {citation.relevance}\n\n"
        else:
            report += "_No citations available_\n"

        report += f"""
---

## Metrics

- **Confidence Score**: {skill.confidence}% - How confident we are this is a valid pattern
- **Impact Score**: {skill.impact_score} pts - Expected score improvement from applying this skill
- **Reusability Score**: {skill.reusability_score}% - How often this pattern applies across projects

---

**Generated by**: AgentReady Skill Generator
**Source**: Pattern extracted from {skill.source_attribute_id} assessment
"""

        return report
