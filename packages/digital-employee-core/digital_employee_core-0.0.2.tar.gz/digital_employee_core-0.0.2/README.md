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
```

## Configuration Management

### Understanding MCP Configuration Placeholders

The library uses YAML configuration templates (`digital_employee_core/config_templates/mcp_configs.yaml` and `tool_configs.yaml`) that contain **placeholder keys** in angle brackets (e.g., `<GOOGLE_CALENDAR_MCP_URL>`). These placeholders need to be replaced with actual values at runtime.

**How Placeholders Work:**

1. **Configuration Template** (in `mcp_configs.yaml`):
```yaml
digital_employee_google_calendar_mcp:
  config:
    url: <GOOGLE_CALENDAR_MCP_URL>
  authentication:
    type: api-key
    key: X-API-Key
    value: <GOOGLE_MCP_X_API_KEY>
```

2. **Supply Values** using `DigitalEmployeeConfiguration`:
```python
from digital_employee_core import DigitalEmployeeConfiguration

configurations = [
    DigitalEmployeeConfiguration(
        key="GOOGLE_CALENDAR_MCP_URL",
        value="https://api.example.com/calendar/mcp"
    ),
    DigitalEmployeeConfiguration(
        key="GOOGLE_MCP_X_API_KEY",
        value="your-secret-api-key"
    ),
]
```

3. **Pass to Digital Employee**:
```python
from digital_employee_core import DigitalEmployee
from digital_employee_core.connectors.mcps import google_calendar_mcp

de = DigitalEmployee(
    identity=identity,
    mcps=[google_calendar_mcp],
    configurations=configurations  # Placeholder values will be replaced automatically
)

de.deploy()
```

### Available Placeholder Keys

Refer to `digital_employee_core/config_templates/mcp_configs.yaml` and `tool_configs.yaml` to see all available placeholders. Common ones include:

**Google MCPs:**
- `GOOGLE_CALENDAR_MCP_URL`
- `GOOGLE_DOCS_MCP_URL`
- `GOOGLE_DRIVE_MCP_URL`
- `GOOGLE_MAIL_MCP_URL`
- `GOOGLE_SHEETS_MCP_URL`
- `GOOGLE_MCP_X_API_KEY`

**GitHub MCP:**
- `GITHUB_MCP_URL`
- `GITHUB_MCP_X_API_KEY`

**SQL Tool MCP:**
- `SQL_TOOL_MCP_URL`
- `SQL_AUTH_TOKEN`
- `SQL_API_KEY`
- `SQL_IDENTIFIER`

### Configuration Priority

Configurations can be supplied in three ways:

1. **At Initialization** (applied during `deploy()`):
```python
de = DigitalEmployee(
    identity=identity,
    mcps=[google_calendar_mcp],
    configurations=configurations
)
```

2. **At Runtime** (applied per `run()` call):
```python
response = de.run(
    message="Check my calendar",
    configurations=runtime_configurations
)
```

3. **Combined** (initialization configs + runtime configs are merged):
```python
# Initialization configs for persistent settings
de = DigitalEmployee(
    identity=identity,
    configurations=base_configurations
)
de.deploy()

# Runtime configs for per-request overrides
response = de.run(
    message="Send email",
    configurations=request_specific_configurations
)
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
