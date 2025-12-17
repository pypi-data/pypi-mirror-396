# Clappia API Tools

**Clappia APIs SDK**

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/clappia-api-tools)](https://pypi.org/project/clappia-api-tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

Clappia API Tools is a Python package that provides a set of clients for seamless integration with the [Clappia API](https://developer.clappia.com/). It enables developers to automate workflows, manage submissions, and interact with Clappia apps programmatically. The package is designed for use in automation, data integration, and agent-based systems (e.g., LangChain agents, MCP).

---

## Features

-  **Multiple API Clients**: Dedicated clients for each Clappia API operation.
-  **Submission Management**: Create, edit, update owners, and change status of submissions.
-  **App Definition Retrieval**: Fetch complete app structure and metadata and manage the app structure via fields and sections updates.
-  **Workflow Management**: Retrieve, create, modify, and manage workflow definitions and steps.
-  **Analytics Management**: Add, update, and reorder charts and analytics configurations.

---

## Available Clients

-  `SubmissionClient`: Manage submissions (create, edit, update owners, change status)
-  `AppDefinitionClient`: Retrieve app definitions and metadata and Manage app structure (fields, sections, creation)
-  `WorkflowDefinitionClient`: Manage workflow definitions (get, add, update, reorder workflow steps)
-  `AnalyticsClient`: Manage analytics and charts (add, update, reorder charts)

---

## Documentation

-  [Submission Client Reference](docs/submission_client.md)
-  [App Definition Client Reference](docs/app_definition_client.md)
-  [Workflow Definition Client Reference](docs/workflow_definition_client.md)
-  [Analytics Client Reference](docs/analytics_client.md)
-  [Setup, Testing, and Publish Reference](docs/setup_testing_publishing.md)

---

## Installation

```bash
pip install clappia-api-tools
```

Or, for development:

```bash
git clone https://github.com/clappia-dev/clappia-api-tools.git
cd clappia-api-tools
pip install -e ."[dev]"
```

---

## Configuration

You must provide your Clappia API credentials and workspace information directly when initializing any client:

-  `api_key`: Your Clappia API key
-  `base_url`: The base URL for the Clappia API (e.g., `https://api.clappia.com`)

---

## Usage

### SubmissionClient Example

```python
from clappia_api_tools.client.submission_client import SubmissionClient

client = SubmissionClient(
    api_key="your-api-key",
    base_url="https://api.clappia.com",
)

# Create a submission
result = client.create_submission(
    app_id="MFX093412",
    data={"employee_name": "John Doe", "department": "Engineering"},
)
print(result)
```

### AppDefinitionClient Example

```python
from clappia_api_tools.client.app_definition_client import AppDefinitionClient

client = AppDefinitionClient(
    api_key="your-api-key",
    base_url="https://api.clappia.com",
)

# Get app definition
result = client.get_definition(app_id="MFX093412")
print(result)
```

### WorkflowDefinitionClient Example

```python
from clappia_api_tools.client.workflow_definition_client import WorkflowDefinitionClient

client = WorkflowDefinitionClient(
    api_key="your-api-key",
    base_url="https://api.clappia.com",
)

# Get workflow definition
result = client.get_workflow(
    app_id="MFX093412",
    trigger_type="submissionCreated",
)
print(result)

# Add a workflow step
add_result = client.add_step(
    app_id="MFX093412",
    trigger_type="submissionCreated",
    node_type="Email",
)
print(add_result)
```

### AnalyticsClient Example

```python
from clappia_api_tools.client.analytics_client import AnalyticsClient

client = AnalyticsClient(
    api_key="your-api-key",
    base_url="https://api.clappia.com",
)

# Add a chart
result = client.add_chart(
    app_id="MFX093412",
    chart_type="Bar",
    chart_title="Sales Overview"
)
print(result)

# Update chart configuration
update_data = {
    "chart_title": "Updated Sales Overview",
    "dimensions": ["region"],
    "metrics": ["sales_amount"]
}
update_result = client.update_chart(
    app_id="MFX093412",
    chart_index=0,
    update_data=update_data
)
print(update_result)
```

---

## Contributing

1. Fork the repository and create your branch.
2. Write clear, well-documented code and tests.
3. Run `pytest` and ensure all tests pass.
4. Submit a pull request with a clear description of your changes.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
