"""
Entry point for MCPB / IDE discovery (stdio).

Delegates to :func:`gimp_mcp.main.main` which runs the full portmanteau + SOTA stack.
"""

from __future__ import annotations

import sys

from .main import main

if __name__ == "__main__":
    sys.exit(main())


__all__ = ["main"]
