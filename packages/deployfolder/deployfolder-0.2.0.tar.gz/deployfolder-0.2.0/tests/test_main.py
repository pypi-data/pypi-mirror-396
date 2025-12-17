"""
Unit tests for the DeployFolder tool.

Copyright (c) 2025 Janosch Meyer (janosch.code@proton.me)
This project is licensed under the MIT License - see the LICENSE file for details.
This project was created with the assistance of artificial intelligence.
"""

import unittest
import os
import sys
import json
import zipfile
import tarfile
import yaml
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import functions from deployfolder package
from deployfolder import (
    replace_placeholders,
    create_empty_folder,
    copy_file,
    archive_folder,
    process_config,
    render_template,
    render_template_file
)
from deployfolder.cli import main

class TestReplacePlaceholders(unittest.TestCase):
    """Test cases for the replace_placeholders function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Test values with nested JSON
        self.values = {
            "project_name": "MyProject",
            "environment": "production",
            "date": "2025-11-08",
            "user": {
                "name": "JohnDoe",
                "role": "admin"
            },
            "database": {
                "host": "db.example.com",
                "port": 5432,
                "credentials": {
                    "username": "dbuser",
                    "password": "secret"
                }
            }
        }
    
    def test_basic_placeholder_replacement(self):
        """Test basic placeholder replacement."""
        # Test with a simple placeholder
        text = "Project: {{ project_name }}"
        expected = "Project: MyProject"
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
        
        # Test with multiple placeholders
        text = "Project: {{ project_name }}, Environment: {{ environment }}"
        expected = "Project: MyProject, Environment: production"
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
    
    def test_nested_json_placeholder_replacement(self):
        """Test nested JSON placeholder replacement."""
        # Test with first-level nested placeholder
        text = "User: {{ user.name }}"
        expected = "User: JohnDoe"
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
        
        # Test with second-level nested placeholder
        text = "DB Host: {{ database.host }}"
        expected = "DB Host: db.example.com"
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
        
        # Test with deeply nested placeholder
        text = "DB User: {{ database.credentials.username }}"
        expected = "DB User: dbuser"
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
        
        # Test with numeric value
        text = "DB Port: {{ database.port }}"
        expected = "DB Port: 5432"
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
        
        # Test with multiple nested placeholders
        text = "{{ user.name }} is an {{ user.role }} on {{ database.host }}"
        expected = "JohnDoe is an admin on db.example.com"
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
    
    def test_edge_cases(self):
        """Test edge cases for placeholder replacement."""
        # Test with empty text
        text = ""
        expected = ""
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
        
        # Test with None text
        text = None
        expected = None
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
        
        # Test with empty values
        text = "Project: {{ project_name }}"
        expected = "Project: {{ project_name }}"
        result = replace_placeholders(text, {})
        self.assertEqual(result, expected)
        
        # Test with None values
        text = "Project: {{ project_name }}"
        expected = "Project: {{ project_name }}"
        result = replace_placeholders(text, None)
        self.assertEqual(result, expected)
        
        # Test with non-existent placeholder
        text = "Missing: {{ nonexistent.key }}"
        expected = "Missing: {{ nonexistent.key }}"
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)
        
        # Test with mixed existing and non-existent placeholders
        text = "{{ user.name }} has {{ nonexistent.key }}"
        expected = "JohnDoe has {{ nonexistent.key }}"
        result = replace_placeholders(text, self.values)
        self.assertEqual(result, expected)


class TestFileOperations(unittest.TestCase):
    """Test cases for file operations functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_content = "This is a test file."
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.temp_dir)
    
    def test_create_empty_folder(self):
        """Test creating an empty folder."""
        # Test creating a new folder
        folder_path = Path(self.temp_dir) / "test_folder"
        create_empty_folder(folder_path)
        self.assertTrue(folder_path.exists())
        self.assertTrue(folder_path.is_dir())
        
        # Test with existing folder (should not raise an exception)
        create_empty_folder(folder_path)
        self.assertTrue(folder_path.exists())
        
        # Test creating nested folders
        nested_folder_path = Path(self.temp_dir) / "parent" / "child" / "grandchild"
        create_empty_folder(nested_folder_path)
        self.assertTrue(nested_folder_path.exists())
        self.assertTrue(nested_folder_path.is_dir())
    
    def test_copy_file(self):
        """Test copying a file."""
        # Create a test file
        source_path = Path(self.temp_dir) / "source.txt"
        with open(source_path, "w") as f:
            f.write(self.test_file_content)
        
        # Test copying to a new location
        target_path = Path(self.temp_dir) / "target.txt"
        copy_file(source_path, target_path)
        self.assertTrue(target_path.exists())
        with open(target_path, "r") as f:
            content = f.read()
        self.assertEqual(content, self.test_file_content)
        
        # Test copying to a non-existent directory (should create the directory)
        target_path = Path(self.temp_dir) / "subdir" / "target.txt"
        copy_file(source_path, target_path)
        self.assertTrue(target_path.exists())
        with open(target_path, "r") as f:
            content = f.read()
        self.assertEqual(content, self.test_file_content)
    
    def test_archive_folder(self):
        """Test archiving a folder."""
        # Create a test folder with files
        folder_path = Path(self.temp_dir) / "test_folder"
        folder_path.mkdir()
        file1_path = folder_path / "file1.txt"
        file2_path = folder_path / "file2.txt"
        with open(file1_path, "w") as f:
            f.write("File 1 content")
        with open(file2_path, "w") as f:
            f.write("File 2 content")
        
        # Test archiving with default path
        archive_path = archive_folder(folder_path)
        self.assertTrue(archive_path.exists())
        self.assertEqual(archive_path, folder_path.with_suffix('.zip'))
        
        # Test archiving with custom path
        custom_archive_path = Path(self.temp_dir) / "custom.zip"
        archive_path = archive_folder(folder_path, custom_archive_path)
        self.assertTrue(archive_path.exists())
        self.assertEqual(archive_path, custom_archive_path)


class TestProcessConfig(unittest.TestCase):
    """Test cases for the process_config function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_file1 = Path(self.temp_dir) / "file1.txt"
        self.test_file2 = Path(self.temp_dir) / "file2.txt"
        with open(self.test_file1, "w") as f:
            f.write("File 1 content")
        with open(self.test_file2, "w") as f:
            f.write("File 2 content")
        
        # Test values with nested JSON
        self.values = {
            "project_name": "MyProject",
            "environment": "production",
            "date": "2025-11-08",
            "user": {
                "name": "JohnDoe",
                "role": "admin"
            }
        }
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.temp_dir)
    
    def test_simple_config(self):
        """Test processing a simple configuration."""
        # Create a simple configuration
        config = {
            "output_folder": "test_output",
            "files": [
                str(self.test_file1)
            ]
        }
        
        # Process the configuration
        output_folder = process_config(config)
        
        # Check that the output folder was created
        self.assertTrue(output_folder.exists())
        self.assertTrue(output_folder.is_dir())
        
        # Check that the file was copied
        copied_file = output_folder / self.test_file1.name
        self.assertTrue(copied_file.exists())
        with open(copied_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "File 1 content")
    
    def test_complex_config(self):
        """Test processing a complex configuration with placeholders."""
        # Create a complex configuration
        config = {
            "output_folder": "{{ project_name }}_output",
            "files": [
                str(self.test_file1),
                {
                    "source": str(self.test_file2),
                    "target": "renamed_{{ environment }}.txt"
                },
                {
                    "source": str(self.test_file1),
                    "directory": "{{ environment }}/docs"
                },
                {
                    "target": "empty_{{ environment }}"
                }
            ]
        }
        
        # Process the configuration
        output_folder = process_config(config, self.values)
        
        # Check that the output folder was created with the placeholder replaced
        expected_output_folder = Path("MyProject_output")
        self.assertEqual(output_folder, expected_output_folder)
        self.assertTrue(output_folder.exists())
        
        # Check that the files were copied correctly
        # Simple file copy
        copied_file1 = output_folder / self.test_file1.name
        self.assertTrue(copied_file1.exists())
        
        # Renamed file with placeholder
        renamed_file = output_folder / "renamed_production.txt"
        self.assertTrue(renamed_file.exists())
        
        # File in subdirectory with placeholder
        subdir_file = output_folder / "production" / "docs" / self.test_file1.name
        self.assertTrue(subdir_file.exists())
        
        # Empty folder with placeholder
        empty_folder = output_folder / "empty_production"
        self.assertTrue(empty_folder.exists())
        self.assertTrue(empty_folder.is_dir())
    
    def test_glob_pattern_config(self):
        """Test processing a configuration with glob patterns."""
        # Create additional test files for glob pattern testing
        test_file3 = Path(self.temp_dir) / "test_a.txt"
        test_file4 = Path(self.temp_dir) / "test_b.txt"
        test_file5 = Path(self.temp_dir) / "test_c.txt"
        
        with open(test_file3, "w") as f:
            f.write("Test A content")
        with open(test_file4, "w") as f:
            f.write("Test B content")
        with open(test_file5, "w") as f:
            f.write("Test C content")
        
        # Create a configuration with glob patterns
        config = {
            "output_folder": "glob_test_output",
            "files": [
                # Simple glob pattern
                str(self.temp_dir) + "/*.txt",
                # Complex case with glob pattern
                {
                    "source": str(self.temp_dir) + "/test_*.txt",
                    "directory": "test_files"
                },
                # Complex case with glob pattern and target as directory
                {
                    "source": str(self.temp_dir) + "/test_[ab].txt",
                    "target": "selected/"
                }
            ]
        }
        
        # Process the configuration
        output_folder = process_config(config)
        
        # Check that the output folder was created
        self.assertTrue(output_folder.exists())
        self.assertTrue(output_folder.is_dir())
        
        # Check that all files were copied to the root
        for filename in ["file1.txt", "file2.txt", "test_a.txt", "test_b.txt", "test_c.txt"]:
            copied_file = output_folder / filename
            self.assertTrue(copied_file.exists(), f"File {filename} not found in root directory")
        
        # Check that test_*.txt files were copied to the test_files directory
        test_files_dir = output_folder / "test_files"
        self.assertTrue(test_files_dir.exists())
        for filename in ["test_a.txt", "test_b.txt", "test_c.txt"]:
            copied_file = test_files_dir / filename
            self.assertTrue(copied_file.exists(), f"File {filename} not found in test_files directory")
        
        # Check that test_[ab].txt files were copied to the selected directory
        selected_dir = output_folder / "selected"
        self.assertTrue(selected_dir.exists())
        for filename in ["test_a.txt", "test_b.txt"]:
            copied_file = selected_dir / filename
            self.assertTrue(copied_file.exists(), f"File {filename} not found in selected directory")
        
        # Check that test_c.txt is not in the selected directory
        self.assertFalse((selected_dir / "test_c.txt").exists())
    
    def test_nested_json_config(self):
        """Test processing a configuration with nested JSON placeholders."""
        # Create a configuration with nested JSON placeholders
        config = {
            "output_folder": "{{ project_name }}_output",
            "files": [
                {
                    "source": str(self.test_file1),
                    "target": "{{ user.name }}_file.txt"
                },
                {
                    "target": "logs/{{ user.role }}"
                }
            ]
        }
        
        # Process the configuration
        output_folder = process_config(config, self.values)
        
        # Check that the files were copied correctly with nested placeholders
        user_file = output_folder / "JohnDoe_file.txt"
        self.assertTrue(user_file.exists())
        
        # Check that the empty folder was created with nested placeholder
        role_folder = output_folder / "logs" / "admin"
        self.assertTrue(role_folder.exists())
        self.assertTrue(role_folder.is_dir())
    
    def test_template_config(self):
        """Test processing a configuration with templates."""
        # Create a template file
        template_file = Path(self.temp_dir) / "template.txt"
        with open(template_file, "w") as f:
            f.write("Hello, {{ user.name }}! Welcome to {{ project_name }}.")
        
        # Create a configuration with templates
        config = {
            "output_folder": "{{ project_name }}_output",
            "templates": [
                {
                    "content": "Project: {{ project_name }}\nEnvironment: {{ environment }}",
                    "target": "config.txt"
                },
                {
                    "file": str(template_file),
                    "target": "welcome_{{ user.name }}.txt"
                },
                {
                    "content": """
                    {% if environment == 'production' %}
                    This is a production environment.
                    {% else %}
                    This is a non-production environment.
                    {% endif %}
                    """,
                    "target": "env_info.txt"
                }
            ]
        }
        
        # Process the configuration
        output_folder = process_config(config, self.values)
        
        # Check that the output folder was created with the placeholder replaced
        expected_output_folder = Path("MyProject_output")
        self.assertEqual(output_folder, expected_output_folder)
        self.assertTrue(output_folder.exists())
        
        # Check that the templates were rendered correctly
        # Inline template
        config_file = output_folder / "config.txt"
        self.assertTrue(config_file.exists())
        with open(config_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Project: MyProject\nEnvironment: production")
        
        # Template from file with placeholder in target
        welcome_file = output_folder / "welcome_JohnDoe.txt"
        self.assertTrue(welcome_file.exists())
        with open(welcome_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Hello, JohnDoe! Welcome to MyProject.")
        
        # Template with Jinja2 conditionals
        env_file = output_folder / "env_info.txt"
        self.assertTrue(env_file.exists())
        with open(env_file, "r") as f:
            content = f.read()
        self.assertIn("This is a production environment.", content)
        self.assertNotIn("This is a non-production environment.", content)

    def test_archive_config_boolean(self):
        """Test processing a configuration with archive enabled as boolean."""
        output_folder_path = Path(self.temp_dir) / "archive_bool"
        config = {
            "output_folder": str(output_folder_path),
            "files": [str(self.test_file1)],
            "archive": True,
        }

        output_folder = process_config(config)
        self.assertEqual(output_folder, output_folder_path)

        archive_path = output_folder.with_suffix(".zip")
        self.assertTrue(archive_path.exists())

        with zipfile.ZipFile(archive_path, "r") as zipf:
            self.assertIn(self.test_file1.name, zipf.namelist())
            self.assertEqual(zipf.read(self.test_file1.name).decode("utf-8"), "File 1 content")

    def test_archive_config_tar_gz(self):
        """Test processing a configuration with archive dict (tar.gz)."""
        output_folder_path = Path(self.temp_dir) / "archive_dict"
        config = {
            "output_folder": str(output_folder_path),
            "files": [str(self.test_file1)],
            "archive": {"format": "tar", "method": "gz"},
        }

        output_folder = process_config(config)
        self.assertEqual(output_folder, output_folder_path)

        archive_path = output_folder.with_suffix(".tar.gz")
        self.assertTrue(archive_path.exists())

        with tarfile.open(archive_path, "r:*") as tarf:
            names = tarf.getnames()
            # archive includes the folder name, so check for nested path
            self.assertIn(f"{output_folder_path.name}/{self.test_file1.name}", names)


class TestTemplateRendering(unittest.TestCase):
    """Test cases for the template rendering functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Test values with nested JSON
        self.values = {
            "project_name": "MyProject",
            "environment": "production",
            "date": "2025-11-08",
            "user": {
                "name": "JohnDoe",
                "role": "admin"
            },
            "database": {
                "host": "db.example.com",
                "port": 5432,
                "credentials": {
                    "username": "dbuser",
                    "password": "secret"
                }
            }
        }
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.temp_dir)
    
    def test_render_template(self):
        """Test rendering a template from a string."""
        # Create a simple template
        template_content = "Hello, {{ user.name }}! Welcome to {{ project_name }}."
        expected_content = "Hello, JohnDoe! Welcome to MyProject."
        
        # Render the template
        target_path = Path(self.temp_dir) / "rendered.txt"
        render_template(template_content, target_path, self.values)
        
        # Check that the file was created with the expected content
        self.assertTrue(target_path.exists())
        with open(target_path, "r") as f:
            content = f.read()
        self.assertEqual(content, expected_content)
    
    def test_render_template_with_jinja2_features(self):
        """Test rendering a template with Jinja2 features like conditionals and loops."""
        # Create a template with conditionals and loops
        template_content = """
        # Project: {{ project_name }}
        
        {% if environment == 'production' %}
        This is a production environment.
        {% else %}
        This is a non-production environment.
        {% endif %}
        
        ## Database Information
        {% for key, value in database.items() if key != 'credentials' %}
        - {{ key }}: {{ value }}
        {% endfor %}
        """
        
        # Render the template
        target_path = Path(self.temp_dir) / "rendered_complex.txt"
        render_template(template_content, target_path, self.values)
        
        # Check that the file was created
        self.assertTrue(target_path.exists())
        
        # Check the content
        with open(target_path, "r") as f:
            content = f.read()
        
        # Verify that conditionals worked
        self.assertIn("This is a production environment.", content)
        self.assertNotIn("This is a non-production environment.", content)
        
        # Verify that loops worked
        self.assertIn("- host: db.example.com", content)
        self.assertIn("- port: 5432", content)
        self.assertNotIn("credentials", content)
    
    def test_render_template_file(self):
        """Test rendering a template from a file."""
        # Create a template file
        template_path = Path(self.temp_dir) / "template.txt"
        with open(template_path, "w") as f:
            f.write("Database: {{ database.host }}:{{ database.port }}")
        
        # Render the template
        target_path = Path(self.temp_dir) / "rendered_from_file.txt"
        render_template_file(template_path, target_path, self.values)
        
        # Check that the file was created with the expected content
        self.assertTrue(target_path.exists())
        with open(target_path, "r") as f:
            content = f.read()
        self.assertEqual(content, "Database: db.example.com:5432")


class TestMain(unittest.TestCase):
    """Test cases for the main function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_file = Path(self.temp_dir) / "file.txt"
        with open(self.test_file, "w") as f:
            f.write("Test file content")
        
        # Create test config file
        self.config_file = Path(self.temp_dir) / "config.yaml"
        config = {
            "output_folder": "test_output",
            "files": [
                str(self.test_file)
            ]
        }
        with open(self.config_file, "w") as f:
            yaml.dump(config, f)
        
        # Create test values file
        self.values_file = Path(self.temp_dir) / "values.json"
        values = {
            "project_name": "TestProject"
        }
        with open(self.values_file, "w") as f:
            json.dump(values, f)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.temp_dir)
        
        # Remove the output folder if it exists
        output_folder = Path("test_output")
        if output_folder.exists():
            shutil.rmtree(output_folder)
    
    @patch('sys.argv')
    def test_main_with_config_only(self, mock_argv):
        """Test main function with config file only."""
        # Mock command line arguments
        mock_argv.__getitem__.side_effect = lambda i: [
            "deployfolder", str(self.config_file)
        ][i]
        
        # Run main function
        result = main()
        
        # Check that the function returned success
        self.assertEqual(result, 0)
        
        # Check that the output folder was created
        output_folder = Path("test_output")
        self.assertTrue(output_folder.exists())
        
        # Check that the file was copied
        copied_file = output_folder / self.test_file.name
        self.assertTrue(copied_file.exists())
    
    @patch('sys.argv')
    def test_main_with_config_and_values(self, mock_argv):
        """Test main function with config and values files."""
        # Mock command line arguments
        mock_argv.__getitem__.side_effect = lambda i: [
            "deployfolder", str(self.config_file), "--values", str(self.values_file)
        ][i]
        
        # Run main function
        result = main()
        
        # Check that the function returned success
        self.assertEqual(result, 0)
        
        # Check that the output folder was created
        output_folder = Path("test_output")
        self.assertTrue(output_folder.exists())
        
        # Check that the file was copied
        copied_file = output_folder / self.test_file.name
        self.assertTrue(copied_file.exists())


if __name__ == '__main__':
    unittest.main()
