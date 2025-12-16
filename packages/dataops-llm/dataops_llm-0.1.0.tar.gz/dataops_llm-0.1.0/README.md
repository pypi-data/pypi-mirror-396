# DataOps LLM Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**LLM-powered data operations for Excel/CSV files using natural language**

DataOps LLM Engine is a standalone Python SDK that allows you to perform arbitrary data operations on Excel/CSV files using natural language instructions. It uses Large Language Models (LLMs) to generate and execute safe Python code for data manipulation, without requiring predefined tools.

## Features

- **Natural Language Interface**: Describe what you want in plain English
- **Multi-Provider LLM Support**: Works with OpenAI, Anthropic, Google, and 100+ providers via LiteLLM
- **7-Layer Security Model**: AST validation, import whitelisting, subprocess isolation, and more
- **Flexible Input**: CSV, Excel files, or pandas DataFrames
- **Dry-Run Mode**: Preview generated code before execution
- **REST API**: Optional FastAPI wrapper for HTTP access
- **Zero Configuration**: Works out of the box with sensible defaults

## Quick Start

### Installation

```bash
pip install dataops-llm
```

Or install from source:

```bash
git clone https://github.com/yourusername/dataops-llm-engine.git
cd dataops-llm-engine
pip install -e .
```

### Basic Usage

```python
from dataops_llm import process

# Process a CSV file with natural language
result = process(
    file_path="companies.csv",
    instruction="Remove duplicates by email and normalize company names to lowercase"
)

if result.success:
    result.save("companies_cleaned.csv")
    print(result.report)
```

### Configuration

Create a `.env` file with your LLM API key:

```bash
LITELLM_API_KEY=sk-...
LITELLM_MODEL=gpt-4
```

Or pass configuration directly:

```python
result = process(
    file_path="data.csv",
    instruction="Filter rows where revenue > 1000000",
    llm_config={
        "api_key": "sk-...",
        "model": "claude-3-5-sonnet-20241022"
    }
)
```

## How It Works

```
User Instruction
    ↓
1. Intent Extraction (LLM) → Structured intent
    ↓
2. Execution Planning (LLM) → Step-by-step plan
    ↓
3. Code Generation (LLM) → Pandas code
    ↓
4. Code Validation (AST) → Security checks
    ↓
5. Sandbox Execution (subprocess) → Result
```

## Examples

### Example 1: Data Cleaning

```python
from dataops_llm import process

result = process(
    file_path="messy_data.csv",
    instruction="""
    1. Remove rows with null emails
    2. Trim whitespace from all text columns
    3. Convert dates to ISO format
    4. Remove duplicate rows based on email
    """
)
```

### Example 2: Aggregation

```python
result = process(
    file_path="sales.xlsx",
    instruction="Group by region and calculate total sales, average order value"
)
```

### Example 3: Dry-Run Mode

```python
result = process(
    file_path="data.csv",
    instruction="Filter rows where age > 25",
    dry_run=True,
    return_code=True
)

print(result.generated_code)  # See what code would be executed
```

### Example 4: Working with DataFrames

```python
import pandas as pd
from dataops_llm import process

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35]
})

result = process(
    file_path=df,
    instruction="Add a column 'age_group' categorizing ages as young/middle/senior"
)
```

## Security

DataOps LLM Engine implements a **7-layer security model** to prevent malicious code execution:

1. **LLM Prompt Engineering**: System prompts explicitly forbid dangerous operations
2. **Import Whitelisting**: Only pandas, numpy, datetime, re, math allowed
3. **AST Validation**: Parse and inspect code before execution
4. **Call Blacklisting**: Block eval, exec, open, subprocess, network calls
5. **Subprocess Isolation**: Code runs in separate process
6. **Resource Limits**: 60s timeout, 512MB memory limit
7. **File System Isolation**: Execution in temporary directory

**Allowed imports**: `pandas`, `numpy`, `datetime`, `re`, `math`

**Blocked operations**: File I/O, network access, subprocess execution, eval/exec, pickling

See [docs/security.md](docs/security.md) for detailed security documentation.

## API Reference

### `process()`

Main SDK function for processing data.

**Parameters:**
- `file_path` (str | Path | DataFrame): Input file path or DataFrame
- `instruction` (str): Natural language instruction
- `llm_config` (dict, optional): LLM configuration
  - `api_key`: LLM provider API key
  - `model`: Model name (default: "gpt-4")
  - `temperature`: Sampling temperature (default: 0.1)
  - `max_tokens`: Maximum tokens (default: 2000)
- `sandbox_config` (dict, optional): Sandbox configuration
  - `timeout`: Max execution time in seconds (default: 60)
  - `memory_limit_mb`: Max memory in MB (default: 512)
- `dry_run` (bool): Preview mode without execution (default: False)
- `return_code` (bool): Include generated code in result (default: False)

**Returns:**
- `DataOpsResult`: Result object with:
  - `success`: Whether operation succeeded
  - `dataframe`: Resulting DataFrame
  - `report`: Human-readable report
  - `generated_code`: Generated code (if requested)
  - `execution_time`: Time taken in seconds
  - `warnings`: Warning messages
  - `metadata`: Additional metadata

## REST API

Run the FastAPI server:

```bash
python -m dataops_llm.web.app
```

Or with uvicorn:

```bash
uvicorn dataops_llm.web.app:app --reload
```

API endpoints:
- `GET /` - API information
- `GET /api/v1/health` - Health check
- `POST /api/v1/process` - Process data

Example request:

```python
import requests
import base64

with open("data.csv", "rb") as f:
    file_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:8000/api/v1/process",
    json={
        "instruction": "Remove duplicates",
        "file_base64": file_base64,
        "file_format": "csv"
    }
)

result = response.json()
```

## Configuration Options

### Environment Variables

```bash
# LLM Configuration
LITELLM_API_KEY=sk-...
LITELLM_MODEL=gpt-4
LITELLM_TEMPERATURE=0.1
LITELLM_MAX_TOKENS=2000

# Sandbox Configuration
SANDBOX_TIMEOUT=60
SANDBOX_MEMORY_MB=512

# Application
APP_LOG_LEVEL=INFO
```

See `.env.example` for all options.

## Supported LLM Providers

Via LiteLLM, supports 100+ providers:

- **OpenAI**: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **Anthropic**: claude-3-5-sonnet, claude-3-opus
- **Google**: gemini-pro, gemini-ultra
- **Azure OpenAI**: All OpenAI models via Azure
- **AWS Bedrock**: Claude, Llama, etc.
- **And many more...**

## Limitations

- **File Size**: Max 1M rows × 1K columns (configurable)
- **Execution Time**: Max 60 seconds (configurable)
- **Memory**: Max 512MB (configurable)
- **Operations**: Only pandas-compatible operations
- **No**: File I/O, network access, subprocess execution

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/dataops-llm-engine.git
cd dataops-llm-engine

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dataops_llm

# Run security tests only
pytest tests/test_sandbox/test_security.py
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Citation

If you use this project in your research, please cite:

```bibtex
@software{dataops_llm_engine,
  title={DataOps LLM Engine: Natural Language Data Operations},
  author={Islam Abd-Elhady},
  year={2025},
  url={https://github.com/yourusername/dataops-llm-engine}
}
```

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/dataops-llm-engine/issues)
- **Security**: For security concerns, email security@yourdomain.com

## Acknowledgments

- Built with [LiteLLM](https://github.com/BerriAI/litellm) for multi-provider LLM support
- Uses [pandas](https://pandas.pydata.org/) for data manipulation
- Powered by [FastAPI](https://fastapi.tiangolo.com/) for REST API

## Roadmap

- [ ] Multi-step workflow chaining
- [ ] SQL database support
- [ ] Custom function definitions
- [ ] Operation history and rollback
- [ ] Web UI for non-developers
- [ ] Docker-based sandbox option
- [ ] Response caching
- [ ] Streaming progress updates
