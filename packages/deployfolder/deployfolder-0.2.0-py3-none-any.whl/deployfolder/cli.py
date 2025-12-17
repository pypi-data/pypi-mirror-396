#!/usr/bin/env python3
"""
Command-line interface for DeployFolder.

Copyright (c) 2025 Janosch Meyer (janosch.code@proton.me)
This project is licensed under the MIT License - see the LICENSE file for details.
This project was created with the assistance of artificial intelligence.

This module provides the command-line interface for the DeployFolder tool.
"""

import sys
import argparse
import yaml
import json
from pathlib import Path

# --- magic so that "from .main ..." auch als direktes Skript klappt ---
if __name__ == "__main__" and (not __package__):
    # Pfad so setzen, dass das Parent-Verzeichnis importierbar ist
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "deployfolder"   # <== deinen Paketnamen hier eintragen
# ----------------------------------------------------------------------

from .main import process_config


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Create deployment folders based on YAML configuration.')
    parser.add_argument('config', help='Path to the YAML configuration file')
    parser.add_argument('--values', help='Path to the JSON values file for placeholder replacement')
    parser.add_argument('--version', action='store_true', help='Show version information and exit')
    
    args = parser.parse_args()
    
    # Show version information if requested
    if args.version:
        from . import __version__
        print(f"DeployFolder version {__version__}")
        return 0
    
    # Load configuration
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration file: {e}", file=sys.stderr)
        return 1
    
    # Load values if provided
    values = None
    if args.values:
        try:
            with open(args.values, 'r', encoding='utf-8') as f:
                values = json.load(f)
        except Exception as e:
            print(f"Error loading values file: {e}", file=sys.stderr)
            return 1
    
    # Process configuration
    try:
        output_folder = process_config(config, values)
        print(f"Deployment folder created successfully: {output_folder}")
        return 0
    except Exception as e:
        print(f"Error creating deployment folder: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())