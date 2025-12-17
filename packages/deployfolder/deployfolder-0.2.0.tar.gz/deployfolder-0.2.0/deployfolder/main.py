#!/usr/bin/env python3
"""
DeployFolder - A tool to create deployment folders based on YAML configuration.

Copyright (c) 2025 Janosch Meyer (janosch.code@proton.me)
This project is licensed under the MIT License - see the LICENSE file for details.
This project was created with the assistance of artificial intelligence.

This tool creates a folder structure based on a YAML configuration file.
It can copy files from source to target paths, with optional renaming.
It supports placeholders in filenames and folder names that can be replaced with values from a JSON file.
It can create empty folders and optionally zip the created folder.
"""

import os
import sys
import yaml
import json
import shutil
import zipfile
import re
import glob
import tarfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from jinja2 import Template, Environment, FileSystemLoader


def replace_placeholders(text: str, values: Dict[str, Any]) -> str:
    """
    Replace placeholders in the format {{ name }} with values from the provided dictionary.
    
    Args:
        text: The text containing placeholders
        values: Dictionary with values to replace placeholders
        
    Returns:
        Text with placeholders replaced by their values
    """
    if not text or not values:
        return text
        
    pattern = r"{{[\s]*([^{}]+)[\s]*}}"
    
    def replace_match(match):
        key = match.group(1).strip()
        
        # Handle nested JSON with dot notation (e.g., "user.name")
        if '.' in key and key not in values:
            parts = key.split('.')
            current = values
            found = True
            
            # Traverse the nested dictionary
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    found = False
                    break
            
            if found:
                return str(current)
        elif key in values:
            return str(values[key])
            
        return match.group(0)  # Keep original if not found
    
    return re.sub(pattern, replace_match, text)


def create_empty_folder(target_path: Path) -> None:
    """
    Create an empty folder at the specified path.
    
    Args:
        target_path: Path where the folder should be created
    """
    target_path.mkdir(parents=True, exist_ok=True)


def copy_file(source_path: Path, target_path: Path) -> None:
    """
    Copy a file from source to target path.
    
    Args:
        source_path: Path to the source file
        target_path: Path where the file should be copied
    """
    # Create target directory if it doesn't exist
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy the file
    shutil.copy2(source_path, target_path)


def archive_folder(
    folder_path: Path, 
    archive_path: Optional[Path] = None,
    format: str = "zip", # möglich sind "zip", "tar", "7z"
    method: Optional[str] = None,
    level: Optional[int] = None
) -> Path:
    """
    Archive a folder using the specified format and compression method.
    
    Args:
        folder_path: Path to the folder to be archived
        archive_path: Path where the archive file should be created (default: folder_path.{format})
        format: Archive format ("zip", "tar", or "7z")
        method: Compression method 
            - For zip: "stored", "deflated", "bzip2", "lzma" (default: "lzma")
            - For tar: "gz", "bz2", "xz" (default: no compression)
            - For 7z: compression method is handled by py7zr
        level: Compression level (if applicable)
        
    Returns:
        Path to the created archive file
    """
    # Handle ZIP format
    if format == "zip":
        # Set default archive path if not provided
        if archive_path is None:
            archive_path = folder_path.with_suffix(".zip")

        # Map compression method names to zipfile constants
        compression_methods = {
            "stored": zipfile.ZIP_STORED,
            "deflated": zipfile.ZIP_DEFLATED,
            "bzip2": zipfile.ZIP_BZIP2,
            "lzma": zipfile.ZIP_LZMA
        }
        
        # Default to LZMA if method not specified or invalid
        compression = compression_methods.get(method or "lzma", zipfile.ZIP_LZMA)
        
        # Create the zip file
        with zipfile.ZipFile(archive_path, 'w', compression, compresslevel=level) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
    
    # Handle TAR format
    elif format == "tar":
        # Map compression method to file extension and mode
        tar_modes = {
            "gz": ("w:gz", ".tar.gz"),
            "bz2": ("w:bz2", ".tar.bz2"),
            "xz": ("w:xz", ".tar.xz"),
            None: ("w", ".tar")
        }
        
        # Get mode and correct extension
        mode, correct_ext = tar_modes.get(method, tar_modes[None])
        
        # If no specific archive_path was provided, use the correct extension
        if archive_path is None:
            archive_path = folder_path.with_suffix(correct_ext)
        
        # Create the tar file
        with tarfile.open(archive_path, mode) as tarf:
            # Add the folder to the tar file
            tarf.add(folder_path, arcname=folder_path.name)
    
    # Handle 7z format
    elif format == "7z":
        try:
            import py7zr
            
            # Ensure the file has .7z extension
            if archive_path is None:
                archive_path = folder_path.with_suffix('.7z')

            # Ensure the file has .7z extension
            if not str(archive_path).endswith('.7z'):
                archive_path = Path(str(archive_path) + '.7z')
            
            # Create the 7z file
            with py7zr.SevenZipFile(archive_path, 'w') as szf:
                szf.writeall(folder_path, folder_path.name)
                
        except ImportError:
            print("Error: py7zr module not installed. Please install it with 'pip install py7zr'", file=sys.stderr)
            raise
    
    else:
        raise ValueError(f"Unsupported archive format: {format}")
    
    return archive_path


def render_template(template_content: str, target_path: Path, values: Dict[str, Any]) -> None:
    """
    Render a Jinja2 template and save it to the target path.
    
    Args:
        template_content: The template content as a string
        target_path: Path where the rendered template should be saved
        values: Dictionary with values for template rendering
    """
    # Create target directory if it doesn't exist
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Render the template
    template = Template(template_content)
    rendered_content = template.render(**values)
    
    # Save the rendered content to the target path
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(rendered_content)


def render_template_file(template_path: Path, target_path: Path, values: Dict[str, Any]) -> None:
    """
    Render a Jinja2 template from a file and save it to the target path.
    
    Args:
        template_path: Path to the template file
        target_path: Path where the rendered template should be saved
        values: Dictionary with values for template rendering
    """
    # Create target directory if it doesn't exist
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Set up Jinja2 environment with the template file's directory as the loader
    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)
    
    # Render the template
    rendered_content = template.render(**values)
    
    # Save the rendered content to the target path
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(rendered_content)


def process_config(config: Dict[str, Any], values: Optional[Dict[str, Any]] = None) -> Path:
    """
    Process the configuration and create the deployment folder.
    
    Args:
        config: Configuration dictionary from YAML
        values: Values dictionary from JSON for placeholder replacement
        
    Returns:
        Path to the created deployment folder
    """
    if values is None:
        values = {}
    
    # Get the output folder name with placeholders replaced
    output_folder_name = config.get('output_folder', 'deploy')
    output_folder_name = replace_placeholders(output_folder_name, values)
    output_folder = Path(output_folder_name)
    
    # Create the output folder
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Process files
    files = config.get('files', [])
    for file_config in files:
        if isinstance(file_config, str):
            # Simple case: just a source path, keep the filename
            # Check if the path contains glob patterns
            if any(c in file_config for c in ['*', '?', '[']):
                # Handle glob pattern
                for source_file in glob.glob(file_config):
                    source_path = Path(source_file)
                    target_path = output_folder / source_path.name
                    copy_file(source_path, target_path)
            else:
                # Handle single file
                source_path = Path(file_config)
                target_path = output_folder / source_path.name
                copy_file(source_path, target_path)
        elif isinstance(file_config, dict):
            # Complex case: source, target, directory, and possibly rename
            source = file_config.get('source')
            target = file_config.get('target')
            directory = file_config.get('directory')
            
            if source is None:
                # Create empty folder
                if target:
                    target_path = replace_placeholders(target, values)
                    create_empty_folder(output_folder / target_path)
            else:
                # Check if the source contains glob patterns
                if any(c in source for c in ['*', '?', '[']):
                    # Handle glob pattern
                    for source_file in glob.glob(source):
                        source_path = Path(source_file)
                        
                        if target is None:
                            if directory is not None:
                                # Use source filename in specified directory
                                directory = replace_placeholders(directory, values)
                                target_path = output_folder / directory / source_path.name
                            else:
                                # Use source filename in root directory
                                target_path = output_folder / source_path.name
                        else:
                            # For glob patterns with explicit target, we need to handle multiple files
                            # If target ends with / or \, treat it as a directory
                            target_str = replace_placeholders(target, values)
                            if target_str.endswith('/') or target_str.endswith('\\'):
                                # Use as directory
                                target_path = output_folder / target_str / source_path.name
                            else:
                                # For single file target with multiple sources, use only the first file
                                # This maintains backward compatibility with existing behavior
                                target_path = output_folder / target_str
                        
                        copy_file(source_path, target_path)
                else:
                    # Handle single file
                    source_path = Path(source)
                    
                    if target is None:
                        if directory is not None:
                            # Use source filename in specified directory
                            directory = replace_placeholders(directory, values)
                            target_path = output_folder / directory / source_path.name
                        else:
                            # Use source filename in root directory
                            target_path = output_folder / source_path.name
                    else:
                        # Use specified target path/name
                        target = replace_placeholders(target, values)
                        target_path = output_folder / target
                    
                    copy_file(source_path, target_path)
    
    # Process templates
    templates = config.get('templates', [])
    for template_config in templates:
        if isinstance(template_config, dict):
            # Get template configuration
            template_content = template_config.get('content')
            template_file = template_config.get('file')
            target = template_config.get('target')
            
            if target is None:
                # Target is required for templates
                print("Warning: Skipping template without target path", file=sys.stderr)
                continue
            
            # Replace placeholders in target path
            target = replace_placeholders(target, values)
            target_path = output_folder / target
            
            if template_content is not None:
                # Render template from content
                render_template(template_content, target_path, values)
            elif template_file is not None:
                # Render template from file
                template_path = Path(template_file)
                render_template_file(template_path, target_path, values)
            else:
                # Either content or file is required
                print("Warning: Skipping template without content or file", file=sys.stderr)
    
    # Archive the folder if requested
    # Check for new archive configuration
    archive_config = config.get('archive', None)
    
    # Handle archiving based on configuration
    if archive_config is not None:
        # Configuration format
        if isinstance(archive_config, dict):
            format = archive_config.get('format', 'zip')
            method = archive_config.get('method', None)
            level = archive_config.get('level', None)
            
            archive_path = archive_folder(
                output_folder,
                format=format,
                method=method,
                level=level
            )
            print(f"Created {format} archive: {archive_path}")
        # Boolean value
        elif archive_config:
            archive_path = archive_folder(output_folder)
            print(f"Created archive: {archive_path}")
    
    return output_folder
