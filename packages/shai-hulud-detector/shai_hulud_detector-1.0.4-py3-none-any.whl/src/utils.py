import typer
from src.common import ScanResult, ScanStatus

def format_scan_result(result: ScanResult):
    if result.status == ScanStatus.FLAG:
        typer.secho(f"[FLAG] {result.username} compromised ({len(result.suspicious_results)} suspicious results):", fg=typer.colors.RED)
        for suspicious_result in result.suspicious_results:
            typer.secho(f"    {suspicious_result.reason}: {suspicious_result.html_url}", fg=typer.colors.RED)
            if suspicious_result.file_path:
                typer.secho(f"        {suspicious_result.file_path}", fg=typer.colors.YELLOW)
    elif result.status == ScanStatus.OKAY:
        typer.secho(f"[OKAY] {result.username} ({len(result.suspicious_results)} suspicious results)", fg=typer.colors.GREEN)
    else:
        typer.secho(f"[ERROR] {result.username}: {result.error}", fg=typer.colors.YELLOW)