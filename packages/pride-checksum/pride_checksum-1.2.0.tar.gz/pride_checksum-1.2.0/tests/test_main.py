import hashlib
import os
import tempfile
import pytest
import logging
from pathlib import Path
from click.testing import CliRunner

from pride_checksum.__main__ import sha1sum, is_hidden_file, main, read_existing_checksums


class TestSha1sum:
    """Tests for the sha1sum function."""
    
    def test_sha1sum_basic(self):
        """Test sha1sum with a simple file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            result = sha1sum(temp_file)
            # Calculate expected hash
            expected = hashlib.sha1("test content".encode()).hexdigest()
            assert result == expected
        finally:
            os.unlink(temp_file)
    
    def test_sha1sum_empty_file(self):
        """Test sha1sum with an empty file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        try:
            result = sha1sum(temp_file)
            # Empty file SHA1
            expected = hashlib.sha1(b"").hexdigest()
            assert result == expected
        finally:
            os.unlink(temp_file)
    
    def test_sha1sum_nonexistent_file(self):
        """Test sha1sum with a non-existent file."""
        with pytest.raises(FileNotFoundError):
            sha1sum("/nonexistent/file.txt")


class TestReadExistingChecksums:
    """Tests for the read_existing_checksums function."""
    
    def test_read_existing_checksums_valid(self):
        """Test reading a valid checksum.txt file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            checksum_file = os.path.join(temp_dir, "checksum.txt")
            with open(checksum_file, 'w') as f:
                f.write("# SHA-1 Checksum \n")
                f.write("file1.txt\tabc123\n")
                f.write("file2.txt\tdef456\n")
            
            result = read_existing_checksums(checksum_file)
            assert len(result) == 2
            assert result["file1.txt"] == "abc123"
            assert result["file2.txt"] == "def456"
    
    def test_read_existing_checksums_nonexistent(self):
        """Test reading a non-existent checksum.txt file."""
        result = read_existing_checksums("/nonexistent/checksum.txt")
        assert result == {}
    
    def test_read_existing_checksums_empty(self):
        """Test reading an empty checksum.txt file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            checksum_file = os.path.join(temp_dir, "checksum.txt")
            with open(checksum_file, 'w') as f:
                f.write("# SHA-1 Checksum \n")
            
            result = read_existing_checksums(checksum_file)
            assert result == {}
    
    def test_read_existing_checksums_with_comments(self):
        """Test reading checksum.txt with comments and empty lines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            checksum_file = os.path.join(temp_dir, "checksum.txt")
            with open(checksum_file, 'w') as f:
                f.write("# SHA-1 Checksum \n")
                f.write("\n")
                f.write("file1.txt\tabc123\n")
                f.write("# Comment line\n")
                f.write("file2.txt\tdef456\n")
            
            result = read_existing_checksums(checksum_file)
            assert len(result) == 2
            assert result["file1.txt"] == "abc123"
            assert result["file2.txt"] == "def456"


class TestIsHiddenFile:
    """Tests for the is_hidden_file function."""
    
    def test_hidden_file_unix(self):
        """Test detection of hidden files on Unix systems."""
        # Test with a path that starts with dot
        assert is_hidden_file("/path/to/.hidden_file")
        assert is_hidden_file(".hidden_file")
        
    def test_non_hidden_file_unix(self):
        """Test detection of non-hidden files on Unix systems."""
        assert not is_hidden_file("/path/to/visible_file.txt")
        assert not is_hidden_file("visible_file.txt")
        
    def test_hidden_dir_unix(self):
        """Test detection of hidden directories on Unix systems."""
        # The function checks if the filename (not directory) starts with dot
        assert not is_hidden_file("/path/to/.hidden_dir/file.txt")
        assert is_hidden_file("/path/to/.hidden_file")


class TestMainFunction:
    """Tests for the main function and CLI integration."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.runner = CliRunner()
        
    def test_main_with_files_dir(self):
        """Test main function with files_dir option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file1 = os.path.join(temp_dir, "file1.txt")
            test_file2 = os.path.join(temp_dir, "file2.txt")
            
            with open(test_file1, 'w') as f:
                f.write("content1")
            with open(test_file2, 'w') as f:
                f.write("content2")
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            try:
                # Capture logs for the test
                with self.runner.isolated_filesystem():
                    result = self.runner.invoke(main, [
                        '--files_dir', temp_dir,
                        '--out_path', output_dir
                    ])
                
                assert result.exit_code == 0
                
                # Check that checksum.txt was created
                checksum_file = os.path.join(output_dir, "checksum.txt")
                assert os.path.exists(checksum_file)
                
                # Verify checksum file content
                with open(checksum_file, 'r') as f:
                    content = f.read()
                    assert "# SHA-1 Checksum" in content
                    assert "file1.txt" in content
                    assert "file2.txt" in content
                    
            finally:
                # Clean up output directory
                import shutil
                shutil.rmtree(output_dir)
    
    def test_main_with_files_list(self):
        """Test main function with files_list_path option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file1 = os.path.join(temp_dir, "file1.txt")
            test_file2 = os.path.join(temp_dir, "file2.txt")
            
            with open(test_file1, 'w') as f:
                f.write("content1")
            with open(test_file2, 'w') as f:
                f.write("content2")
            
            # Create file list
            file_list = os.path.join(temp_dir, "file_list.txt")
            with open(file_list, 'w') as f:
                f.write(f"{test_file1}\n{test_file2}\n")
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            try:
                result = self.runner.invoke(main, [
                    '--files_list_path', file_list,
                    '--out_path', output_dir
                ])
                
                assert result.exit_code == 0
                
                # Check that checksum.txt was created
                checksum_file = os.path.join(output_dir, "checksum.txt")
                assert os.path.exists(checksum_file)
                
            finally:
                # Clean up output directory
                import shutil
                shutil.rmtree(output_dir)
    
    def test_main_missing_options(self):
        """Test main function with missing required options."""
        with tempfile.TemporaryDirectory() as output_dir:
            result = self.runner.invoke(main, [
                '--out_path', output_dir
            ])
            
            assert result.exit_code == 1
    
    def test_main_nonexistent_output_dir(self):
        """Test main function with non-existent output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = os.path.join(temp_dir, "file1.txt")
            with open(test_file, 'w') as f:
                f.write("content")
            
            result = self.runner.invoke(main, [
                '--files_dir', temp_dir,
                '--out_path', '/nonexistent/directory'
            ])
            
            assert result.exit_code == 1
    
    def test_main_invalid_filename(self):
        """Test main function with invalid filename characters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file with invalid characters (space)
            test_file = os.path.join(temp_dir, "file with spaces.txt")
            with open(test_file, 'w') as f:
                f.write("content")
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            try:
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                
                assert result.exit_code == 1
                
            finally:
                # Clean up output directory
                import shutil
                shutil.rmtree(output_dir)
    
    def test_checksum_generation_functionality(self):
        """Test that checksums are correctly generated and stored."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file with known content
            test_file = os.path.join(temp_dir, "testfile.txt")
            test_content = "Hello World"
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            try:
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                
                assert result.exit_code == 0
                
                # Check that checksum.txt was created and has correct content
                checksum_file = os.path.join(output_dir, "checksum.txt")
                assert os.path.exists(checksum_file)
                
                # Calculate expected SHA1
                expected_sha1 = hashlib.sha1(test_content.encode()).hexdigest()
                
                # Verify checksum file content
                with open(checksum_file, 'r') as f:
                    content = f.read()
                    assert "# SHA-1 Checksum" in content
                    assert f"testfile.txt\t{expected_sha1}" in content
                    
            finally:
                # Clean up output directory
                import shutil
                shutil.rmtree(output_dir)
    
    def test_checksum_overwrite(self):
        """Test that existing checksum.txt is overwritten."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = os.path.join(temp_dir, "file1.txt")
            with open(test_file, 'w') as f:
                f.write("content")
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            try:
                # Create existing checksum.txt
                existing_checksum = os.path.join(output_dir, "checksum.txt")
                with open(existing_checksum, 'w') as f:
                    f.write("existing content")
                
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                
                assert result.exit_code == 0
                
                # Verify the file was overwritten with new content
                with open(existing_checksum, 'r') as f:
                    content = f.read()
                    assert "# SHA-1 Checksum" in content
                    assert "existing content" not in content
                    assert "file1.txt" in content
                
            finally:
                # Clean up output directory
                import shutil
                shutil.rmtree(output_dir)
    
    def test_incremental_update_file_renamed(self):
        """Test incremental update when a file is renamed (e.g., .gz removed)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create initial file
            test_file_gz = os.path.join(temp_dir, "data.txt.gz")
            with open(test_file_gz, 'w') as f:
                f.write("compressed data")
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            try:
                # First run: generate initial checksum for .gz file
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                assert result.exit_code == 0
                
                checksum_file = os.path.join(output_dir, "checksum.txt")
                with open(checksum_file, 'r') as f:
                    initial_content = f.read()
                    assert "data.txt.gz" in initial_content
                
                # Rename file (remove .gz extension)
                test_file = os.path.join(temp_dir, "data.txt")
                os.rename(test_file_gz, test_file)
                
                # Add new content to the renamed file
                with open(test_file, 'w') as f:
                    f.write("uncompressed data")
                
                # Second run: incremental update should remove .gz and add .txt
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                assert result.exit_code == 0
                
                # Verify the checksum file was updated correctly
                with open(checksum_file, 'r') as f:
                    updated_content = f.read()
                    assert "data.txt.gz" not in updated_content  # Old file removed
                    assert "data.txt\t" in updated_content  # New file added
                    # Verify it's computing the checksum for the new file
                    expected_sha1 = hashlib.sha1("uncompressed data".encode()).hexdigest()
                    assert expected_sha1 in updated_content
                
            finally:
                import shutil
                shutil.rmtree(output_dir)
    
    def test_incremental_update_file_added(self):
        """Test incremental update when a new file is added."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create initial file
            test_file1 = os.path.join(temp_dir, "file1.txt")
            with open(test_file1, 'w') as f:
                f.write("content1")
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            try:
                # First run: generate checksum for file1
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                assert result.exit_code == 0
                
                checksum_file = os.path.join(output_dir, "checksum.txt")
                
                # Add a new file
                test_file2 = os.path.join(temp_dir, "file2.txt")
                with open(test_file2, 'w') as f:
                    f.write("content2")
                
                # Second run: incremental update should keep file1 and add file2
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                assert result.exit_code == 0
                
                # Verify both files are in checksum
                with open(checksum_file, 'r') as f:
                    updated_content = f.read()
                    assert "file1.txt" in updated_content
                    assert "file2.txt" in updated_content
                
            finally:
                import shutil
                shutil.rmtree(output_dir)
    
    def test_incremental_update_file_removed(self):
        """Test incremental update when a file is removed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create two initial files
            test_file1 = os.path.join(temp_dir, "file1.txt")
            test_file2 = os.path.join(temp_dir, "file2.txt")
            with open(test_file1, 'w') as f:
                f.write("content1")
            with open(test_file2, 'w') as f:
                f.write("content2")
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            try:
                # First run: generate checksums for both files
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                assert result.exit_code == 0
                
                checksum_file = os.path.join(output_dir, "checksum.txt")
                
                # Remove file2
                os.remove(test_file2)
                
                # Second run: incremental update should keep file1 and remove file2
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                assert result.exit_code == 0
                
                # Verify only file1 is in checksum
                with open(checksum_file, 'r') as f:
                    updated_content = f.read()
                    assert "file1.txt" in updated_content
                    assert "file2.txt" not in updated_content
                
            finally:
                import shutil
                shutil.rmtree(output_dir)
    
    def test_incremental_update_no_changes(self):
        """Test incremental update when no files have changed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create initial files
            test_file1 = os.path.join(temp_dir, "file1.txt")
            test_file2 = os.path.join(temp_dir, "file2.txt")
            with open(test_file1, 'w') as f:
                f.write("content1")
            with open(test_file2, 'w') as f:
                f.write("content2")
            
            # Create output directory
            output_dir = tempfile.mkdtemp()
            
            try:
                # First run: generate checksums
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                assert result.exit_code == 0
                
                checksum_file = os.path.join(output_dir, "checksum.txt")
                with open(checksum_file, 'r') as f:
                    initial_content = f.read()
                
                # Second run: no changes, should reuse all checksums
                result = self.runner.invoke(main, [
                    '--files_dir', temp_dir,
                    '--out_path', output_dir
                ])
                assert result.exit_code == 0
                
                # Verify content is the same
                with open(checksum_file, 'r') as f:
                    updated_content = f.read()
                    assert initial_content == updated_content
                
            finally:
                import shutil
                shutil.rmtree(output_dir)