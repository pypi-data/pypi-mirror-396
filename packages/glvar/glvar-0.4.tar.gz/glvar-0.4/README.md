# glvar

CLI for fetching GitLab CI/CD variables and inject them into your local environment for running commands.

Inspired by `op`, Doppler, `pass`, etc.

## Use Cases

- Read API keys for local development
- Run deployments that require secrets/API keys from your machine
- Extract `.env` files with config options stored in CI/CD variables

## Installation

Requires Python 3.10+.

```bash
# Install with uv
uv tool install glvar

# Or with pip
pip install glvar
```

## Quick Start

```bash
# Interactive setup (creates token, stores in OS keyring)
glvar config setup

# Get a variable value
glvar get -p mygroup/myproject API_KEY

# Run a command with variables injected
glvar run -p mygroup/myproject API_KEY DB_PASS -- ./deploy.sh

# List available variables
glvar list -p mygroup/myproject

# List projects you have access to
glvar projects
```

## Usage

### Configuration

```bash
# Interactive setup - guides you through creating a GitLab PAT
glvar config setup

# Store token in config file instead of keyring
glvar config setup --no-keyring

# Show current configuration
glvar config show

# Reset configuration (remove token from keyring)
glvar config reset
```

The setup wizard will:
1. Ask for your GitLab URL (defaults to https://gitlab.com)
2. Provide a link to create a Personal Access Token with `read_api` scope
3. Validate the token and store it securely in your OS keyring

### Getting Variables

```bash
# Get a single variable (outputs value only)
glvar get -p mygroup/myproject MY_SECRET

# Get multiple variables in .env format
glvar get -p mygroup/myproject VAR1 VAR2 --format=env > .env

# Get all variables
glvar get -p mygroup/myproject --all --format=env > .env

# Use in shell
export SECRET=$(glvar get -p mygroup/myproject API_KEY)
```

### Running Commands with Variables

```bash
# Inject specific variables into command environment
glvar run -p mygroup/myproject API_KEY DB_PASS -- ./deploy.sh

# Inject all variables
glvar run -p mygroup/myproject --all -- docker-compose up
```

Variables are injected directly into the command's environment without exposing them to your shell history.

### Environment Variables

You can set defaults via environment variables:

| Variable | Description |
|----------|-------------|
| `GLVAR_PROJECT` | Default project/group path |
| `GLVAR_URL` | GitLab URL (overrides config) |
| `GLVAR_TOKEN` | Access token (overrides keyring) |

```bash
export GLVAR_PROJECT=mygroup/myproject
glvar get API_KEY  # Uses GLVAR_PROJECT
```

### Variable Resolution

When fetching from a project path (e.g., `mygroup/myproject`), glvar checks both:
1. Project-level variables (takes precedence)
2. Group-level variables


## Development

```bash
# Install dependencies
uv sync

# Show make targets
make
make help

# Run linting
make lint

# Format code
make format

# Build package
make build

# Clean build artifacts
make clean
```

## Security Notes

- Tokens are stored in your OS keyring (not in plain text files)
- Config file at `~/.config/glvar/config.json` contains only the GitLab URL
- Be careful when exporting secrets to files - prefer using `glvar run` when possible

## License

See LICENSE file for details.
