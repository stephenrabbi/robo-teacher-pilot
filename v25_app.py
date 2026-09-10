"""Backward-compatible Robo-Teacher V2.5 staging entrypoint.

The classroom API and classroom page are registered by ``main`` so production
and staging exercise the same application path. Staging may continue to start
this module without adding route-specific middleware.
"""

from main import app
