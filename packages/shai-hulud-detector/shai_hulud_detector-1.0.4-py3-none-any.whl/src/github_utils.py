import os
from github import Github
import typer

def get_github_client(token: str = None):
    """Return authenticated or anonymous Github client."""
    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        typer.secho("ERROR: No GITHUB_TOKEN! Code search requires authentication.", fg="red", bold=True)
        typer.secho("→ Create one at: https://github.com/settings/tokens", fg="yellow")
        raise typer.Exit(1)
    
    return Github(token) if token else Github()