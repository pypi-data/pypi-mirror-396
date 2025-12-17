"""
AIPT v2 - AI-Powered Penetration Testing Framework
===================================================

A unified penetration testing framework built on top of 8 reference tools:
- AIPTx: LLM (litellm), Runtime (Docker), Tools (Browser, Terminal, Proxy)
- pentest-agent: CVE Intelligence with EPSS scoring
- PentestAssistant: RAG-based tool selection with BGE embeddings
- PentestGPT: PTT (Penetration Testing Tree) task tracking
- VulnBot: Output parsing patterns
- HackSynth: Multi-step reasoning
- Pentagi: Docker isolation
- ez-ai-agent: Simple execution model

Features:
- Universal LLM support via litellm (100+ models)
- Docker sandbox execution
- Browser automation via Playwright
- Proxy interception via mitmproxy
- CVE prioritization (CVSS + EPSS + trending + POC)
- RAG tool selection with semantic search
- Hierarchical task tracking
- SQLAlchemy persistence
- FastAPI REST API
"""

__version__ = "2.0.0"
__author__ = "AIPT Team"

# Lazy imports to avoid failures when optional dependencies are missing


def __getattr__(name):
    """Lazy import handler for optional dependencies"""
    if name == "LLM":
        from llm.llm import LLM
        return LLM
    elif name == "LLMConfig":
        from llm.config import LLMConfig
        return LLMConfig
    elif name == "PTT":
        from agents.ptt import PTT
        return PTT
    elif name == "BaseAgent":
        from agents.base import BaseAgent
        return BaseAgent
    elif name == "CVEIntelligence":
        from intelligence.cve_aipt import CVEIntelligence
        return CVEIntelligence
    elif name == "ToolRAG":
        from intelligence.rag import ToolRAG
        return ToolRAG
    elif name == "OutputParser":
        from tools.parser import OutputParser
        return OutputParser
    elif name == "Repository":
        from database.repository import Repository
        return Repository
    raise AttributeError(f"module 'aipt_v2' has no attribute '{name}'")
