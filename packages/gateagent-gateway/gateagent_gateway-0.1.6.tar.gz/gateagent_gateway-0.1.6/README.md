# Gateagent

The Gateway for your Agents. It acts as a central hub to monitor, track, and visualize the actions performed by your AI agents.

- **PyPI Package**: [gateagent](https://pypi.org/project/gateagent/)
- **Companion Library**: [agent-revert](https://pypi.org/project/agent-revert/)

## Features

-   **Event Tracking**: Receive and store events from agents using `agent-revert`.
-   **Agent Registry**: Keep track of all registered agents.
-   **Visual Dashboard**: A web-based UI to view agent activities, timelines, and affected applications.
-   **Integrations**: View status of external integrations (e.g., Gsuite, Salesforce).

## Installation

```bash
pip install gateagent
```

## Usage

Start the gateway server:

```bash
gateagent start
```

Visit `http://localhost:5173` (or the configured port) to view the dashboard.

## Connecting Agents

Use the `agent-revert` package in your agent code to send events to this gateway.

```python
from agent_revert import register_agent, track_action

register_agent("MyAgent")

@track_action(agent_name="MyAgent")
def do_work():
    pass
```
