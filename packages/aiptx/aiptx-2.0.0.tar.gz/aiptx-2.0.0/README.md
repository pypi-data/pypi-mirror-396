# AIPTX - AI-Powered Penetration Testing Framework

[![PyPI version](https://badge.fury.io/py/aiptx.svg)](https://badge.fury.io/py/aiptx)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Zero-click security scanning with LLM intelligence.** AIPTX automates penetration testing workflows using AI-guided decision making and integrates with enterprise security scanners.

## Features

- **AI-Guided Scanning** - LLM-powered decision making for intelligent vulnerability discovery
- **Enterprise Scanner Integration** - Acunetix, Burp Suite, Nessus, OWASP ZAP
- **Automated Reconnaissance** - Subdomain enumeration, port scanning, technology detection
- **Professional Reports** - HTML, JSON, and summary reports
- **VPS Execution** - Run tools remotely via SSH
- **Extensible Architecture** - Plugin system for custom tools and scanners

## Installation

```bash
# Zero-click install (recommended)
pipx install aiptx

# Or with pip
pip install aiptx

# Full installation with all features
pip install aiptx[full]
```

## Quick Start

```bash
# Run a basic scan
aiptx scan example.com

# Full comprehensive scan
aiptx scan example.com --full

# AI-guided scanning (requires API key)
aiptx scan example.com --ai

# Check configuration
aiptx status

# Start REST API server
aiptx api
```

## Configuration

Set environment variables for API keys and scanner integration:

```bash
# LLM Configuration
export ANTHROPIC_API_KEY="your-key"
# or
export OPENAI_API_KEY="your-key"

# Scanner Configuration
export ACUNETIX_URL="https://your-acunetix:3443"
export ACUNETIX_API_KEY="your-api-key"

export BURP_URL="http://your-burp:1337"
export BURP_API_KEY="your-api-key"

# VPS Configuration (for remote execution)
export VPS_HOST="your-vps-ip"
export VPS_USER="ubuntu"
export VPS_KEY="~/.ssh/your-key.pem"
```

## Commands

| Command | Description |
|---------|-------------|
| `aiptx scan <target>` | Run security scan against target |
| `aiptx scan <target> --ai` | AI-guided intelligent scanning |
| `aiptx scan <target> --full` | Comprehensive scan with all tools |
| `aiptx status` | Check configuration and dependencies |
| `aiptx version` | Show version information |
| `aiptx api` | Start REST API server |

## Scan Modes

- **quick** - Fast scan with essential tools
- **standard** - Balanced scan (default)
- **full** - Comprehensive scan with all available tools
- **ai** - AI-guided scanning with LLM decision making

## Requirements

- Python 3.10+
- For full features: Docker (optional), SSH access to VPS (optional)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Satyam Rastogi** - [GitHub](https://github.com/satyamrastogi)

## Links

- [Documentation](https://aiptx.io/docs)
- [GitHub Repository](https://github.com/satyamrastogi/aiptx)
- [Issue Tracker](https://github.com/satyamrastogi/aiptx/issues)
