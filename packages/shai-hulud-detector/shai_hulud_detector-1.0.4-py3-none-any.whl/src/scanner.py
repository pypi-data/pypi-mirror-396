from github import Github, GithubException
from typing import List, Optional, Callable, Set
from src.common import SuspiciousResult, ScanResult, ScanStats, ScanStatus, SuspiciousReason
import typer

PATTERNS = [
    "Sha1-Hulud: The Second Coming.",
    # Add more patterns here
]

SUSPICIOUS_FILES = [
    'actionsSecrets.json',
    'secrets.json',
    'env.json',
    'credentials.json',
    'contents.json',
    'environment.json',
    'cloud.json',
    'truffleSecrets.json',
]

def search_repos_by_description(github: Github, username: str, log: Callable[[str], None]) -> List[SuspiciousResult]:
    found: Set[SuspiciousResult] = set()
    query_parts = [f'user:{username}'] + [f'description:"{p}"' for p in PATTERNS]
    query = " OR ".join(query_parts)
    log(f"Searching for description patterns in {username}...")
    for repo in github.search_repositories(query=query):
        found.add(SuspiciousResult(
            name=repo.name,
            html_url=repo.html_url,
            reason=SuspiciousReason.DESCRIPTION_PATTERN
        ))
    return list(found)

def search_suspicious_files(
    github: Github,
    username: str,
    log: Callable[[str], None]
) -> List[SuspiciousResult]:
    found: Set[SuspiciousResult] = set()
    for filename in SUSPICIOUS_FILES:
        query = f'user:{username} filename:{filename}'
        log(f"Searching for suspicious file: {filename} in {username}...")
        for item in github.search_code(query=query):
            found.add(SuspiciousResult(
                name=item.repository.name,
                html_url=item.repository.html_url,
                file_path=item.path,
                reason=SuspiciousReason.SUSPICIOUS_FILE
            ))
    return list(found)

def scan_user(
    github: Github,
    username: str,
    verbose_callback: Optional[Callable[[str], None]] = None
) -> ScanResult:
    stats = ScanStats()
    suspicious_results: Set[SuspiciousResult] = set()
    
    def log(msg: str):
        if verbose_callback:
            verbose_callback(msg)

    log(f"Scanning user: {username}")
    try:
        # Search for description patterns
        desc_hits = search_repos_by_description(github, username, log)
        suspicious_results.update(desc_hits)
        stats.search_description_hits = len(desc_hits)
        for hit in desc_hits:
            log(f"  ⚠️ Description match in {hit.name}: {hit.html_url}")

        # Search for suspicious files
        file_hits = search_suspicious_files(github, username, log)
        suspicious_results.update(file_hits)
        stats.suspicious_files_found = len(file_hits)
        for hit in file_hits:
            log(f"  ⚠️ Suspicious file in {hit.name}: {hit.file_path}")

        suspicious_list = list(suspicious_results)
        if suspicious_list:
            log(f"FLAG {username}: {len(suspicious_list)} suspicious results")
            return ScanResult(
                username=username,
                status=ScanStatus.FLAG,
                suspicious_results=suspicious_list,
                stats=stats
            )
        else:
            log(f"OKAY {username}: clean")
            return ScanResult(
                username=username,
                status=ScanStatus.OKAY,
                suspicious_results=[],
                stats=stats
            )
    except GithubException as e:
        error_msg = str(e)
        log(f"ERROR {username}: GitHub API error - {error_msg}")
        return ScanResult(
            username=username,
            status=ScanStatus.ERROR,
            error=error_msg,
            stats=stats
        )
    except Exception as e:
        error_msg = str(e)
        log(f"ERROR {username}: Unexpected - {error_msg}")
        return ScanResult(
            username=username,
            status=ScanStatus.ERROR,
            error=error_msg,
            stats=stats
        )

def get_org_members(github: Github, org_name: str) -> List[str]:
    org = github.get_organization(org_name)
    return [member.login for member in org.get_members()]