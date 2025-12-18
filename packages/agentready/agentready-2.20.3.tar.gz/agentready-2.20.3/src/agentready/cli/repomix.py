"""Repomix command for generating AI-friendly repository context."""

import sys
from pathlib import Path

import click

from ..services.repomix import RepomixService


@click.command()
@click.argument("repository", type=click.Path(exists=True), default=".")
@click.option(
    "--init",
    is_flag=True,
    help="Initialize Repomix configuration (config + ignore file)",
)
@click.option(
    "--format",
    type=click.Choice(["markdown", "xml", "json", "plain"], case_sensitive=False),
    default="markdown",
    help="Output format (default: markdown)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--check",
    is_flag=True,
    help="Check if Repomix output exists and is fresh (no generation)",
)
@click.option(
    "--max-age",
    type=int,
    default=7,
    help="Maximum age in days before output is considered stale (default: 7)",
)
def repomix_generate(repository, init, format, verbose, check, max_age):
    """Generate Repomix repository context for AI consumption.

    Repomix creates a single AI-optimized file containing your repository's
    structure and contents, making it easier for LLMs to understand your codebase.

    REPOSITORY: Path to git repository (default: current directory)

    Examples:

        \b
        # Initialize Repomix configuration
        agentready repomix-generate --init

        \b
        # Generate repository context (markdown format)
        agentready repomix-generate

        \b
        # Generate with XML format
        agentready repomix-generate --format xml

        \b
        # Check if output is fresh
        agentready repomix-generate --check
    """
    repo_path = Path(repository).resolve()

    # Validate git repository
    if not (repo_path / ".git").exists():
        click.echo("Error: Not a git repository", err=True)
        sys.exit(1)

    service = RepomixService(repo_path)

    # Check mode - just verify freshness
    if check:
        if not service.has_config():
            click.echo("❌ Repomix not configured")
            click.echo("\nRun: agentready repomix-generate --init")
            sys.exit(1)

        is_fresh, message = service.check_freshness(max_age_days=max_age)
        if is_fresh:
            click.echo(f"✅ {message}")
            output_files = service.get_output_files()
            if output_files:
                click.echo("\nOutput files:")
                for file_path in output_files:
                    click.echo(f"  • {file_path.name}")
            sys.exit(0)
        else:
            click.echo(f"❌ {message}")
            click.echo("\nRun: agentready repomix-generate")
            sys.exit(1)

    # Initialize mode - create configuration
    if init:
        click.echo("🤖 Initializing Repomix Configuration")
        click.echo("=" * 50)

        # Check if repomix is installed
        if not service.is_installed():
            click.echo("\n⚠️  Warning: Repomix is not installed")
            click.echo("Install with: npm install -g repomix")
            click.echo("\nConfiguration files will still be created.")
            click.echo()

        # Generate config
        config_created = service.generate_config(overwrite=False)
        if config_created:
            click.echo(f"✓ Created {service.config_path.name}")
        else:
            click.echo(f"• {service.config_path.name} already exists (skipped)")

        # Generate ignore file
        ignore_created = service.generate_ignore(overwrite=False)
        if ignore_created:
            click.echo(f"✓ Created {service.ignore_path.name}")
        else:
            click.echo(f"• {service.ignore_path.name} already exists (skipped)")

        click.echo("\n✅ Repomix configuration initialized!")
        click.echo("\nNext steps:")
        click.echo("  1. Review and customize repomix.config.json")
        click.echo("  2. Add custom ignore patterns to .repomixignore")
        click.echo("  3. Generate context: agentready repomix-generate")

        if not service.is_installed():
            click.echo("  4. Install Repomix: npm install -g repomix")

        return

    # Generate mode - run repomix
    if verbose:
        click.echo("🤖 Generating Repomix Repository Context")
        click.echo("=" * 50)
        click.echo(f"\nRepository: {repo_path}")
        click.echo(f"Format: {format}\n")

    # Check if configured
    if not service.has_config():
        click.echo("Error: Repomix not configured", err=True)
        click.echo("\nRun: agentready repomix-generate --init", err=True)
        sys.exit(1)

    # Check if repomix is installed
    if not service.is_installed():
        click.echo("Error: Repomix is not installed", err=True)
        click.echo("Install with: npm install -g repomix", err=True)
        sys.exit(1)

    # Run repomix
    success, message = service.run_repomix(output_format=format, verbose=verbose)

    if success:
        click.echo(f"\n✅ {message}")

        # Show freshness status
        is_fresh, freshness_msg = service.check_freshness(max_age_days=max_age)
        click.echo(f"   {freshness_msg}")
    else:
        click.echo(f"\n❌ {message}", err=True)
        sys.exit(1)
