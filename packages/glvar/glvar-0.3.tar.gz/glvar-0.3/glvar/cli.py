#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests<3",
#   "rich",
#   "click",
#   "keyring",
# ]
# ///
"""
glvar - Fetch Gitlab CI/CD variables and inject into environment for local commands.
"""

import json
import sys
from pathlib import Path
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

import click
import keyring
import requests
from rich.console import Console
from rich.prompt import Prompt


# Version format: MAJOR.MINOR[.devN]
# - Use .devN suffix during development - add after making a release
# - Remove .devN for stable releases
# - Increment MINOR for new features, MAJOR for breaking changes
__version__ = "0.3"


HELP_TEXT = """GitLab CI/CD variable reader.

glvar - Fetch Gitlab CI/CD variables and inject into environment for local commands.

\b
Usage:
  glvar run -p GROUP/PROJECT MY_SECRET -- ./deploy.sh ...
  glvar get -p GROUP/PROJECT VAR        # Get a variable
\b
  export GLVAR_PROJECT=mygroup/myproject
  export SECRET=$(glvar get MY_SECRET)
\b
  glvar config setup                    # Interactive setup
  glvar projects                        # List available projects
  glvar list -p GROUP/PROJECT           # List variables

\b
Use cases:
- Read API keys for development
- Run a deploy that requires secrets/api keys from your computer
- Extract a .env file with config options stored in a CI/CD variable

Examples:

IMPORTANT: The examples extract secrets from GitLab - be careful and use responsibly.
Understand what it does before using and avoid saving secrets to files whenever possible.

\b
# Setup glvar - with guide to creating a token in GitLab:
# (glvar store token in OS keyring)
$ glvar config setup

\b
# Run deploy that requires secrets from Gitlab - without exposing to shell:
$ glvar run -p group/project DEV_OPENROUTER_API_KEY \\
    -- ./sdeploy deploy --host $DEPLOY_HOST \\
      --build /path/to/build --system-config /path/to/system-config \\
      --env DEV_OPENROUTER_API_KEY

\b
# Set as shell variable:
$ OPENROUTER_API_KEY=$(glvar get -p group/project DEV_OPENROUTER_API_KEY) ./your-command

\b
# Can also write to .env file (bestfor non-secret variables):
$ glvar get -p group/project --format env SETTING_A OPTION_B > .env

\b
# List available variables:
$ glvar list -p group/project

"""


# Constants
APP_NAME = "glvar"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"

console = Console(stderr=True)


def load_config() -> dict | None:
    """Load configuration from file and optionally keyring."""
    if not CONFIG_FILE.exists():
        return None

    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        console.print(f"[red]Error reading config: {e}[/red]")
        return None

    # Get token based on storage setting (default: keyring)
    if config.get("use_keyring", True):
        token = keyring.get_password(APP_NAME, "token")
        if token:
            config["token"] = token
    # If use_keyring is False, token is already in config dict

    return config


def save_config(gitlab_url: str, token: str, use_keyring: bool = True) -> None:
    """Save configuration to file and token to keyring or config."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    config = {
        "gitlab_url": gitlab_url.rstrip("/"),
        "use_keyring": use_keyring,
    }

    if token:
        if use_keyring:
            keyring.set_password(APP_NAME, "token", token)
        else:
            config["token"] = token

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    # Set secure permissions (owner read/write only)
    CONFIG_FILE.chmod(0o600)


def validate_config(gitlab_url: str, token: str) -> tuple[bool, str | None]:
    """Validate GitLab URL and token by making a test API call."""
    try:
        resp = requests.get(
            f"{gitlab_url.rstrip('/')}/api/v4/user",
            headers={"PRIVATE-TOKEN": token},
            timeout=10,
        )
        if resp.status_code == 200:
            user = resp.json()
            return True, user.get("username")
        elif resp.status_code == 401:
            return False, "Invalid token"
        else:
            return False, f"HTTP {resp.status_code}: {resp.text[:100]}"
    except requests.RequestException as e:
        return False, str(e)


def _fetch_variable(
    gitlab_url: str, token: str, path: str, variable: str, is_group: bool
) -> tuple[str | None, str | None]:
    """Fetch a CI/CD variable from GitLab. Returns (value, error)."""
    encoded = quote(path, safe="")
    if is_group:
        url = f"{gitlab_url}/api/v4/groups/{encoded}/variables/{variable}"
        entity = "group"
    else:
        url = f"{gitlab_url}/api/v4/projects/{encoded}/variables/{variable}"
        entity = "project"

    try:
        resp = requests.get(
            url,
            headers={"PRIVATE-TOKEN": token},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["value"], None
        elif resp.status_code == 404:
            return None, None  # Not found is not an error, just missing
        elif resp.status_code == 401:
            return None, "Authentication failed. Check your token."
        elif resp.status_code == 403:
            return None, f"Access denied to {entity} {path}"
        else:
            return None, f"Error {resp.status_code}: {resp.text}"
    except requests.RequestException as e:
        return None, f"Request failed: {e}"


def get_variable(gitlab_url: str, token: str, path: str, variable: str) -> str | None:
    """Fetch a CI/CD variable, checking project then group in parallel."""

    is_group = "/" not in path

    if is_group:
        # Just a group, single fetch
        value, error = _fetch_variable(gitlab_url, token, path, variable, is_group=True)
        if error:
            console.print(f"[red]{error}[/red]")
        elif value is None:
            console.print(f"[red]Variable not found: {variable} in group {path}[/red]")
        return value

    # Project path - fetch both project and group in parallel
    group = path.split("/")[0]

    with ThreadPoolExecutor(max_workers=2) as executor:
        project_future = executor.submit(
            _fetch_variable, gitlab_url, token, path, variable, is_group=False
        )
        group_future = executor.submit(
            _fetch_variable, gitlab_url, token, group, variable, is_group=True
        )

        project_val, project_err = project_future.result()
        group_val, group_err = group_future.result()

    # Project takes precedence
    if project_val is not None:
        return project_val
    if group_val is not None:
        return group_val

    # Report errors (prefer project error if both failed)
    if project_err:
        console.print(f"[red]{project_err}[/red]")
    elif group_err:
        console.print(f"[red]{group_err}[/red]")
    else:
        console.print(f"[red]Variable not found: {variable} in {path} or {group}[/red]")

    return None


def list_variables(gitlab_url: str, token: str, path: str) -> list[dict] | None:
    """List CI/CD variables for a project or group."""
    encoded = quote(path, safe="")
    is_group = "/" not in path
    if is_group:
        url = f"{gitlab_url}/api/v4/groups/{encoded}/variables"
        entity = "group"
    else:
        url = f"{gitlab_url}/api/v4/projects/{encoded}/variables"
        entity = "project"

    try:
        resp = requests.get(
            url,
            headers={"PRIVATE-TOKEN": token},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            console.print("[red]Authentication failed. Check your token.[/red]")
        elif resp.status_code == 403:
            console.print(f"[red]Access denied to {entity} {path}[/red]")
        elif resp.status_code == 404:
            console.print(f"[red]{entity.capitalize()} not found: {path}[/red]")
        else:
            console.print(f"[red]Error {resp.status_code}: {resp.text}[/red]")
        return None
    except requests.RequestException as e:
        console.print(f"[red]Request failed: {e}[/red]")
        return None


def quote_env_value(value: str) -> str:
    """Quote a value for dotenv format using double quotes."""
    # Escape backslash, double quote, dollar sign, backtick, newline
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace("$", "\\$")
    escaped = escaped.replace("`", "\\`")
    escaped = escaped.replace("\n", "\\n")
    escaped = escaped.replace("\r", "\\r")
    return f'"{escaped}"'


def list_projects(gitlab_url: str, token: str, limit: int = 100) -> list[dict] | None:
    """List projects the user has access to."""
    url = f"{gitlab_url}/api/v4/projects"

    try:
        resp = requests.get(
            url,
            headers={"PRIVATE-TOKEN": token},
            params={
                "membership": "true",
                "simple": "true",  # Only return basic fields
                "per_page": min(limit, 100),
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            console.print("[red]Authentication failed. Check your token.[/red]")
            return None
        else:
            console.print(f"[red]Error {resp.status_code}: {resp.text}[/red]")
            return None
    except requests.RequestException as e:
        console.print(f"[red]Request failed: {e}[/red]")
        return None


# ============================================================================
# CLI Commands
# ============================================================================


def get_config(ctx) -> dict:
    """Get config from context, exit if not configured."""
    cfg = ctx.obj.get("config", {})
    if not cfg.get("gitlab_url") or not cfg.get("token"):
        console.print("[red]Not configured. Run: glvar config setup[/red]")
        sys.exit(1)
    return cfg


@click.group(help=HELP_TEXT, invoke_without_command=True)
@click.option("--url", envvar="GLVAR_URL", show_envvar=True, help="GitLab URL (overrides config)")
@click.option(
    "--token",
    envvar="GLVAR_TOKEN",
    show_envvar=True,
    help="Personal Access Token (overrides keyring)",
)
@click.pass_context
def cli(ctx, url: str | None, token: str | None):
    ctx.ensure_object(dict)

    # Load config, then override with CLI options
    cfg = load_config() or {}
    if url:
        cfg["gitlab_url"] = url.rstrip("/")
    if token:
        cfg["token"] = token
    ctx.obj["config"] = cfg

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.group()
def config():
    """Manage configuration."""
    pass


@config.command("setup")
@click.option(
    "--url",
    envvar="GLVAR_URL",
    show_envvar=True,
    help="GitLab URL (e.g., https://gitlab.example.com)",
)
@click.option(
    "--token",
    envvar="GLVAR_TOKEN",
    show_envvar=True,
    help="Personal Access Token with read_api scope",
)
@click.option("--no-keyring", is_flag=True, help="Store token in config file instead of OS keyring")
def config_setup(url: str | None, token: str | None, no_keyring: bool):
    """Configure GitLab connection."""
    use_keyring = not no_keyring
    interactive = not url or not token

    if interactive:
        console.print("[bold]GitLab Variable Reader Setup[/bold]")
        console.print()
        console.print(f"[dim]Config will be saved to: {CONFIG_FILE}[/dim]")
        if not use_keyring:
            console.print("[dim]Token will be stored in config file (--no-keyring)[/dim]")
        console.print()

    # Get URL
    if not url:
        url = Prompt.ask("GitLab URL", default="https://gitlab.com")

    # Save URL (whether from arg or prompt)
    save_config(url, "", use_keyring=use_keyring)
    if interactive:
        console.print("[dim]Saved URL to config[/dim]")

    # Get token
    if not token:
        token_url = f"{url.rstrip('/')}/-/user_settings/personal_access_tokens"
        console.print()
        console.print(f"Create a PAT at: [link={token_url}]{token_url}[/link]")
        console.print("[dim]Required scope: read_api[/dim]")
        console.print()
        token = Prompt.ask("Personal Access Token", password=True)

    if not url or not token:
        console.print("[red]URL and token are required.[/red]")
        sys.exit(1)

    # Validate
    console.print()
    console.print("[dim]Validating...[/dim]")
    valid, result = validate_config(url, token)

    if not valid:
        console.print(f"[red]Validation failed: {result}[/red]")
        sys.exit(1)

    # Save
    save_config(url, token, use_keyring=use_keyring)

    console.print()
    console.print(f"[green]✓ Authenticated as:[/green] {result}")
    console.print(f"[green]✓ Config saved to:[/green] {CONFIG_FILE}")
    if use_keyring:
        console.print("[green]✓ Token stored in:[/green] OS keyring")
    else:
        console.print("[green]✓ Token stored in:[/green] config file")
    console.print()
    console.print("[dim]Example: export SECRET=$(glvar get -p group/project MY_SECRET)[/dim]")


@config.command("show")
def config_show():
    """Show current configuration."""
    cfg = load_config()

    if not cfg:
        console.print("[yellow]Not configured. Run: glvar config setup[/yellow]")
        sys.exit(1)

    console.print(f"[bold]Config file:[/bold] {CONFIG_FILE}")
    console.print(f"[bold]GitLab URL:[/bold] {cfg.get('gitlab_url', 'not set')}")

    use_keyring = cfg.get("use_keyring", True)
    console.print(f"[bold]Token storage:[/bold] {'keyring' if use_keyring else 'config file'}")

    # Get token based on storage setting
    token = cfg.get("token")
    if token:
        storage_location = "keyring" if use_keyring else "config file"
        console.print(f"[bold]Token:[/bold] {'*' * 20} (hidden, from {storage_location})")
    else:
        console.print("[bold]Token:[/bold] [yellow]not found[/yellow]")
        return

    valid, result = validate_config(cfg["gitlab_url"], token)
    if valid:
        console.print(f"[bold]User:[/bold] {result}")
        console.print("[green]✓ Token is valid[/green]")
    else:
        console.print(f"[red]✗ Token invalid: {result}[/red]")


@config.command("reset")
def config_reset():
    """Remove configuration and token."""
    removed = False

    # Check if we need to clean up keyring
    use_keyring = True
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
                use_keyring = cfg.get("use_keyring", True)
        except (json.JSONDecodeError, IOError):
            pass

        CONFIG_FILE.unlink()
        console.print(f"[green]✓ Removed {CONFIG_FILE}[/green]")
        removed = True

    if use_keyring:
        try:
            keyring.delete_password(APP_NAME, "token")
            console.print("[green]✓ Removed token from keyring[/green]")
            removed = True
        except keyring.errors.PasswordDeleteError:
            pass

    if not removed:
        console.print("[dim]Nothing to remove[/dim]")


@cli.command()
@click.option("-n", "--limit", default=50, help="Max number of projects to show")
@click.pass_context
def projects(ctx, limit: int):
    """List projects you have access to.

    Shows project paths that can be used with 'list' and 'get' commands.
    """
    cfg = get_config(ctx)
    project_list = list_projects(cfg["gitlab_url"], cfg["token"], limit)

    if project_list is None:
        sys.exit(1)

    if not project_list:
        console.print("[dim]No projects found[/dim]")
        return

    # Sort by path
    project_list.sort(key=lambda p: p.get("path_with_namespace", "").lower())

    for proj in project_list:
        path = proj.get("path_with_namespace", "")
        print(path)


@cli.command("list")
@click.option(
    "-p", "--project", envvar="GLVAR_PROJECT", show_envvar=True, help="Project/group path"
)
@click.pass_context
def list_cmd(ctx, project: str | None):
    """List CI/CD variables for a project or group.

    Examples:

        glvar list -p mygroup/myproject

        export GLVAR_PROJECT=mygroup/myproject
        glvar list
    """
    cfg = get_config(ctx)

    if not project:
        console.print("[red]No project specified. Use -p/--project or set GLVAR_PROJECT[/red]")
        sys.exit(1)

    variables = list_variables(cfg["gitlab_url"], cfg["token"], project)

    if variables is None:
        sys.exit(1)

    if not variables:
        console.print("[dim]No variables found[/dim]")
        return

    for var in variables:
        key = var.get("key", "")
        scope = var.get("environment_scope", "*")
        protected = "protected" if var.get("protected") else ""
        masked = "masked" if var.get("masked") else ""

        flags = " ".join(filter(None, [protected, masked]))
        if flags:
            flags = f" [dim]({flags})[/dim]"

        if scope != "*":
            console.print(f"{key} [dim][{scope}][/dim]{flags}")
        else:
            console.print(f"{key}{flags}")


@cli.command()
@click.option(
    "-p", "--project", envvar="GLVAR_PROJECT", show_envvar=True, help="Project/group path"
)
@click.option("-a", "--all", "fetch_all", is_flag=True, help="Get all variables")
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["value", "env"]),
    default="value",
    help="Output format",
)
@click.argument("variables", nargs=-1)
@click.pass_context
def get(ctx, project: str | None, fetch_all: bool, fmt: str, variables: tuple[str, ...]):
    """Get CI/CD variable(s).

    Examples:

        glvar get -p mygroup/myproject API_KEY

        glvar get -p mygroup/myproject VAR1 VAR2 --format=env > .env

        glvar get -p mygroup/myproject --all --format=env > .env

        export GLVAR_PROJECT=mygroup/myproject
        export SECRET=$(glvar get API_KEY)
    """
    cfg = get_config(ctx)

    if not project:
        console.print("[red]No project specified. Use -p/--project or set GLVAR_PROJECT[/red]")
        sys.exit(1)

    if not fetch_all and not variables:
        console.print("[red]No variables specified. Use -a/--all or provide variable names[/red]")
        sys.exit(1)

    # If --all, fetch all variable names first
    if fetch_all:
        var_list = list_variables(cfg["gitlab_url"], cfg["token"], project)
        if var_list is None:
            sys.exit(1)
        variables = tuple(v["key"] for v in var_list)

    failed = False
    results = []

    for variable in variables:
        value = get_variable(cfg["gitlab_url"], cfg["token"], project, variable)
        if value is None:
            failed = True
        else:
            results.append((variable, value))

    # Output results
    for variable, value in results:
        if fmt == "env":
            print(f"{variable}={quote_env_value(value)}")
        else:
            print(value)

    if failed:
        sys.exit(1)


@cli.command()
@click.option(
    "-p", "--project", envvar="GLVAR_PROJECT", show_envvar=True, help="Project/group path"
)
@click.option("-a", "--all", "fetch_all", is_flag=True, help="Use all variables")
@click.argument("variables", nargs=-1)
@click.pass_context
def run(ctx, project: str | None, fetch_all: bool, variables: tuple[str, ...]):
    """Run a command with CI/CD variables in environment.

    Variables are listed before --, command follows after.

    Examples:

        glvar run -p mygroup/project VAR1 VAR2 -- ./deploy.sh

        glvar run -p mygroup/project --all -- ./deploy.sh

        export GLVAR_PROJECT=mygroup/project
        glvar run API_KEY DB_PASS -- docker-compose up
    """
    import os

    cfg = get_config(ctx)

    if not project:
        console.print("[red]No project specified. Use -p/--project or set GLVAR_PROJECT[/red]")
        sys.exit(1)

    if not _doubledash_command:
        console.print("[red]Missing -- separator. Usage: glvar run VAR1 VAR2 -- command[/red]")
        sys.exit(1)

    if not fetch_all and not variables:
        console.print("[red]No variables specified. Use -a/--all or provide variable names[/red]")
        sys.exit(1)

    # If --all, fetch all variable names first
    if fetch_all:
        var_list = list_variables(cfg["gitlab_url"], cfg["token"], project)
        if var_list is None:
            sys.exit(1)
        variables = tuple(v["key"] for v in var_list)

    # Fetch variables
    env = os.environ.copy()
    for variable in variables:
        value = get_variable(cfg["gitlab_url"], cfg["token"], project, variable)
        if value is None:
            sys.exit(1)
        env[variable] = value

    # Replace process with command
    os.execvpe(_doubledash_command[0], _doubledash_command, env)


_doubledash_command = None

if __name__ == "__main__":
    if "--" in sys.argv:
        sep_idx = sys.argv.index("--")
        _doubledash_command = sys.argv[sep_idx + 1 :]
        sys.argv = sys.argv[:sep_idx]
    cli()
