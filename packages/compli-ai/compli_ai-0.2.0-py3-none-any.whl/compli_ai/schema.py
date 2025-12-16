from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Optional
from enum import Enum

from pydantic import BaseModel, Field

# --- Analysis Data Models (from scanner) ---

@dataclass
class ModelInfo:
    """Represents a detected AI model."""
    name: str
    framework: str
    line_number: int
    file_path: Path

@dataclass
class DependencyInfo:
    """Represents a detected software dependency."""
    name: str
    line_number: int
    file_path: Path

@dataclass
class ScanError:
    """Represents an error that occurred during a file scan."""
    file_path: Path
    error: str

@dataclass
class ScanResult:
    """Represents the complete result of a codebase scan."""
    models: List[ModelInfo]
    dependencies: Set[str]
    errors: List[ScanError]
    files_scanned: int


# --- YAML Schema Models (for compli.yaml) ---

class RiskCategory(str, Enum):
    """Defines the risk categories based on the EU AI Act."""
    PROHIBITED = "prohibited"
    HIGH = "high_risk"
    LIMITED = "limited_risk"
    MINIMAL = "minimal_risk"

class ProjectMeta(BaseModel):
    """Pydantic model for project metadata."""
    name: str = Field(..., description="The name of the project.")
    version: str = Field(..., description="The version of the project.")
    author: str = Field(..., description="The author or team responsible for the project.")

class Policy(BaseModel):
    """Pydantic model for the compliance policy."""
    intended_purpose: str = Field(
        "Placeholder: Describe the intended purpose of the AI system.",
        description="The specific goal and application of the AI system."
    )
    risk_category: RiskCategory = Field(
        RiskCategory.MINIMAL,
        description="The assessed risk category under the EU AI Act."
    )

class System(BaseModel):
    """Pydantic model for the system components."""
    models: List[str] = Field(default_factory=list, description="List of AI models used or developed.")
    dependencies: List[str] = Field(default_factory=list, description="List of software dependencies.")

class Data(BaseModel):
    """Pydantic model for data handling practices."""
    description: str = Field(
        "Placeholder: Describe the data used for training, testing, and validation.",
        description="Details about data sources, collection, and preprocessing."
    )
    has_pii: bool = Field(False, description="Indicates if the data contains Personally Identifiable Information (PII).")

class ComplianceReport(BaseModel):
    """Top-level Pydantic model for the compli.yaml file."""
    project: ProjectMeta = Field(..., description="Metadata about the project.")
    policy: Policy = Field(..., description="The compliance policy for the AI system.")
    system: System = Field(..., description="The technical components of the AI system.")
    data: Data = Field(..., description="Information about the data used by the system.")

