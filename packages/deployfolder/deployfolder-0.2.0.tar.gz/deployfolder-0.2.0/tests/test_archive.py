import unittest
import os
import sys
import shutil
import tempfile
import zipfile
import tarfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import functions from deployfolder package
from deployfolder import archive_folder

class TestArchiveFormats(unittest.TestCase):
    """Test cases for different archive formats and compression methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test folder with files
        self.folder_path = Path(self.temp_dir) / "test_folder"
        self.folder_path.mkdir()
        
        # Create test files with content
        self.file1_path = self.folder_path / "file1.txt"
        self.file2_path = self.folder_path / "file2.txt"
        
        # Create a subdirectory with a file
        self.subdir_path = self.folder_path / "subdir"
        self.subdir_path.mkdir()
        self.file3_path = self.subdir_path / "file3.txt"
        
        # Write content to test files
        with open(self.file1_path, "w") as f:
            f.write("File 1 content")
        with open(self.file2_path, "w") as f:
            f.write("File 2 content")
        with open(self.file3_path, "w") as f:
            f.write("File 3 content in subdirectory")
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.temp_dir)
    
    def verify_zip_contents(self, archive_path):
        """Helper method to verify ZIP archive contents."""
        self.assertTrue(archive_path.exists(), f"Archive file {archive_path} does not exist")
        
        # Check that the archive contains the expected files
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            file_list = zipf.namelist()
            self.assertIn("file1.txt", file_list)
            self.assertIn("file2.txt", file_list)
            self.assertIn("subdir/file3.txt", file_list)
            
            # Check file contents
            self.assertEqual(zipf.read("file1.txt").decode('utf-8'), "File 1 content")
            self.assertEqual(zipf.read("file2.txt").decode('utf-8'), "File 2 content")
            self.assertEqual(zipf.read("subdir/file3.txt").decode('utf-8'), "File 3 content in subdirectory")
    
    def verify_tar_contents(self, archive_path):
        """Helper method to verify TAR archive contents."""
        self.assertTrue(archive_path.exists(), f"Archive file {archive_path} does not exist")
        
        # Check that the archive contains the expected files
        with tarfile.open(archive_path, 'r:*') as tarf:
            # Get the folder name inside the archive
            folder_name = self.folder_path.name
            
            # Check that the expected files exist in the archive
            self.assertTrue(tarf.getmember(f"{folder_name}/file1.txt"))
            self.assertTrue(tarf.getmember(f"{folder_name}/file2.txt"))
            self.assertTrue(tarf.getmember(f"{folder_name}/subdir/file3.txt"))
            
            # Extract and check file contents
            f1 = tarf.extractfile(f"{folder_name}/file1.txt")
            f2 = tarf.extractfile(f"{folder_name}/file2.txt")
            f3 = tarf.extractfile(f"{folder_name}/subdir/file3.txt")
            
            self.assertEqual(f1.read().decode('utf-8'), "File 1 content")
            self.assertEqual(f2.read().decode('utf-8'), "File 2 content")
            self.assertEqual(f3.read().decode('utf-8'), "File 3 content in subdirectory")
    
    def verify_7z_contents(self, archive_path):
        """Helper method to verify 7z archive contents."""
        try:
            import py7zr
        except ImportError:
            self.skipTest("py7zr module not installed, skipping 7z test")
            
        self.assertTrue(archive_path.exists(), f"Archive file {archive_path} does not exist")
        
        # Create a temporary directory for extraction
        extract_dir = Path(self.temp_dir) / "extract_7z"
        extract_dir.mkdir()
        
        # Extract and check contents
        with py7zr.SevenZipFile(archive_path, 'r') as szf:
            szf.extractall(extract_dir)
            
            # Get the folder name inside the archive
            folder_name = self.folder_path.name
            
            # Check that the expected files exist and have correct content
            extracted_file1 = extract_dir / folder_name / "file1.txt"
            extracted_file2 = extract_dir / folder_name / "file2.txt"
            extracted_file3 = extract_dir / folder_name / "subdir" / "file3.txt"
            
            self.assertTrue(extracted_file1.exists())
            self.assertTrue(extracted_file2.exists())
            self.assertTrue(extracted_file3.exists())
            
            with open(extracted_file1, "r") as f:
                self.assertEqual(f.read(), "File 1 content")
            with open(extracted_file2, "r") as f:
                self.assertEqual(f.read(), "File 2 content")
            with open(extracted_file3, "r") as f:
                self.assertEqual(f.read(), "File 3 content in subdirectory")
    
    # ZIP FORMAT TESTS
    
    def test_zip_default(self):
        """Test ZIP format with default settings (LZMA compression)."""
        archive_path = archive_folder(self.folder_path)
        self.assertEqual(archive_path.suffix, '.zip')
        self.verify_zip_contents(archive_path)
    
    def test_zip_stored(self):
        """Test ZIP format with STORED method (no compression)."""
        archive_path = archive_folder(self.folder_path, format="zip", method="stored")
        self.assertEqual(archive_path.suffix, '.zip')
        self.verify_zip_contents(archive_path)
    
    def test_zip_deflated(self):
        """Test ZIP format with DEFLATED method."""
        archive_path = archive_folder(self.folder_path, format="zip", method="deflated")
        self.assertEqual(archive_path.suffix, '.zip')
        self.verify_zip_contents(archive_path)
    
    def test_zip_bzip2(self):
        """Test ZIP format with BZIP2 compression."""
        archive_path = archive_folder(self.folder_path, format="zip", method="bzip2")
        self.assertEqual(archive_path.suffix, '.zip')
        self.verify_zip_contents(archive_path)
    
    def test_zip_lzma(self):
        """Test ZIP format with LZMA compression."""
        archive_path = archive_folder(self.folder_path, format="zip", method="lzma")
        self.assertEqual(archive_path.suffix, '.zip')
        self.verify_zip_contents(archive_path)
    
    def test_zip_custom_path(self):
        """Test ZIP format with custom archive path."""
        custom_path = Path(self.temp_dir) / "custom_archive.zip"
        archive_path = archive_folder(self.folder_path, archive_path=custom_path)
        self.assertEqual(archive_path, custom_path)
        self.verify_zip_contents(archive_path)
    
    def test_zip_compression_level(self):
        """Test ZIP format with custom compression level."""
        archive_path = archive_folder(self.folder_path, format="zip", method="deflated", level=9)
        self.assertEqual(archive_path.suffix, '.zip')
        self.verify_zip_contents(archive_path)
    
    # TAR FORMAT TESTS
    
    def test_tar_uncompressed(self):
        """Test uncompressed TAR format."""
        archive_path = archive_folder(self.folder_path, format="tar")
        self.assertEqual(archive_path.suffix, '.tar')
        self.verify_tar_contents(archive_path)
    
    def test_tar_gz(self):
        """Test TAR format with gzip compression."""
        archive_path = archive_folder(self.folder_path, format="tar", method="gz")
        self.assertTrue(str(archive_path).endswith('.tar.gz'))
        self.verify_tar_contents(archive_path)
    
    def test_tar_bz2(self):
        """Test TAR format with bzip2 compression."""
        archive_path = archive_folder(self.folder_path, format="tar", method="bz2")
        self.assertTrue(str(archive_path).endswith('.tar.bz2'))
        self.verify_tar_contents(archive_path)
    
    def test_tar_xz(self):
        """Test TAR format with xz compression."""
        archive_path = archive_folder(self.folder_path, format="tar", method="xz")
        self.assertTrue(str(archive_path).endswith('.tar.xz'))
        self.verify_tar_contents(archive_path)
    
    def test_tar_custom_path(self):
        """Test TAR format with custom archive path."""
        # For custom path, make sure it has the correct extension for the compression method
        custom_path = Path(self.temp_dir) / "custom_archive.tar.gz"
        archive_path = archive_folder(self.folder_path, format="tar", method="gz", archive_path=custom_path)
        self.assertEqual(archive_path, custom_path)
        self.verify_tar_contents(archive_path)
    
    # 7Z FORMAT TESTS
    
    def test_7z_format(self):
        """Test 7z format."""
        try:
            import py7zr
            archive_path = archive_folder(self.folder_path, format="7z")
            self.assertTrue(str(archive_path).endswith('.7z'))
            self.verify_7z_contents(archive_path)
        except ImportError:
            self.skipTest("py7zr module not installed, skipping 7z test")
    
    def test_7z_custom_path(self):
        """Test 7z format with custom archive path."""
        try:
            import py7zr
            custom_path = Path(self.temp_dir) / "custom_archive.7z"
            archive_path = archive_folder(self.folder_path, format="7z", archive_path=custom_path)
            self.assertEqual(archive_path, custom_path)
            self.verify_7z_contents(archive_path)
        except ImportError:
            self.skipTest("py7zr module not installed, skipping 7z test")
    
    def test_unsupported_format(self):
        """Test that an unsupported format raises a ValueError."""
        with self.assertRaises(ValueError):
            archive_folder(self.folder_path, format="unsupported")


if __name__ == '__main__':
    unittest.main()
