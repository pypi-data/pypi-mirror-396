# stewai (Python SDK)

Base URL (only): `https://api.stewai.com/v1`

## Install

```bash
pip install stewai
```

## Get an API key

1. Log in to `stewai.com`
2. Go to `Settings → API keys`
3. Create a key and copy it once (`sk-live-...`)

## Usage

```python
from stewai import Stew

client = Stew(api_key="sk-live-...")

# Use the Input step “API input id” shown in the editor as the inputs key
run = client.runs.create(
    recipe_id="01K....",
    inputs={"USERQUESTION": "What should I focus on this week?"},
)

run = client.runs.wait(run["id"], timeout=300)
steps = client.runs.steps(run["id"])
```
