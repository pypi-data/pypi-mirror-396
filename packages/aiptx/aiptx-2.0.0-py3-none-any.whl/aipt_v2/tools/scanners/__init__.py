"""
AIPT Scanner Tools - External Scanner Integrations

Provides plug-and-play integrations with enterprise security scanners:
- Acunetix Web Vulnerability Scanner
- Burp Suite Pro/Enterprise

Server Configuration:
    Public IP:    13.127.28.41
    Acunetix:     https://13.127.28.41:3443
    Burp Suite:   http://13.127.28.41:1337
"""

# Configuration
from aipt_v2.tools.scanners.config import (
    SCANNER_SERVER_IP,
    ACUNETIX_PORT,
    BURP_PORT,
    ACUNETIX_URL,
    BURP_URL,
    ACUNETIX,
    BURP,
    SCANNER,
    AcunetixSettings,
    BurpSettings,
    ScannerSettings,
    get_acunetix_config,
    get_burp_config,
    print_config,
)

# Acunetix Integration
from aipt_v2.tools.scanners.acunetix_tool import (
    AcunetixTool,
    AcunetixConfig,
    ScanProfile,
    ScanStatus as AcunetixScanStatus,
    ScanResult as AcunetixScanResult,
    Vulnerability as AcunetixVulnerability,
    Severity as AcunetixSeverity,
    get_acunetix,
    acunetix_scan,
    acunetix_status,
    acunetix_vulns,
    acunetix_summary,
)

# Burp Suite Integration
from aipt_v2.tools.scanners.burp_tool import (
    BurpTool,
    BurpConfig,
    ScanStatus as BurpScanStatus,
    ScanResult as BurpScanResult,
    Issue as BurpIssue,
    IssueSeverity,
    IssueConfidence,
    get_burp,
    burp_scan,
    burp_status,
    burp_issues,
    burp_summary,
)

__all__ = [
    # Configuration
    "SCANNER_SERVER_IP",
    "ACUNETIX_PORT",
    "BURP_PORT",
    "ACUNETIX_URL",
    "BURP_URL",
    "ACUNETIX",
    "BURP",
    "SCANNER",
    "AcunetixSettings",
    "BurpSettings",
    "ScannerSettings",
    "get_acunetix_config",
    "get_burp_config",
    "print_config",
    # Acunetix
    "AcunetixTool",
    "AcunetixConfig",
    "ScanProfile",
    "AcunetixScanStatus",
    "AcunetixScanResult",
    "AcunetixVulnerability",
    "AcunetixSeverity",
    "get_acunetix",
    "acunetix_scan",
    "acunetix_status",
    "acunetix_vulns",
    "acunetix_summary",
    # Burp Suite
    "BurpTool",
    "BurpConfig",
    "BurpScanStatus",
    "BurpScanResult",
    "BurpIssue",
    "IssueSeverity",
    "IssueConfidence",
    "get_burp",
    "burp_scan",
    "burp_status",
    "burp_issues",
    "burp_summary",
    # Unified Interface
    "ScannerType",
    "get_scanner",
    "scan_target",
    "get_findings",
    "get_all_findings",
    "test_all_connections",
]


# ==================== Unified Scanner Interface ====================

class ScannerType:
    """Scanner type constants."""
    ACUNETIX = "acunetix"
    BURP = "burp"


def get_scanner(scanner_type: str, config: dict = None):
    """
    Get a scanner instance by type.

    Args:
        scanner_type: 'acunetix' or 'burp'
        config: Optional configuration dict

    Returns:
        Scanner tool instance
    """
    if scanner_type == ScannerType.ACUNETIX:
        cfg = AcunetixConfig(**config) if config else None
        return get_acunetix(cfg)
    elif scanner_type == ScannerType.BURP:
        cfg = BurpConfig(**config) if config else None
        return get_burp(cfg)
    else:
        raise ValueError(f"Unknown scanner type: {scanner_type}")


def scan_target(url: str, scanner_type: str = "acunetix", **kwargs):
    """
    Unified scan function - works with any scanner.

    Args:
        url: Target URL to scan
        scanner_type: 'acunetix' or 'burp'
        **kwargs: Scanner-specific options

    Returns:
        ScanResult from the chosen scanner
    """
    if scanner_type == ScannerType.ACUNETIX:
        profile = kwargs.get("profile", "full")
        return acunetix_scan(url, profile)
    elif scanner_type == ScannerType.BURP:
        config_id = kwargs.get("config_id")
        return burp_scan(url, config_id)
    else:
        raise ValueError(f"Unknown scanner type: {scanner_type}")


def get_findings(scanner_type: str, scan_id: str = None, severity: str = None):
    """
    Get findings from any scanner in unified AIPT format.

    Args:
        scanner_type: 'acunetix' or 'burp'
        scan_id: Optional scan ID filter
        severity: Optional severity filter

    Returns:
        List of findings in AIPT format
    """
    if scanner_type == ScannerType.ACUNETIX:
        return acunetix_vulns(scan_id, severity)
    elif scanner_type == ScannerType.BURP:
        return burp_issues(scan_id, severity)
    else:
        raise ValueError(f"Unknown scanner type: {scanner_type}")


def get_all_findings(scan_ids: dict = None) -> list:
    """
    Aggregate findings from all scanners.

    Args:
        scan_ids: Dict mapping scanner_type to scan_id

    Returns:
        Combined list of findings from all scanners
    """
    findings = []
    scan_ids = scan_ids or {}

    try:
        acunetix_findings = acunetix_vulns(scan_ids.get("acunetix"))
        findings.extend(acunetix_findings)
    except Exception as e:
        pass  # Scanner not available

    try:
        burp_findings = burp_issues(scan_ids.get("burp"))
        findings.extend(burp_findings)
    except Exception as e:
        pass  # Scanner not available

    return findings


def test_all_connections() -> dict:
    """
    Test connections to all configured scanners.

    Returns:
        Dict with connection status for each scanner
    """
    results = {}

    # Test Acunetix
    try:
        acunetix = AcunetixTool()
        results["acunetix"] = {
            "connected": acunetix.connect(),
            "url": acunetix.config.base_url,
            "info": acunetix.get_info() if acunetix.is_connected() else None
        }
    except Exception as e:
        results["acunetix"] = {"connected": False, "error": str(e)}

    # Test Burp
    try:
        burp = BurpTool()
        results["burp"] = {
            "connected": burp.connect(),
            "url": burp.config.base_url,
            "info": burp.get_info() if burp.is_connected() else None
        }
    except Exception as e:
        results["burp"] = {"connected": False, "error": str(e)}

    return results
