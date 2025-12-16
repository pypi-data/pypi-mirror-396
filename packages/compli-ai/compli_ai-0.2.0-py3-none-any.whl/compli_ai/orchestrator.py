import os
import yaml
import tomli
from pathlib import Path
from typing import List
from enum import Enum

from compli_ai.inspector import analyze_imports, detect_models
from compli_ai.schema import ScanResult, ModelInfo, ScanError, ComplianceReport, ProjectMeta, Policy, System, Data, RiskCategory

# Custom Dumper to handle Enums as strings
class EnumDumper(yaml.Dumper):
    def represent_data(self, data):
        if isinstance(data, Enum):
            return self.represent_str(data.value)
        return super().represent_data(data)

def get_project_version(scan_path: Path) -> str:
    """Reads the project version from pyproject.toml."""
    try:
        pyproject_path = scan_path / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
        return data["tool"]["poetry"]["version"]
    except (FileNotFoundError, KeyError):
        return "0.0.0" # Default if not found

def generate_compliance_file(scan_path: Path) -> str:
    """
    Performs a scan, populates the compliance model, and returns the YAML string.
    """
    # 1. Perform a standard scan
    scan_result = run_scan(scan_path)
    project_version = get_project_version(scan_path)

    # 2. Populate the Pydantic model
    report = ComplianceReport(
        project=ProjectMeta(
            name=scan_path.name,
            version=project_version,
            author="My Team <email@example.com>"
        ),
        policy=Policy(
            intended_purpose="DESCRIBE_INTENDED_PURPOSE_HERE",
            risk_category=RiskCategory.MINIMAL
        ),
        system=System(
            models=sorted([model.name for model in scan_result.models]),
            dependencies=sorted(list(scan_result.dependencies))
        ),
        data=Data(
            description="Placeholder: Describe the data used for training, testing, and validation.",
            has_pii=False
        )
    )

    # 3. Serialize to YAML string using the custom dumper
    yaml_string = yaml.dump(
        report.model_dump(),
        Dumper=EnumDumper,
        sort_keys=False,
        indent=2,
        width=80
    )
    
    # 4. Add comments to the YAML string
    commented_yaml = add_comments_to_yaml(yaml_string)
    
    return commented_yaml

def add_comments_to_yaml(yaml_string: str) -> str:
    """
    A helper function to add descriptive comments to the YAML string.
    This is a workaround as PyYAML does not support comment preservation.
    """
    lines = yaml_string.split('\n')
    commented_lines = []
    for line in lines:
        if "project:" in line:
            commented_lines.append("# Metadata about the project.")
        elif "policy:" in line:
            commented_lines.append("\n# Policy declarations required for EU AI Act compliance.")
        elif "intended_purpose:" in line:
            commented_lines.append("  # Intended Purpose (EU AI Act, Annex IV): A clear, specific description of the system's intended use.")
        elif "risk_category:" in line:
            commented_lines.append("  # Risk Category (EU AI Act, Title III): The assessed risk level. Options: prohibited, high_risk, limited_risk, minimal_risk")
        elif "system:" in line:
            commented_lines.append("\n# The technical components of the AI system, auto-detected from the codebase.")
        elif "data:" in line:
            commented_lines.append("\n# Information about the data used by the system.")
        commented_lines.append(line)
    return "\n".join(commented_lines)

def run_scan(path: Path) -> ScanResult:
    """
    Scans a directory, analyzes files, and returns aggregated results.
    """
    all_models: List[ModelInfo] = []
    all_libraries: set[str] = set()
    errors: List[ScanError] = []
    py_files_count = 0

    for root, _, files in os.walk(path):
        for file in files:
            if not file.endswith(".py"):
                continue

            py_files_count += 1
            file_path = Path(root) / file
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                libs = analyze_imports(content, file_path)
                all_libraries.update(libs)
                
                models = detect_models(content, file_path)
                all_models.extend(models)

            except (IOError, UnicodeDecodeError, SyntaxError) as e:
                errors.append(ScanError(file_path=file_path, error=str(e)))
            except Exception as e:
                errors.append(ScanError(file_path=file_path, error=f"An unexpected error occurred: {e}"))

    return ScanResult(
        models=all_models,
        dependencies=all_libraries,
        errors=errors,
        files_scanned=py_files_count,
    )
