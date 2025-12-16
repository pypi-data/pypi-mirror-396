import ast
import sys
from dataclasses import dataclass

@dataclass
class ModelInfo:
    name: str
    framework: str
    line_number: int

def analyze_imports(file_path: str) -> set[str]:
    """
    Parses a Python file and extracts top-level imported module names.
    """
    libraries = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=file_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level = alias.name.split('.')[0]
                    libraries.add(top_level)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    continue
                if node.module:
                    top_level = node.module.split('.')[0]
                    libraries.add(top_level)
    except Exception:
        return set()
    return libraries

def detect_models(file_path: str) -> list[ModelInfo]:
    """
    Detects AI models in a Python file.
    """
    models = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=file_path)

        for node in ast.walk(tree):
            # Detect Hugging Face models: x = AutoModel.from_pretrained('name')
            if (isinstance(node, ast.Assign) and
                    isinstance(node.value, ast.Call) and
                    isinstance(node.value.func, ast.Attribute) and
                    node.value.func.attr == 'from_pretrained' and
                    node.value.args and
                    isinstance(node.value.args[0], ast.Constant)):
                model_name = node.value.args[0].value
                models.append(ModelInfo(name=model_name, framework="Hugging Face", line_number=node.lineno))

            # Detect PyTorch models: class MyModel(torch.nn.Module)
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if (isinstance(base, ast.Attribute) and
                        isinstance(base.value, ast.Attribute) and
                        base.value.value.id == 'torch' and
                        base.value.attr == 'nn' and
                        base.attr == 'Module'):
                        models.append(ModelInfo(name=node.name, framework="PyTorch", line_number=node.lineno))

    except Exception:
        return []
    return models
