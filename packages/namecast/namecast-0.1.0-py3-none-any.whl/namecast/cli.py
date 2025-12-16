"""Command-line interface for Namecast."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from namecast.evaluator import BrandEvaluator, NamecastWorkflow
from namecast.perception import analyze_two_pass


console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Namecast - AI-powered brand name intelligence.

    Generate, filter, and evaluate brand names with AI.

    Commands:

        namecast find "Your project description" - Generate and evaluate names

        namecast eval Acme - Evaluate a single name

        namecast eval --compare Acme Globex - Compare multiple names
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("description")
@click.option("--ideas", "-i", multiple=True, help="Your name ideas (can specify multiple)")
@click.option("--generate", "-g", default=10, help="Number of AI names to generate")
@click.option("--evaluate", "-e", default=5, help="Max names to fully evaluate")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def find(description: str, ideas: tuple[str, ...], generate: int, evaluate: int, output_json: bool):
    """Generate and evaluate brand names for your project.

    Examples:

        namecast find "A SaaS tool for tracking carbon emissions"

        namecast find "Dog walking app" --ideas Waggle --ideas PupPath

        namecast find "AI coding assistant" -g 15 -e 8
    """
    workflow = NamecastWorkflow()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Running naming workflow...", total=None)
        result = workflow.run(
            project_description=description,
            user_name_ideas=list(ideas) if ideas else None,
            generate_count=generate,
            max_to_evaluate=evaluate,
        )

    if output_json:
        click.echo(result.to_json())
    else:
        _print_workflow_result(result)


@main.command()
@click.argument("names", nargs=-1, required=True)
@click.option("--mission", "-m", help="Company mission for alignment scoring")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--compare", is_flag=True, help="Compare multiple names side-by-side")
def eval(names: tuple[str, ...], mission: str | None, output_json: bool, compare: bool):
    """Evaluate specific brand names.

    Examples:

        namecast eval Acme

        namecast eval Acme --mission "Industrial supply company"

        namecast eval --compare Acme Globex Initech
    """
    evaluator = BrandEvaluator()

    if compare and len(names) > 1:
        results = [evaluator.evaluate(name, mission) for name in names]
        if output_json:
            import json
            click.echo(json.dumps([r.to_dict() for r in results], indent=2, default=str))
        else:
            _print_comparison(results)
    else:
        for name in names:
            result = evaluator.evaluate(name, mission)
            if output_json:
                click.echo(result.to_json())
            else:
                _print_result(result, mission)


@main.command()
@click.argument("name")
@click.argument("product_description")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def comport(name: str, product_description: str, output_json: bool):
    """Two-pass evaluation: Does the product comport with the name?

    This runs a two-pass test:
    1. "What would you expect a company named {NAME} to do?"
    2. "{NAME} does {PRODUCT}. Does that comport?"

    The delta between expectation and reality reveals whether
    name-product mismatches are intentional (like Mailchimp) or jarring.

    Examples:

        namecast comport EggNest "simulates personal finance with real tax models"

        namecast comport Stripe "processes online payments"
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Running two-pass evaluation...", total=None)
        result = analyze_two_pass(name, product_description)

    if output_json:
        import json
        from dataclasses import asdict
        click.echo(json.dumps(asdict(result), indent=2, default=str))
    else:
        _print_comport_result(result)


def _print_comport_result(result):
    """Print the two-pass comport analysis."""
    console.print()

    # Verdict panel with color based on result
    verdict_colors = {
        "strong_fit": "green",
        "positive_contrast": "blue",
        "neutral": "yellow",
        "jarring_mismatch": "red",
    }
    color = verdict_colors.get(result.verdict, "white")

    console.print(Panel(
        f"[bold {color}]{result.verdict.upper().replace('_', ' ')}[/bold {color}]\n\n"
        f"{result.verdict_explanation}",
        title=f"[bold]{result.name}[/bold]",
        subtitle=f"Comport Score: {result.avg_comport_score:.1f}/10",
    ))

    # Key metrics
    console.print()
    metrics_table = Table(title="Two-Pass Metrics", show_header=True)
    metrics_table.add_column("Metric")
    metrics_table.add_column("Value", justify="right")

    metrics_table.add_row("Comport Rate", f"{result.comport_rate*100:.0f}%")
    metrics_table.add_row("Positive Surprise Rate", f"{result.positive_surprise_rate*100:.0f}%")
    metrics_table.add_row("Contrast Works Rate", f"{result.contrast_works_rate*100:.0f}%")

    trust_delta_str = f"+{result.trust_delta*100:.0f}%" if result.trust_delta >= 0 else f"{result.trust_delta*100:.0f}%"
    trust_color = "green" if result.trust_delta > 0 else "red" if result.trust_delta < 0 else "white"
    metrics_table.add_row("Trust Delta", f"[{trust_color}]{trust_delta_str}[/{trust_color}]")

    console.print(metrics_table)

    # Individual persona responses
    console.print()
    console.print("[bold]Persona Responses:[/bold]")
    console.print()

    for r in result.responses:
        reaction_emoji = {
            "positive_surprise": "😮",
            "matches": "✓",
            "neutral": "—",
            "jarring_mismatch": "❌",
        }.get(r.reaction, "?")

        trust_change = ""
        if r.initial_trust != r.final_trust:
            trust_change = " [green]↑ trust[/green]" if r.final_trust else " [red]↓ trust[/red]"

        console.print(f"  [bold]{r.persona}[/bold] ({r.age}, {r.occupation})")
        console.print(f"    Expected: {r.expected_product}")
        console.print(f"    Reaction: {reaction_emoji} {r.reaction.replace('_', ' ')} (comport: {r.comport_score}/10){trust_change}")
        if r.reaction != "matches" and r.contrast_works:
            console.print(f"    [dim]→ Says the contrast works intentionally[/dim]")
        console.print(f"    [dim]{r.explanation}[/dim]")
        console.print()

    console.print()


def _print_workflow_result(result):
    """Print the workflow result with rich formatting."""
    console.print()
    console.print(Panel(
        f"[dim]{result.project_description}[/dim]",
        title="[bold]Namecast Workflow Results[/bold]",
    ))

    # Summary stats
    console.print()
    console.print(f"[bold]Candidates:[/bold] {len(result.all_candidates)} total → "
                  f"{len(result.viable_candidates)} passed domain filter → "
                  f"{len(result.evaluated_candidates)} fully evaluated")

    # Rejected candidates
    rejected = [c for c in result.all_candidates if not c.passed_domain_filter]
    if rejected:
        console.print()
        console.print("[dim]Filtered out (no .com or .io available):[/dim]")
        for c in rejected[:5]:  # Show first 5
            console.print(f"  [dim]✗ {c.name}[/dim]")
        if len(rejected) > 5:
            console.print(f"  [dim]... and {len(rejected) - 5} more[/dim]")

    # Evaluated candidates table
    if result.evaluated_candidates:
        console.print()
        table = Table(title="Evaluated Names", show_header=True)
        table.add_column("Rank")
        table.add_column("Name")
        table.add_column("Source")
        table.add_column("Score", justify="right")
        table.add_column(".com")
        table.add_column(".io")

        # Sort by score
        sorted_candidates = sorted(
            result.evaluated_candidates,
            key=lambda c: c.evaluation.overall_score if c.evaluation else 0,
            reverse=True
        )

        for i, c in enumerate(sorted_candidates, 1):
            score = c.evaluation.overall_score if c.evaluation else 0
            score_color = "green" if score >= 70 else "yellow" if score >= 50 else "red"
            com_status = "[green]✓[/green]" if c.domains_available.get(".com") else "[red]✗[/red]"
            io_status = "[green]✓[/green]" if c.domains_available.get(".io") else "[red]✗[/red]"

            is_recommended = result.recommended and c.name == result.recommended.name
            rank = f"[bold gold1]★ {i}[/bold gold1]" if is_recommended else str(i)

            table.add_row(
                rank,
                f"[bold]{c.name}[/bold]" if is_recommended else c.name,
                c.source,
                f"[{score_color}]{score:.0f}[/{score_color}]",
                com_status,
                io_status,
            )

        console.print(table)

    # Recommendation
    if result.recommended and result.recommended.evaluation:
        console.print()
        rec = result.recommended
        console.print(Panel(
            f"[bold]{rec.name}[/bold] - Score: {rec.evaluation.overall_score:.0f}/100\n\n"
            f"[dim]This tool provides general information only and does not constitute legal advice.[/dim]",
            title="[bold gold1]★ Recommended[/bold gold1]",
            border_style="gold1",
        ))

    console.print()


def _print_result(result, mission: str | None):
    """Print a single evaluation result with rich formatting."""
    # Header
    score_color = "green" if result.overall_score >= 70 else "yellow" if result.overall_score >= 50 else "red"
    console.print()
    console.print(Panel(
        Text(f"{result.overall_score:.0f}/100", style=f"bold {score_color}", justify="center"),
        title=f"[bold]{result.name}[/bold]",
        subtitle="Overall Score",
    ))

    # Domain table
    domain_table = Table(title="Domain Availability", show_header=True)
    domain_table.add_column("TLD")
    domain_table.add_column("Status")
    for tld, available in result.domains.items():
        status = "[green]Available[/green]" if available else "[red]Taken[/red]"
        domain_table.add_row(tld, status)
    console.print(domain_table)

    # Social table
    social_table = Table(title="Social Handles", show_header=True)
    social_table.add_column("Platform")
    social_table.add_column("Status")
    for platform, available in result.social.items():
        status = "[green]Available[/green]" if available else "[red]Taken[/red]"
        social_table.add_row(platform, status)
    console.print(social_table)

    # Pronunciation
    if result.pronunciation:
        console.print(f"\n[bold]Pronunciation:[/bold] {result.pronunciation.score:.1f}/10")
        console.print(f"  Syllables: {result.pronunciation.syllables}")
        console.print(f"  Spelling: {result.pronunciation.spelling_difficulty}")

    # International
    issues = [lang for lang, data in result.international.items() if data.get("has_issue")]
    if issues:
        console.print("\n[bold yellow]International Issues:[/bold yellow]")
        for lang in issues:
            meaning = result.international[lang].get("meaning", "unknown issue")
            console.print(f"  {lang}: {meaning}")
    else:
        console.print("\n[bold green]International Check:[/bold green] No issues found")

    # Mission alignment
    if mission and result.perception and result.perception.mission_alignment:
        console.print(f"\n[bold]Mission Alignment:[/bold] {result.perception.mission_alignment:.1f}/10")

    console.print()


def _print_comparison(results):
    """Print side-by-side comparison of multiple names."""
    console.print()
    console.print("[bold]Comparison[/bold]")
    console.print()

    table = Table(show_header=True)
    table.add_column("Criteria")
    for r in results:
        table.add_column(r.name, justify="center")

    table.add_row("Overall", *[f"{r.overall_score:.0f}" for r in results])
    table.add_row("Domain", *[f"{r.domain_score:.0f}" for r in results])
    table.add_row("Social", *[f"{r.social_score:.0f}" for r in results])
    table.add_row("Similar Companies", *[f"{r.similar_companies_score:.0f}" for r in results])
    table.add_row("Pronunciation", *[f"{r.pronunciation_score:.0f}" for r in results])
    table.add_row("International", *[f"{r.international_score:.0f}" for r in results])

    console.print(table)

    # Winner
    winner = max(results, key=lambda r: r.overall_score)
    console.print(f"\n[bold green]Winner: {winner.name}[/bold green] ({winner.overall_score:.0f}/100)")
    console.print()


if __name__ == "__main__":
    main()
