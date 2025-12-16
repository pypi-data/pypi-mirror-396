"""
Handles the reporting of scan results in various formats.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

from compli_ai.schema import ScanResult, ModelInfo

def render_json(result: ScanResult, scan_path: Path) -> None:
    """Prints scan results as a JSON object to stdout."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "files_scanned": result.files_scanned,
        "dependencies": [
            {"name": lib, "risk": "unknown"} for lib in sorted(list(result.dependencies))
        ],
        "models": [
            {
                "file": str(model.file_path.relative_to(scan_path)),
                "line": model.line_number,
                "model_name": model.name,
                "framework": model.framework,
            }
            for model in result.models
        ],
        "errors": [
            {
                "file": str(err.file_path.relative_to(scan_path)),
                "error": err.error
            }
            for err in result.errors
        ]
    }
    print(json.dumps(output, indent=2))

def render_tables(result: ScanResult, console: Console, scan_path: Path) -> None:
    """Renders scan results as rich tables to the console."""
    console.print(f"Scan complete. Found {result.files_scanned} Python file(s).")
    console.print()

    # Display Libraries Table
    if result.dependencies:
        lib_table = Table(title="Detected Python Libraries")
        lib_table.add_column("Library", style="cyan")
        for lib in sorted(list(result.dependencies)):
            lib_table.add_row(lib)
        console.print(lib_table)
    else:
        console.print("[yellow]No Python libraries detected.[/yellow]")
    
    console.print()

    # Display Models Table
    if result.models:
        model_table = Table(title="Detected AI Models")
        model_table.add_column("File", style="yellow")
        model_table.add_column("Line", style="magenta")
        model_table.add_column("Model Name/Class", style="cyan")
        model_table.add_column("Framework", style="green")
        
        for model in result.models:
            relative_path = model.file_path.relative_to(scan_path)
            model_table.add_row(
                str(relative_path),
                str(model.line_number),
                model.name,
                model.framework
            )
        console.print(model_table)
    else:
        console.print("[yellow]No AI models detected.[/yellow]")

    # Display Errors Table
    if result.errors:
        console.print()
        error_table = Table(title="[red]Errors Encountered During Scan[/red]")
        error_table.add_column("File", style="yellow")
        error_table.add_column("Error", style="red")
        for err in result.errors:
            error_table.add_row(str(err.file_path.relative_to(scan_path)), err.error)

def generate_markdown_report(result: ScanResult, scan_path: Path) -> str:
    """Generates a Markdown formatted report string."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_lines = ["# EU AI Act - Technical Compliance Snapshot", f"Report generated on: {now}\n"]

    report_lines.append("## 1. Identified AI Models")
    if not result.models:
        report_lines.append("No AI models detected.")
    else:
        report_lines.append("| File | Line | Model Name/Class | Framework |")
        report_lines.append("|------|------|------------------|-----------|")
        for model in result.models:
            relative_path = model.file_path.relative_to(scan_path)
            report_lines.append(f"| {relative_path} | {model.line_number} | {model.name} | {model.framework} |")
    
    report_lines.append("\n## 2. Software Dependencies")
    if not result.dependencies:
        report_lines.append("No software dependencies detected.")
    else:
        for lib in sorted(list(result.dependencies)):
            report_lines.append(f"- `{lib}`")
            
    if result.errors:
        report_lines.append("\n## 3. Scan Errors")
        report_lines.append("The following files could not be scanned successfully:")
        for err in result.errors:
            report_lines.append(f"- **{err.file_path.relative_to(scan_path)}**: `{err.error}`")
            
    return "\n".join(report_lines)
