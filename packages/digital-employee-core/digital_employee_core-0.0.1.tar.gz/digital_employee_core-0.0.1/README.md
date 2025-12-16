# Digital Employee Core

A Python library for building and managing AI-powered digital employees with support for tools, MCPs (Model Context Protocol), and flexible configuration management.

## Setup

### 1. Install Dependencies

```bash
poetry install
```

### 2. Configure Environment

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Required
AIP_API_URL=https://your-ai-platform-url.com
AIP_API_KEY=your-api-key

# Optional: Google MCP Configuration
GOOGLE_CALENDAR_MCP_URL=https://api.example.com/calendar/mcp
GOOGLE_DOCS_MCP_URL=https://api.example.com/docs/mcp
GOOGLE_MCP_X_API_KEY=your-google-mcp-key
```

## Run Examples

### Basic Usage

```bash
poetry run python examples/basic_usage.py
```

### Configuration Usage

```bash
poetry run python examples/configuration_usage.py
```

### Subclass Example

```bash
poetry run python examples/subclass_example.py
```

## Run Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run coverage run -m pytest
poetry run coverage report

# Run with coverage HTML report
poetry run coverage run -m pytest
poetry run coverage html
# Open htmlcov/index.html in browser

# Run specific test file
poetry run pytest tests/digital_employee/test_digital_employee.py
```
