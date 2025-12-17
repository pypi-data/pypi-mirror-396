import typer
from typing import List, Optional
import concurrent.futures

from src.github_utils import get_github_client
from src.scanner import scan_user, get_org_members
from src.common import ScanResult
from src.utils import format_scan_result

app = typer.Typer(
    help="""
    Shai Hulud Detector

    A CLI tool to scan GitHub users and organizations for shai-hulud compromise detection.
    """,
    invoke_without_command=True,
    no_args_is_help=True,
)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Welcome to Shai-Hulud — the worm that detects worms.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

@app.command(no_args_is_help=True)
def scan(
    usernames: List[str] = typer.Argument(None, help="GitHub usernames to scan"),
    org: Optional[str] = typer.Option(None, "--org", "-o", help="GitHub org to scan all members"),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN)"),
    workers: int = typer.Option(5, "--workers", "-w", help="Concurrent workers"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose output including repo counts"),
):
    """
    Scan GitHub user(s) or org members for shai-hulud compromise.
    """
    github = get_github_client(token)

    scan_list: List[str] = []
    if org:
        try:
            scan_list = get_org_members(github, org)
            typer.echo(f"Scanning {len(scan_list)} org members of '{org}' ...")
        except Exception as e:
            typer.secho(f"Error getting org members: {e}", fg=typer.colors.RED, err=True)
            raise typer.Abort()
    elif usernames:
        scan_list = usernames
    if not scan_list:
        typer.secho("You must specify at least one GitHub username OR an organization with --org.", fg=typer.colors.RED, err=True)
        raise typer.Abort()

    def verbose_log(msg: str):
        if verbose:
            typer.echo(f"  {msg}", err=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(scan_user, github, u, verbose_log if verbose else None): u for u in scan_list}
        for future in concurrent.futures.as_completed(futures):
            result: ScanResult = future.result()
            format_scan_result(result)

def main():
    app()