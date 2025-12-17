"""
DeployFolder - A tool to create deployment folders based on YAML configuration.

Copyright (c) 2025 Janosch Meyer (janosch.code@proton.me)
This project is licensed under the MIT License - see the LICENSE file for details.
This project was created with the assistance of artificial intelligence.

This package provides tools to create deployment folders based on YAML configuration.
It can copy files from source to target paths, with optional renaming.
It supports placeholders in filenames and folder names that can be replaced with values from a JSON file.
It can create empty folders and optionally zip the created folder.
"""

__version__ = '0.2.0'

# Import and expose public functions
from .main import (
    replace_placeholders,
    create_empty_folder,
    copy_file,
    archive_folder,
    process_config,
    render_template,
    render_template_file
)

__all__ = [
    'replace_placeholders',
    'create_empty_folder',
    'copy_file',
    'archive_folder',
    'process_config',
    'render_template',
    'render_template_file'
]