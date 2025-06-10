#!/usr/bin/env python3
"""
Wrapper script to ensure proper path resolution for MCP server
"""

import sys
import os

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the script directory to Python path
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Now import and run the actual server
try:
    from server_mcp import mcp
    mcp.run()
except Exception as e:
    # Write error to stderr so it shows up in Claude Desktop logs
    print(f"MCP Server Error: {e}", file=sys.stderr)
    sys.exit(1)