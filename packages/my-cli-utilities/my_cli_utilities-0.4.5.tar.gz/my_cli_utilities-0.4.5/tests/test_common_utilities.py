"""
Unit tests for common utilities.
"""

import unittest
from unittest.mock import patch, Mock
from rc_cli.common_lib.config import ValidationUtils, DisplayUtils, BaseConfig


class TestValidationUtils(unittest.TestCase):
    """Test validation utilities."""
    
    def test_is_numeric_string(self):
        """Test numeric string validation."""
        # Test integers
        self.assertTrue(ValidationUtils.is_numeric_string(123))
        self.assertTrue(ValidationUtils.is_numeric_string(0))
        
        # Test digit strings
        self.assertTrue(ValidationUtils.is_numeric_string("123"))
        self.assertTrue(ValidationUtils.is_numeric_string("0"))
        
        # Test non-numeric strings
        self.assertFalse(ValidationUtils.is_numeric_string("abc"))
        self.assertFalse(ValidationUtils.is_numeric_string("12.3"))
        self.assertFalse(ValidationUtils.is_numeric_string(""))
    
    def test_normalize_phone_number(self):
        """Test phone number normalization."""
        # Test number without prefix
        self.assertEqual(ValidationUtils.normalize_phone_number("1234567890"), "+1234567890")
        self.assertEqual(ValidationUtils.normalize_phone_number(1234567890), "+1234567890")
        
        # Test number with prefix
        self.assertEqual(ValidationUtils.normalize_phone_number("+1234567890"), "+1234567890")
    
    def test_truncate_text(self):
        """Test text truncation."""
        # Test short text
        self.assertEqual(ValidationUtils.truncate_text("short", 10), "short")
        
        # Test long text
        self.assertEqual(ValidationUtils.truncate_text("this is a very long text", 10), "this is...")
        
        # Test exact length
        self.assertEqual(ValidationUtils.truncate_text("exactly10c", 10), "exactly10c")


class TestDisplayUtils(unittest.TestCase):
    """Test display utilities."""
    
    def test_format_title(self):
        """Test title formatting."""
        result = DisplayUtils.format_title("Test Title", 20)
        expected = "\nTest Title\n===================="
        self.assertEqual(result, expected)
    
    @patch('typer.echo')
    def test_format_search_info(self, mock_echo):
        """Test search info formatting."""
        DisplayUtils.format_search_info("test query", {"env": "production"})
        
        # Check print was called with correct arguments
        expected_calls = [
            unittest.mock.call("\n🔍 Searching..."),
            unittest.mock.call("   Query: 'test query'"),
            unittest.mock.call("   env: production")
        ]
        
        mock_echo.assert_has_calls(expected_calls)
    
    @patch('typer.echo')
    def test_format_success(self, mock_echo):
        """Test success message formatting."""
        DisplayUtils.format_success("Operation completed")
        mock_echo.assert_called_once_with("   ✅ Operation completed")
    
    @patch('typer.echo')
    def test_format_error(self, mock_echo):
        """Test error message formatting."""
        DisplayUtils.format_error("Something went wrong")
        mock_echo.assert_called_once_with("   ❌ Something went wrong")


class TestBaseConfig(unittest.TestCase):
    """Test base configuration."""
    
    def test_config_constants(self):
        """Test configuration constants."""
        self.assertEqual(BaseConfig.DISPLAY_WIDTH, 50)
        self.assertEqual(BaseConfig.PAGE_SIZE, 5)
        self.assertEqual(BaseConfig.EMOJI_SEARCH, "🔍")
        self.assertEqual(BaseConfig.EMOJI_SUCCESS, "✅")
    
    @patch('tempfile.gettempdir')
    def test_get_temp_dir(self, mock_tempdir):
        """Test temp directory retrieval."""
        mock_tempdir.return_value = "/tmp"
        result = BaseConfig.get_temp_dir()
        self.assertEqual(result, "/tmp")
        mock_tempdir.assert_called_once()
    
    @patch('os.path.join')
    @patch('tempfile.gettempdir')
    def test_get_cache_file(self, mock_tempdir, mock_join):
        """Test cache file path generation."""
        mock_tempdir.return_value = "/tmp"
        mock_join.return_value = "/tmp/cache.json"
        
        result = BaseConfig.get_cache_file("cache.json")
        
        mock_tempdir.assert_called_once()
        mock_join.assert_called_once_with("/tmp", "cache.json")
        self.assertEqual(result, "/tmp/cache.json")


if __name__ == '__main__':
    unittest.main() 