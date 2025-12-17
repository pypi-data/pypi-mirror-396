#!/usr/bin/env python3
"""
sheikh-cli - Termux Local Coding Agent
A privacy-first AI coding assistant that runs entirely on your Android device.
"""

from .main import app, CodingAgent, load_config
from .session_manager import session_manager
from .workflow_orchestrator import workflow_orchestrator
from .advanced_config import config_manager

__version__ = "1.0.0"
__author__ = "MiniMax Agent"
__description__ = "Privacy-first AI coding assistant for Termux"

__all__ = ["app", "CodingAgent", "load_config", "session_manager", "workflow_orchestrator", "config_manager"]
