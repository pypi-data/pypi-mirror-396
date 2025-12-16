import os
import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from rich import print
from typing import Optional
from datetime import datetime

from compli_ai.inspector import analyze_imports, detect_models, ModelInfo

app = typer.Typer()
console = Console()

@app.command()
def scan(path: str = typer.Argument(".", help="Directory to scan"), output: Optional[str] = typer.Option(None, "--output", "-o", help="Filename to save the compliance report (e.g., report.md).")):
    """
    Scans the directory for AI compliance data.
    """
    scan_path = Path(path)
    if not scan_path.exists():
        console.print(f"[red]Error: Path '{path}' does not exist.[/red]")
        raise typer.Exit(code=1)

    console.print(f"[green]Scanning directory:[/green] {scan_path.resolve()}...")

    all_libraries = set()
    all_models: list[tuple[Path, ModelInfo]] = []
    py_files_count = 0

    for root, _, files in os.walk(scan_path):
        for file in files:
            if file.endswith(".py"):
                py_files_count += 1
                file_path = Path(root) / file
                
                libs = analyze_imports(str(file_path))
                all_libraries.update(libs)
                
                models = detect_models(str(file_path))
                for model in models:
                    all_models.append((file_path, model))

    console.print(f"Scan complete. Found {py_files_count} Python file(s).")
    console.print()

    # Display Libraries Table
    if all_libraries:
        lib_table = Table(title="Detected Python Libraries")
        lib_table.add_column("Library", style="cyan")
        for lib in sorted(list(all_libraries)):
            lib_table.add_row(lib)
        console.print(lib_table)
    else:
        console.print("[yellow]No Python libraries detected.[/yellow]")
    
    console.print()

    # Display Models Table
    if all_models:
        model_table = Table(title="Detected AI Models")
        model_table.add_column("File", style="yellow")
        model_table.add_column("Line", style="magenta")
        model_table.add_column("Model Name/Class", style="cyan")
        model_table.add_column("Framework", style="green")
        
        for file_path, model in all_models:
            relative_path = file_path.relative_to(scan_path) if file_path.is_relative_to(scan_path) else file_path
            model_table.add_row(
                str(relative_path),
                str(model.line_number),
                model.name,
                model.framework
            )
        console.print(model_table)
    else:
        console.print("[yellow]No AI models detected.[/yellow]")

    # Generate and save report if output path is provided
    if output:
        report_content = generate_markdown_report(all_models, all_libraries, scan_path)
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(report_content)
            console.print(f"\n[green]Report saved to {output}[/green]")
        except IOError as e:
            console.print(f"\n[red]Error saving report: {e}[/red]")

def generate_markdown_report(models: list[tuple[Path, ModelInfo]], libraries: set[str], scan_path: Path) -> str:
    """Generates a Markdown formatted report string."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = ["# EU AI Act - Technical Compliance Snapshot", f"Report generated on: {now}\n"]

    report.append("## 1. Identified AI Models")
    if not models:
        report.append("No AI models detected.")
    else:
        report.append("| File | Line | Model Name/Class | Framework |")
        report.append("|------|------|------------------|-----------|")
        for file_path, model in models:
            relative_path = file_path.relative_to(scan_path) if file_path.is_relative_to(scan_path) else file_path
            report.append(f"| {relative_path} | {model.line_number} | {model.name} | {model.framework} |")
    
    report.append("\n## 2. Software Dependencies")
    if not libraries:
        report.append("No software dependencies detected.")
    else:
        for lib in sorted(list(libraries)):
            report.append(f"- `{lib}`")
            
    return "\n".join(report)

@app.command()
def version():
    """
    Prints the current version of Compli-AI.
    """
    print("[bold green]Compli-AI Version 0.1.0[/bold green]")


if __name__ == "__main__":
    app()