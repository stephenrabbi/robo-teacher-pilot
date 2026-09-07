"""Backward-compatible Robo-Teacher V2.5 staging entrypoint.

The classroom API is registered by ``main`` so production and staging expose
the same browser endpoints. Staging may continue to run this module.
"""
from main import app
