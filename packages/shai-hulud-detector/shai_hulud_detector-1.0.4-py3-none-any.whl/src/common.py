from dataclasses import dataclass, field
from typing import List, Optional
from enum import StrEnum

class ScanStatus(StrEnum):
    OKAY = "OKAY"
    FLAG = "FLAG"
    ERROR = "ERROR"

class SuspiciousReason(StrEnum):
    DESCRIPTION_PATTERN = "DESCRIPTION_PATTERN"
    SUSPICIOUS_FILE = "SUSPICIOUS_FILE"

@dataclass(frozen=True)
class SuspiciousResult:
    name: str
    html_url: str
    reason: SuspiciousReason
    file_path: Optional[str] = None

@dataclass
class ScanStats:
    search_description_hits: int = 0
    suspicious_files_found: int = 0

@dataclass
class ScanResult:
    username: str
    status: ScanStatus = field(default=ScanStatus.OKAY)
    suspicious_results: List[SuspiciousResult] = field(default_factory=list)
    stats: ScanStats = field(default_factory=ScanStats)
    error: Optional[str] = None