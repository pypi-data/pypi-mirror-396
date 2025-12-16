#!/usr/bin/env python3
"""Command-line interface for Polarion MCP Server."""

import sys
from .server import run

def main():
    """Main entry point for the CLI."""
    try:
        run()
    except KeyboardInterrupt:
        print("\nShutting down Polarion MCP Server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
