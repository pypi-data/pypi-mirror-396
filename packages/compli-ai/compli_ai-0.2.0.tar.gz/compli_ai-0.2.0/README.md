# Compli-AI: The Terraform for EU AI Compliance

Compli-AI is a command-line tool that scans your Python codebase to automatically identify AI models and software dependencies, generating technical documentation required for EU AI Act compliance.

## Installation

```bash
pip install compli-ai
```

## Usage

Scan the current directory and view results in your terminal:
```bash
compli-ai scan
```

Scan a specific path and export the report to a Markdown file:
```bash
compli-ai scan ./my_project --output report.md
```

## Supported Frameworks

Compli-AI can currently detect models and components from the following frameworks:

- **Hugging Face** (`transformers`)
- **PyTorch** (`torch.nn.Module`)