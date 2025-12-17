#!/usr/bin/env python3
"""
sheikh-cli - Termux Local Coding Agent
A privacy-first AI coding assistant that runs entirely on your Android device.
"""

from .main import app
from .agent import CodingAgent, load_config

__version__ = "1.0.0"
__author__ = "MiniMax Agent"
__description__ = "Privacy-first AI coding assistant for Termux"

__all__ = ["app", "CodingAgent", "load_config"]
