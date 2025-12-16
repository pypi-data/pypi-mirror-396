# EdgeProt Client

`edgeprot-client` is a Python library for interacting with the EdgeProt API.
It provides a simple interface to send requests and handle responses from EdgeProt.

## Installation

```bash
pip install edgeprot-client
```

## Usage
```python
from edgeprot_api import APIClient

client = APIClient(api_key="API_KEY", base_url="https://api.example.com")

rules = client.rules.get()
print(rules)
```

## Features
- Works with the entire EdgeProt API.
- Fully typed responses with Pydantic.
- Sychronous API calls using requests.
- Easily maintainable.

## Requirements
- Python >= 3.9
- requests >= 2.30.0
- pydantic >= 2.3.0
