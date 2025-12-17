# Development Guide

This guide is for developers who want to contribute to or modify the Shai Hulud Detector package.

## Requirements

- Python 3.11+
- uv package manager (https://docs.astral.sh/uv/)
- GitHub Personal Access Token (https://github.com/settings/tokens)

## Setup

### Clone the repository

```bash
git clone https://github.com/ysskrishna/shai-hulud-detector.git
cd shai-hulud-detector
```

### Install dependencies

```bash
uv sync
```

### Authentication Options

Environment variable (recommended):

```bash
export GITHUB_TOKEN=<GITHUB_TOKEN_HERE>
uv run python main.py scan <USERNAME_HERE>
```

Command-line flag:
```bash
uv run python main.py scan <USERNAME_HERE> --token <GITHUB_TOKEN_HERE>
```

If omitted, the tool exits with a clear warning.

## Development Usage

### Run the tool during development

```bash
uv run python main.py scan <USERNAME_HERE>
uv run python main.py scan <USERNAME_HERE1> <USERNAME_HERE2> <USERNAME_HERE3>
```

### Scan all members of an organization

```bash
uv run python main.py scan --org <ORGANIZATION_NAME_HERE>
```

### Help
```bash
uv run python main.py scan --help 
``` 

### Parallelism

Set concurrency (default 5):
```bash
uv run python main.py scan --org <ORGANIZATION_NAME_HERE> --workers 10
```

### Verbose Output
```bash
uv run python main.py scan <USERNAME_HERE> --verbose
```

