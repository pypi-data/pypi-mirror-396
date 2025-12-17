# GuardianHub SDK

A Python SDK for interacting with GuardianHub services, featuring a model registry and LLM client.

## Features

- Model registry with versioning
- Async HTTP client for API interactions
- Pydantic model support
- Local development and testing tools

## Installation

```bash
# Install from PyPI (when published)
ssh-keygen -t ed25519 -C "rashmi@yantramops.com"
pip install guardianhub-sdk

# Or install in development mode
pip install -e .[test]

# 1. Remove the specified directory and its contents from the Git index.
#    The --cached flag ensures the files are NOT deleted from your local disk.
git rm -r --cached .github

# 2. Add the .gitignore file (which now contains the new rules)
git add .gitignore

# 3. Commit the changes
git commit -m "Cleanup: Remove .github directory from tracking and update .gitignore"

git checkout -b dev
git push -u origin dev


git checkout dev
git pull origin dev   # Ensure you have the latest code
git checkout -b feature/model-registry # Name your branch descriptively
git push -u origin feature/model-registry

```

## Usage

```python
from guardianhub_sdk.models.registry.loader import RegistryLoader

# Initialize the loader
loader = RegistryLoader()

# Load a model
model = await loader.load_model("UserModel", version="v1")
```

## Development

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/guardianhub-sdk.git
   cd guardianhub-sdk
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .[test]
   ```

### Running Tests

```bash
pytest tests/
```

## License

MIT