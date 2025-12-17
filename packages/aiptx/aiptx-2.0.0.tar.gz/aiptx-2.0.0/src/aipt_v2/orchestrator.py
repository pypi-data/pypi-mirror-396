#!/usr/bin/env python3
"""
AIPT Orchestrator - Full Penetration Testing Pipeline
=====================================================

Orchestrates the complete pentest workflow:
    RECON → SCAN → EXPLOIT → REPORT

Each phase uses specialized tools and integrates with enterprise scanners
(Acunetix, Burp Suite) for comprehensive coverage.

Usage:
    from orchestrator import Orchestrator

    orch = Orchestrator("example.com")
    results = await orch.run()

Or via CLI:
    python -m aipt_v2.orchestrator example.com --output ./results
"""

import asyncio
import json
import logging
import os
import re
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Scanner integrations
from aipt_v2.tools.scanners import (
    AcunetixTool,
    AcunetixConfig,
    ScanProfile,
    BurpTool,
    BurpConfig,
    get_acunetix,
    get_burp,
    acunetix_scan,
    acunetix_vulns,
    test_all_connections,
)

logger = logging.getLogger(__name__)


# ==================== SECURITY: Input Validation ====================

# Domain validation pattern (RFC 1123 compliant)
# Allows: alphanumeric, hyphens (not at start/end), dots for subdomains
DOMAIN_PATTERN = re.compile(
    r'^(?!-)'                           # Cannot start with hyphen
    r'(?:[a-zA-Z0-9]'                   # Start with alphanumeric
    r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?' # Middle can have hyphens
    r'\.)*'                             # Subdomains separated by dots
    r'[a-zA-Z0-9]'                      # Domain start
    r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?' # Domain middle
    r'\.[a-zA-Z]{2,}$'                  # TLD (at least 2 chars)
)

# IP address pattern (IPv4)
IPV4_PATTERN = re.compile(
    r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
    r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
)

# Characters that are dangerous in shell commands
SHELL_DANGEROUS_CHARS = set(';|&$`\n\r\\\'\"(){}[]<>!')


def validate_domain(domain: str) -> str:
    """
    Validate domain format to prevent command injection (CWE-78).

    Args:
        domain: Domain string to validate

    Returns:
        Validated domain string

    Raises:
        ValueError: If domain format is invalid or contains dangerous characters
    """
    if not domain:
        raise ValueError("Domain cannot be empty")

    domain = domain.strip().lower()

    # Check length
    if len(domain) > 253:
        raise ValueError(f"Domain too long: {len(domain)} chars (max 253)")

    # Check for dangerous shell characters
    dangerous_found = set(domain) & SHELL_DANGEROUS_CHARS
    if dangerous_found:
        raise ValueError(
            f"Domain contains dangerous characters: {dangerous_found}. "
            "Possible command injection attempt."
        )

    # Validate as IP or domain
    if IPV4_PATTERN.match(domain):
        return domain

    if DOMAIN_PATTERN.match(domain):
        return domain

    raise ValueError(
        f"Invalid domain format: {domain}. "
        "Expected format: example.com or sub.example.com"
    )


def sanitize_for_shell(value: str) -> str:
    """
    Sanitize a value for safe use in shell commands using shlex.quote.

    Args:
        value: String to sanitize

    Returns:
        Shell-escaped string safe for command interpolation
    """
    return shlex.quote(value)


class Phase(Enum):
    """Pentest phases."""
    RECON = "recon"
    SCAN = "scan"
    EXPLOIT = "exploit"
    REPORT = "report"


class Severity(Enum):
    """Finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """Security finding from any tool."""
    type: str
    value: str
    description: str
    severity: str
    phase: str
    tool: str
    target: str = ""
    evidence: str = ""
    remediation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class PhaseResult:
    """Result of a phase execution."""
    phase: Phase
    status: str
    started_at: str
    finished_at: str
    duration: float
    findings: List[Finding]
    tools_run: List[str]
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    # Target
    target: str
    output_dir: str = "./scan_results"

    # Phase control
    skip_recon: bool = False
    skip_scan: bool = False
    skip_exploit: bool = False
    skip_report: bool = False

    # Recon settings
    recon_tools: List[str] = field(default_factory=lambda: [
        "subfinder", "assetfinder", "httpx", "nmap", "waybackurls"
    ])

    # Scan settings
    scan_tools: List[str] = field(default_factory=lambda: [
        "nuclei", "ffuf", "sslscan"
    ])
    use_acunetix: bool = True
    use_burp: bool = False
    acunetix_profile: str = "full"
    wait_for_scanners: bool = False
    scanner_timeout: int = 3600

    # Exploit settings
    validate_findings: bool = True
    check_sensitive_paths: bool = True

    # Report settings
    report_format: str = "html"
    report_template: str = "professional"


class Orchestrator:
    """
    AIPT Orchestrator - Full pentest pipeline controller.

    Coordinates reconnaissance, scanning, exploitation, and reporting
    phases with integrated support for enterprise scanners.
    """

    def __init__(self, target: str, config: Optional[OrchestratorConfig] = None):
        """
        Initialize the orchestrator.

        Args:
            target: Target domain or URL
            config: Optional configuration
        """
        self.target = self._normalize_target(target)
        self.domain = self._extract_domain(target)
        self.config = config or OrchestratorConfig(target=target)
        self.config.target = self.target

        # State
        self.findings: List[Finding] = []
        self.phase_results: Dict[Phase, PhaseResult] = {}
        self.subdomains: List[str] = []
        self.live_hosts: List[str] = []
        self.scan_ids: Dict[str, str] = {}  # Scanner -> scan_id mapping

        # Setup output directory
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_dir = Path(self.config.output_dir) / f"{self.domain}_scan_{self.timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Callbacks
        self.on_phase_start: Optional[Callable[[Phase], None]] = None
        self.on_phase_complete: Optional[Callable[[PhaseResult], None]] = None
        self.on_finding: Optional[Callable[[Finding], None]] = None
        self.on_tool_start: Optional[Callable[[str, str], None]] = None
        self.on_tool_complete: Optional[Callable[[str, str, Any], None]] = None

        logger.info(f"Orchestrator initialized for {self.domain}")
        logger.info(f"Output directory: {self.output_dir}")

    @staticmethod
    def _normalize_target(target: str) -> str:
        """Normalize target URL."""
        if not target.startswith(("http://", "https://")):
            return f"https://{target}"
        return target

    @staticmethod
    def _extract_domain(target: str) -> str:
        """
        Extract and validate domain from target.

        Security: Validates domain format to prevent command injection (CWE-78).
        """
        domain = target.replace("https://", "").replace("http://", "")
        domain = domain.split("/")[0]
        domain = domain.split(":")[0]

        # Security: Validate domain format
        return validate_domain(domain)

    @property
    def safe_domain(self) -> str:
        """
        Get shell-safe domain for command interpolation.

        Returns:
            Shell-escaped domain string
        """
        return sanitize_for_shell(self.domain)

    def _log_phase(self, phase: Phase, message: str):
        """Log a phase message."""
        print(f"\n{'='*60}")
        print(f"  [{phase.value.upper()}] {message}")
        print(f"{'='*60}\n")

    def _log_tool(self, tool: str, status: str = "running"):
        """Log tool execution."""
        icon = "◉" if status == "running" else "✓" if status == "done" else "✗"
        print(f"  [{icon}] {tool}")

    async def _run_command(self, cmd: str, timeout: int = 300) -> tuple[int, str]:
        """Run a shell command asynchronously."""
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
            output = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
            return proc.returncode or 0, output
        except asyncio.TimeoutError:
            return -1, f"Command timed out after {timeout}s"
        except Exception as e:
            return -1, str(e)

    def _add_finding(self, finding: Finding):
        """Add a finding and trigger callback."""
        self.findings.append(finding)
        if self.on_finding:
            self.on_finding(finding)

    # ==================== RECON PHASE ====================

    async def run_recon(self) -> PhaseResult:
        """Execute reconnaissance phase."""
        phase = Phase.RECON
        started_at = datetime.now(timezone.utc).isoformat()
        start_time = time.time()
        findings = []
        tools_run = []
        errors = []

        if self.on_phase_start:
            self.on_phase_start(phase)

        self._log_phase(phase, f"Reconnaissance on {self.domain}")

        # 1. Subdomain Enumeration
        self._log_tool("Subdomain Enumeration")

        # Subfinder
        if "subfinder" in self.config.recon_tools:
            self._log_tool("subfinder", "running")
            # Security: Use safe_domain to prevent command injection
            ret, output = await self._run_command(
                f"subfinder -d {self.safe_domain} -silent 2>/dev/null"
            )
            if ret == 0:
                subs = [s.strip() for s in output.split("\n") if s.strip()]
                self.subdomains.extend(subs)
                (self.output_dir / f"subfinder_{self.domain}.txt").write_text(output)
                tools_run.append("subfinder")
                self._log_tool(f"subfinder - {len(subs)} subdomains", "done")

        # Assetfinder
        if "assetfinder" in self.config.recon_tools:
            self._log_tool("assetfinder", "running")
            # Security: Use safe_domain to prevent command injection
            ret, output = await self._run_command(
                f"assetfinder --subs-only {self.safe_domain} 2>/dev/null"
            )
            if ret == 0:
                subs = [s.strip() for s in output.split("\n") if s.strip()]
                self.subdomains.extend(subs)
                (self.output_dir / f"assetfinder_{self.domain}.txt").write_text(output)
                tools_run.append("assetfinder")
                self._log_tool(f"assetfinder - {len(subs)} assets", "done")

        # Deduplicate subdomains
        self.subdomains = list(set(self.subdomains))
        all_subs_file = self.output_dir / f"all_subs_{self.domain}.txt"
        all_subs_file.write_text("\n".join(self.subdomains))

        findings.append(Finding(
            type="subdomain_count",
            value=str(len(self.subdomains)),
            description=f"Discovered {len(self.subdomains)} unique subdomains",
            severity="info",
            phase="recon",
            tool="subdomain_enum",
            target=self.domain
        ))

        # 2. Live Host Detection with HTTPX
        if "httpx" in self.config.recon_tools and self.subdomains:
            self._log_tool("httpx", "running")
            subs_input = "\n".join(self.subdomains)

            ret, output = await self._run_command(
                f"echo '{subs_input}' | httpx -silent -status-code -title -tech-detect -json 2>/dev/null",
                timeout=180
            )
            if ret == 0:
                httpx_file = self.output_dir / "httpx_results.json"
                httpx_file.write_text(output)

                # Parse live hosts
                for line in output.split("\n"):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            url = data.get("url", "")
                            if url:
                                self.live_hosts.append(url)
                        except json.JSONDecodeError:
                            continue

                tools_run.append("httpx")
                self._log_tool(f"httpx - {len(self.live_hosts)} live hosts", "done")

                findings.append(Finding(
                    type="live_hosts",
                    value=str(len(self.live_hosts)),
                    description=f"Found {len(self.live_hosts)} live hosts",
                    severity="info",
                    phase="recon",
                    tool="httpx",
                    target=self.domain
                ))

        # 3. Port Scanning with Nmap
        if "nmap" in self.config.recon_tools:
            self._log_tool("nmap", "running")
            # Security: Use safe_domain to prevent command injection
            ret, output = await self._run_command(
                f"nmap -sV --top-ports 100 {self.safe_domain} 2>/dev/null",
                timeout=300
            )
            if ret == 0:
                (self.output_dir / f"nmap_{self.domain}.txt").write_text(output)
                tools_run.append("nmap")

                # Parse open ports
                for line in output.split("\n"):
                    if "/tcp" in line and "open" in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            port = parts[0]
                            service = parts[2] if len(parts) > 2 else "unknown"
                            findings.append(Finding(
                                type="open_port",
                                value=port,
                                description=f"Port {port} open running {service}",
                                severity="info",
                                phase="recon",
                                tool="nmap",
                                target=self.domain
                            ))

                self._log_tool("nmap - completed", "done")

        # 4. Wayback URLs
        if "waybackurls" in self.config.recon_tools:
            self._log_tool("waybackurls", "running")
            # Security: Use safe_domain to prevent command injection
            ret, output = await self._run_command(
                f"echo {self.safe_domain} | waybackurls 2>/dev/null | head -5000"
            )
            if ret == 0:
                (self.output_dir / f"wayback_{self.domain}.txt").write_text(output)
                url_count = len([u for u in output.split("\n") if u.strip()])
                tools_run.append("waybackurls")
                self._log_tool(f"waybackurls - {url_count} URLs", "done")

        # Add findings to global list
        for f in findings:
            self._add_finding(f)

        duration = time.time() - start_time
        result = PhaseResult(
            phase=phase,
            status="completed",
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat(),
            duration=duration,
            findings=findings,
            tools_run=tools_run,
            errors=errors,
            metadata={
                "subdomains_count": len(self.subdomains),
                "live_hosts_count": len(self.live_hosts)
            }
        )

        self.phase_results[phase] = result
        if self.on_phase_complete:
            self.on_phase_complete(result)

        return result

    # ==================== SCAN PHASE ====================

    async def run_scan(self) -> PhaseResult:
        """Execute vulnerability scanning phase."""
        phase = Phase.SCAN
        started_at = datetime.now(timezone.utc).isoformat()
        start_time = time.time()
        findings = []
        tools_run = []
        errors = []

        if self.on_phase_start:
            self.on_phase_start(phase)

        self._log_phase(phase, f"Vulnerability Scanning on {self.domain}")

        # 1. Nuclei Scanning
        if "nuclei" in self.config.scan_tools:
            self._log_tool("nuclei", "running")
            ret, output = await self._run_command(
                f"nuclei -u {self.target} -severity low,medium,high,critical -silent 2>/dev/null",
                timeout=600
            )
            if ret == 0:
                (self.output_dir / f"nuclei_{self.domain}.txt").write_text(output)
                tools_run.append("nuclei")

                # Parse nuclei findings
                for line in output.split("\n"):
                    if line.strip():
                        # Format: [template-id] [severity] [matched-at]
                        parts = line.split()
                        if len(parts) >= 2:
                            findings.append(Finding(
                                type="vulnerability",
                                value=parts[0] if parts else line,
                                description=line,
                                severity=self._parse_nuclei_severity(line),
                                phase="scan",
                                tool="nuclei",
                                target=self.domain
                            ))

                self._log_tool(f"nuclei - {len([f for f in findings if f.tool == 'nuclei'])} findings", "done")

        # 2. SSL/TLS Scanning
        if "sslscan" in self.config.scan_tools:
            self._log_tool("sslscan", "running")
            # Security: Use safe_domain to prevent command injection
            ret, output = await self._run_command(
                f"sslscan {self.safe_domain} 2>/dev/null"
            )
            if ret == 0:
                (self.output_dir / "sslscan_results.txt").write_text(output)
                tools_run.append("sslscan")

                # Check for weak ciphers
                if "Accepted" in output and ("RC4" in output or "DES" in output or "NULL" in output):
                    findings.append(Finding(
                        type="weak_cipher",
                        value="Weak TLS ciphers detected",
                        description="Server accepts weak cryptographic ciphers",
                        severity="medium",
                        phase="scan",
                        tool="sslscan",
                        target=self.domain
                    ))

                self._log_tool("sslscan - completed", "done")

        # 3. Directory Fuzzing
        if "ffuf" in self.config.scan_tools:
            self._log_tool("ffuf", "running")
            ret, output = await self._run_command(
                f"ffuf -u {self.target}/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302,403 -s 2>/dev/null | head -50",
                timeout=300
            )
            if ret == 0:
                (self.output_dir / f"ffuf_{self.domain}.txt").write_text(output)
                tools_run.append("ffuf")
                self._log_tool("ffuf - completed", "done")

        # 4. Acunetix DAST Scan (Enterprise)
        if self.config.use_acunetix:
            self._log_tool("Acunetix DAST", "running")
            try:
                acunetix = get_acunetix()
                if acunetix.connect():
                    # Start scan
                    profile_map = {
                        "full": ScanProfile.FULL_SCAN,
                        "high_risk": ScanProfile.HIGH_RISK,
                        "xss": ScanProfile.XSS_SCAN,
                        "sqli": ScanProfile.SQL_INJECTION,
                    }
                    profile = profile_map.get(self.config.acunetix_profile, ScanProfile.FULL_SCAN)

                    scan_id = acunetix.scan_url(self.target, profile, f"AIPT Scan - {self.timestamp}")
                    self.scan_ids["acunetix"] = scan_id

                    # Save scan info
                    scan_info = {
                        "scan_id": scan_id,
                        "target": self.target,
                        "profile": self.config.acunetix_profile,
                        "started_at": datetime.now(timezone.utc).isoformat(),
                        "dashboard_url": f"{acunetix.config.base_url}/#/scans/{scan_id}"
                    }
                    (self.output_dir / "acunetix_scan.json").write_text(json.dumps(scan_info, indent=2))

                    tools_run.append("acunetix")
                    self._log_tool(f"Acunetix - Scan started: {scan_id[:8]}...", "done")

                    # Optionally wait for completion
                    if self.config.wait_for_scanners:
                        self._log_tool("Acunetix - Waiting for completion...", "running")
                        result = acunetix.wait_for_scan(
                            scan_id,
                            timeout=self.config.scanner_timeout,
                            poll_interval=30
                        )

                        # Get vulnerabilities
                        vulns = acunetix.get_scan_vulnerabilities(scan_id)
                        for vuln in vulns:
                            findings.append(Finding(
                                type="vulnerability",
                                value=vuln.name,
                                description=vuln.description or vuln.name,
                                severity=vuln.severity,
                                phase="scan",
                                tool="acunetix",
                                target=vuln.affected_url,
                                metadata={
                                    "vuln_id": vuln.vuln_id,
                                    "cvss": vuln.cvss_score,
                                    "cwe": vuln.cwe_id
                                }
                            ))

                        self._log_tool(f"Acunetix - {len(vulns)} vulnerabilities found", "done")
                else:
                    errors.append("Acunetix connection failed")
                    self._log_tool("Acunetix - Connection failed", "error")
            except Exception as e:
                errors.append(f"Acunetix error: {str(e)}")
                self._log_tool(f"Acunetix - Error: {str(e)}", "error")

        # 5. Burp Suite Scan (Enterprise)
        if self.config.use_burp:
            self._log_tool("Burp Suite", "running")
            try:
                burp = get_burp()
                if burp.connect():
                    scan_id = burp.scan_url(self.target)
                    self.scan_ids["burp"] = scan_id
                    tools_run.append("burp")
                    self._log_tool(f"Burp Suite - Scan started: {scan_id}", "done")
                else:
                    errors.append("Burp Suite connection failed")
            except Exception as e:
                errors.append(f"Burp Suite error: {str(e)}")

        # Add findings to global list
        for f in findings:
            self._add_finding(f)

        duration = time.time() - start_time
        result = PhaseResult(
            phase=phase,
            status="completed",
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat(),
            duration=duration,
            findings=findings,
            tools_run=tools_run,
            errors=errors,
            metadata={
                "scan_ids": self.scan_ids
            }
        )

        self.phase_results[phase] = result
        if self.on_phase_complete:
            self.on_phase_complete(result)

        return result

    def _parse_nuclei_severity(self, line: str) -> str:
        """Parse severity from nuclei output line."""
        line_lower = line.lower()
        if "critical" in line_lower:
            return "critical"
        elif "high" in line_lower:
            return "high"
        elif "medium" in line_lower:
            return "medium"
        elif "low" in line_lower:
            return "low"
        return "info"

    # ==================== EXPLOIT PHASE ====================

    async def run_exploit(self) -> PhaseResult:
        """Execute exploitation/validation phase."""
        phase = Phase.EXPLOIT
        started_at = datetime.now(timezone.utc).isoformat()
        start_time = time.time()
        findings = []
        tools_run = []
        errors = []

        if self.on_phase_start:
            self.on_phase_start(phase)

        self._log_phase(phase, f"Vulnerability Validation on {self.domain}")

        # 1. Check Sensitive Endpoints
        if self.config.check_sensitive_paths:
            self._log_tool("Sensitive Path Check", "running")

            sensitive_paths = [
                "/metrics", "/actuator", "/actuator/health", "/actuator/env",
                "/.env", "/.git/config", "/swagger-ui.html", "/api/swagger",
                "/graphql", "/debug", "/admin", "/phpinfo.php",
                "/server-status", "/.aws/credentials", "/backup"
            ]

            for path in sensitive_paths:
                try:
                    ret, output = await self._run_command(
                        f"curl -s -o /dev/null -w '%{{http_code}}' '{self.target}{path}' --connect-timeout 5",
                        timeout=10
                    )
                    if ret == 0 and output.strip() in ["200", "301", "302"]:
                        severity = "high" if path in ["/.env", "/.git/config", "/.aws/credentials"] else "medium"
                        findings.append(Finding(
                            type="exposed_endpoint",
                            value=f"{self.target}{path}",
                            description=f"Sensitive endpoint accessible: {path} (HTTP {output.strip()})",
                            severity=severity,
                            phase="exploit",
                            tool="path_check",
                            target=self.target
                        ))
                except Exception:
                    continue

            exposed_count = len([f for f in findings if f.type == "exposed_endpoint"])
            tools_run.append("sensitive_path_check")
            self._log_tool(f"Sensitive Path Check - {exposed_count} exposed", "done")

        # 2. WAF Detection
        self._log_tool("WAF Detection", "running")
        ret, output = await self._run_command(
            f"curl -sI \"{self.target}/?id=1'%20OR%20'1'='1\" --connect-timeout 5 | head -1",
            timeout=10
        )
        waf_detected = "403" in output or "406" in output or "429" in output
        (self.output_dir / "waf_test.txt").write_text(f"WAF Test Response: {output}\nWAF Detected: {waf_detected}")
        tools_run.append("waf_detection")

        if not waf_detected:
            findings.append(Finding(
                type="waf_bypass",
                value="No WAF detected",
                description="Target does not appear to have a WAF or WAF is not blocking",
                severity="low",
                phase="exploit",
                tool="waf_detection",
                target=self.target
            ))
        self._log_tool(f"WAF Detection - {'Detected' if waf_detected else 'Not detected'}", "done")

        # 3. Fetch Acunetix Results (if scan completed)
        if "acunetix" in self.scan_ids and not self.config.wait_for_scanners:
            self._log_tool("Fetching Acunetix Results", "running")
            try:
                acunetix = get_acunetix()
                status = acunetix.get_scan_status(self.scan_ids["acunetix"])

                if status.status == "completed":
                    vulns = acunetix.get_scan_vulnerabilities(self.scan_ids["acunetix"])
                    for vuln in vulns:
                        findings.append(Finding(
                            type="vulnerability",
                            value=vuln.name,
                            description=vuln.description or vuln.name,
                            severity=vuln.severity,
                            phase="exploit",
                            tool="acunetix",
                            target=vuln.affected_url,
                            metadata={
                                "vuln_id": vuln.vuln_id,
                                "cvss": vuln.cvss_score
                            }
                        ))
                    self._log_tool(f"Acunetix Results - {len(vulns)} vulnerabilities", "done")
                else:
                    self._log_tool(f"Acunetix - Scan still {status.status} ({status.progress}%)", "done")
            except Exception as e:
                errors.append(f"Error fetching Acunetix results: {e}")

        # Add findings to global list
        for f in findings:
            self._add_finding(f)

        duration = time.time() - start_time
        result = PhaseResult(
            phase=phase,
            status="completed",
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat(),
            duration=duration,
            findings=findings,
            tools_run=tools_run,
            errors=errors
        )

        self.phase_results[phase] = result
        if self.on_phase_complete:
            self.on_phase_complete(result)

        return result

    # ==================== REPORT PHASE ====================

    async def run_report(self) -> PhaseResult:
        """Execute report generation phase."""
        phase = Phase.REPORT
        started_at = datetime.now(timezone.utc).isoformat()
        start_time = time.time()
        findings = []
        tools_run = []
        errors = []

        if self.on_phase_start:
            self.on_phase_start(phase)

        self._log_phase(phase, f"Generating Report for {self.domain}")

        # 1. Generate Summary
        summary = self._generate_summary()
        (self.output_dir / "SUMMARY.md").write_text(summary)
        tools_run.append("summary_generator")
        self._log_tool("Summary generated", "done")

        # 2. Generate Findings JSON
        findings_data = [
            {
                "type": f.type,
                "value": f.value,
                "description": f.description,
                "severity": f.severity,
                "phase": f.phase,
                "tool": f.tool,
                "target": f.target,
                "metadata": f.metadata,
                "timestamp": f.timestamp
            }
            for f in self.findings
        ]
        (self.output_dir / "findings.json").write_text(json.dumps(findings_data, indent=2))
        tools_run.append("findings_export")
        self._log_tool("Findings exported", "done")

        # 3. Generate HTML Report
        if self.config.report_format == "html":
            html_report = self._generate_html_report()
            report_file = self.output_dir / f"VAPT_Report_{self.domain.replace('.', '_')}.html"
            report_file.write_text(html_report)
            tools_run.append("html_report")
            self._log_tool(f"HTML Report: {report_file.name}", "done")

        duration = time.time() - start_time
        result = PhaseResult(
            phase=phase,
            status="completed",
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat(),
            duration=duration,
            findings=findings,
            tools_run=tools_run,
            errors=errors,
            metadata={
                "output_dir": str(self.output_dir),
                "total_findings": len(self.findings)
            }
        )

        self.phase_results[phase] = result
        if self.on_phase_complete:
            self.on_phase_complete(result)

        return result

    def _generate_summary(self) -> str:
        """Generate markdown summary."""
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in self.findings:
            sev = f.severity.lower()
            if sev in severity_counts:
                severity_counts[sev] += 1

        phases_info = []
        for phase, result in self.phase_results.items():
            phases_info.append(f"| {phase.value.upper()} | {result.status} | {result.duration:.1f}s | {len(result.findings)} |")

        return f"""# AIPT Scan Summary

## Target Information
- **Domain**: {self.domain}
- **Target URL**: {self.target}
- **Scan Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Report ID**: VAPT-{self.domain.upper().replace('.', '-')}-{datetime.now().strftime('%Y%m%d')}

## Vulnerability Summary
| Severity | Count |
|----------|-------|
| 🔴 Critical | {severity_counts['critical']} |
| 🟠 High | {severity_counts['high']} |
| 🟡 Medium | {severity_counts['medium']} |
| 🔵 Low | {severity_counts['low']} |
| ⚪ Info | {severity_counts['info']} |
| **Total** | **{len(self.findings)}** |

## Phase Results
| Phase | Status | Duration | Findings |
|-------|--------|----------|----------|
{chr(10).join(phases_info)}

## Scanner IDs
{json.dumps(self.scan_ids, indent=2) if self.scan_ids else 'No enterprise scans'}

## Assets Discovered
- Subdomains: {len(self.subdomains)}
- Live Hosts: {len(self.live_hosts)}

## Output Directory
{self.output_dir}
"""

    def _generate_html_report(self) -> str:
        """Generate HTML report."""
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in self.findings:
            sev = f.severity.lower()
            if sev in severity_counts:
                severity_counts[sev] += 1

        findings_html = ""
        for f in self.findings:
            sev_class = f.severity.lower()
            findings_html += f"""
            <div class="finding {sev_class}">
                <div class="finding-header">
                    <span class="severity-badge {sev_class}">{f.severity.upper()}</span>
                    <span class="finding-title">{f.value}</span>
                    <span class="finding-tool">{f.tool}</span>
                </div>
                <div class="finding-body">
                    <p>{f.description}</p>
                    <small>Target: {f.target or self.target} | Phase: {f.phase}</small>
                </div>
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VAPT Report - {self.domain}</title>
    <style>
        :root {{
            --critical: #dc3545;
            --high: #fd7e14;
            --medium: #ffc107;
            --low: #17a2b8;
            --info: #6c757d;
        }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0 0 10px 0; }}
        .stats {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 30px; }}
        .stat {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat .number {{ font-size: 2em; font-weight: bold; }}
        .stat.critical .number {{ color: var(--critical); }}
        .stat.high .number {{ color: var(--high); }}
        .stat.medium .number {{ color: var(--medium); }}
        .stat.low .number {{ color: var(--low); }}
        .stat.info .number {{ color: var(--info); }}
        .findings {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .finding {{ border-left: 4px solid; padding: 15px; margin-bottom: 15px; background: #fafafa; border-radius: 0 5px 5px 0; }}
        .finding.critical {{ border-color: var(--critical); }}
        .finding.high {{ border-color: var(--high); }}
        .finding.medium {{ border-color: var(--medium); }}
        .finding.low {{ border-color: var(--low); }}
        .finding.info {{ border-color: var(--info); }}
        .finding-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
        .severity-badge {{ padding: 3px 8px; border-radius: 3px; font-size: 0.8em; color: white; }}
        .severity-badge.critical {{ background: var(--critical); }}
        .severity-badge.high {{ background: var(--high); }}
        .severity-badge.medium {{ background: var(--medium); }}
        .severity-badge.low {{ background: var(--low); }}
        .severity-badge.info {{ background: var(--info); }}
        .finding-title {{ font-weight: bold; flex-grow: 1; }}
        .finding-tool {{ color: #666; font-size: 0.9em; }}
        .finding-body p {{ margin: 0 0 10px 0; }}
        .finding-body small {{ color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 VAPT Report</h1>
            <p><strong>Target:</strong> {self.domain}</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Report ID:</strong> VAPT-{self.domain.upper().replace('.', '-')}-{datetime.now().strftime('%Y%m%d')}</p>
        </div>

        <div class="stats">
            <div class="stat critical"><div class="number">{severity_counts['critical']}</div><div>Critical</div></div>
            <div class="stat high"><div class="number">{severity_counts['high']}</div><div>High</div></div>
            <div class="stat medium"><div class="number">{severity_counts['medium']}</div><div>Medium</div></div>
            <div class="stat low"><div class="number">{severity_counts['low']}</div><div>Low</div></div>
            <div class="stat info"><div class="number">{severity_counts['info']}</div><div>Info</div></div>
        </div>

        <div class="findings">
            <h2>Findings ({len(self.findings)})</h2>
            {findings_html if findings_html else '<p>No vulnerabilities found.</p>'}
        </div>

        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>Generated by AIPT - AI-Powered Penetration Testing</p>
            <p>Scanners: {', '.join(self.scan_ids.keys()) if self.scan_ids else 'Open Source Tools'}</p>
        </div>
    </div>
</body>
</html>"""

    # ==================== MAIN RUNNER ====================

    async def run(self, phases: Optional[List[Phase]] = None) -> Dict[str, Any]:
        """
        Run the full orchestration pipeline.

        Args:
            phases: Optional list of phases to run (default: all)

        Returns:
            Complete results dictionary
        """
        if phases is None:
            phases = [Phase.RECON, Phase.SCAN, Phase.EXPLOIT, Phase.REPORT]

        start_time = time.time()

        print("\n" + "="*60)
        print("  AIPT - AI-Powered Penetration Testing")
        print("="*60)
        print(f"  Target: {self.domain}")
        print(f"  Output: {self.output_dir}")
        print(f"  Acunetix: {'Enabled' if self.config.use_acunetix else 'Disabled'}")
        print(f"  Burp: {'Enabled' if self.config.use_burp else 'Disabled'}")
        print("="*60 + "\n")

        try:
            if Phase.RECON in phases and not self.config.skip_recon:
                await self.run_recon()

            if Phase.SCAN in phases and not self.config.skip_scan:
                await self.run_scan()

            if Phase.EXPLOIT in phases and not self.config.skip_exploit:
                await self.run_exploit()

            if Phase.REPORT in phases and not self.config.skip_report:
                await self.run_report()

        except Exception as e:
            logger.exception(f"Orchestration error: {e}")
            raise

        total_duration = time.time() - start_time

        # Final summary
        print("\n" + "="*60)
        print("  SCAN COMPLETE")
        print("="*60)
        print(f"  Duration: {total_duration:.1f}s")
        print(f"  Findings: {len(self.findings)}")
        print(f"  Output: {self.output_dir}")
        print("="*60 + "\n")

        return {
            "target": self.target,
            "domain": self.domain,
            "duration": total_duration,
            "phases": {p.value: r.__dict__ for p, r in self.phase_results.items()},
            "findings_count": len(self.findings),
            "scan_ids": self.scan_ids,
            "output_dir": str(self.output_dir)
        }


# ==================== CLI ====================

async def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AIPT Orchestrator - Full Penetration Testing Pipeline"
    )
    parser.add_argument("target", help="Target domain or URL")
    parser.add_argument("-o", "--output", default="./scan_results", help="Output directory")
    parser.add_argument("--skip-recon", action="store_true", help="Skip reconnaissance phase")
    parser.add_argument("--skip-scan", action="store_true", help="Skip scanning phase")
    parser.add_argument("--skip-exploit", action="store_true", help="Skip exploitation phase")
    parser.add_argument("--no-acunetix", action="store_true", help="Disable Acunetix")
    parser.add_argument("--no-burp", action="store_true", help="Disable Burp Suite")
    parser.add_argument("--wait", action="store_true", help="Wait for enterprise scanners")
    parser.add_argument("--acunetix-profile", default="full",
                       choices=["full", "high_risk", "xss", "sqli"],
                       help="Acunetix scan profile")

    args = parser.parse_args()

    config = OrchestratorConfig(
        target=args.target,
        output_dir=args.output,
        skip_recon=args.skip_recon,
        skip_scan=args.skip_scan,
        skip_exploit=args.skip_exploit,
        use_acunetix=not args.no_acunetix,
        use_burp=not args.no_burp,
        wait_for_scanners=args.wait,
        acunetix_profile=args.acunetix_profile
    )

    orchestrator = Orchestrator(args.target, config)
    results = await orchestrator.run()

    print(f"\n✓ Results saved to: {results['output_dir']}")


if __name__ == "__main__":
    asyncio.run(main())
