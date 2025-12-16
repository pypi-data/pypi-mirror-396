import typer
from rich.console import Console
from pathlib import Path
from typing import Optional

from compli_ai import orchestrator, reporter

app = typer.Typer()
console = Console()

@app.command()
def init(
    path: str = typer.Argument(".", help="The path to the project directory to initialize."),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force overwrite of an existing compli.yaml file."
    )
):
    """
    Initializes a compli.yaml file in the specified project directory.
    """
    scan_path = Path(path).resolve()
    file_path = scan_path / "compli.yaml"

    if not scan_path.is_dir():
        console.print(f"[red]Error: Path '{scan_path}' is not a valid directory.[/red]")
        raise typer.Exit(code=1)

    if file_path.exists() and not force:
        console.print(
            f"[red]Error: '{file_path}' already exists.[/red] Use --force to overwrite."
        )
        raise typer.Exit(code=1)

    try:
        console.print(f"Scanning '{scan_path}' to auto-populate system components...")
        yaml_content = orchestrator.generate_compliance_file(scan_path)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
            
        console.print(f"[green]Successfully created '{file_path}'[/green]")
        console.print("Please review and complete the placeholder values.")
        
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(code=1)
        
@app.command()
def scan(
    path: str = typer.Argument(".", help="Directory to scan"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Filename to save the compliance report (e.g., report.md)."
    ),
    json_mode: bool = typer.Option(
        False, "--json", help="Output results as JSON for machine parsing"
    ),
):
    """
    Scans the directory for AI compliance data.
    """
    scan_path = Path(path)
    if not scan_path.exists():
        console.print(f"[red]Error: Path '{path}' does not exist.[/red]")
        raise typer.Exit(code=1)

    if not json_mode:
        console.print(f"[green]Scanning directory:[/green] {scan_path.resolve()}...")

    # 1. Orchestrate the scan to get results
    scan_result = orchestrator.run_scan(scan_path)

    # 2. Report the results in the desired format
    if json_mode:
        reporter.render_json(scan_result, scan_path)
    else:
        reporter.render_tables(scan_result, console, scan_path)
        if output:
            report_content = reporter.generate_markdown_report(scan_result, scan_path)
            try:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(report_content)
                console.print(f"\n[green]Report saved to {output}[/green]")
            except IOError as e:
                console.print(f"\n[red]Error saving report: {e}[/red]")

@app.command()
def version():
    """
    Prints the current version of Compli-AI.
    """
    console.print("[bold green]Compli-AI Version 0.1.0[/bold green]")

if __name__ == "__main__":
    app()