import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from gettranslated_cli.main import format_validation_issue, upload_file


class ValidationFormattingTest(unittest.TestCase):
    """Test cases for validation issue formatting functionality"""
    
    def test_format_validation_issue_basic(self):
        """Test formatting a basic validation issue"""
        issue = {
            "code": "INVALID_KEY",
            "message": "Key contains invalid characters"
        }
        result = format_validation_issue(issue)
        self.assertIn("INVALID_KEY", result)
        self.assertIn("Key contains invalid characters", result)
        self.assertIn("•", result)
    
    def test_format_validation_issue_with_line(self):
        """Test formatting a validation issue with line number"""
        issue = {
            "code": "SYNTAX_ERROR",
            "message": "Missing semicolon",
            "line": 42
        }
        result = format_validation_issue(issue)
        self.assertIn("SYNTAX_ERROR", result)
        self.assertIn("Missing semicolon", result)
        self.assertIn("line 42", result)
    
    def test_format_validation_issue_with_line_and_column(self):
        """Test formatting a validation issue with line and column numbers"""
        issue = {
            "code": "SYNTAX_ERROR",
            "message": "Unexpected character",
            "line": 10,
            "column": 5
        }
        result = format_validation_issue(issue)
        self.assertIn("SYNTAX_ERROR", result)
        self.assertIn("Unexpected character", result)
        self.assertIn("line 10", result)
        self.assertIn("column 5", result)
    
    def test_format_validation_issue_with_key(self):
        """Test formatting a validation issue with key name"""
        issue = {
            "code": "DUPLICATE_KEY",
            "message": "Key already exists",
            "key": "welcome_message"
        }
        result = format_validation_issue(issue)
        self.assertIn("DUPLICATE_KEY", result)
        self.assertIn("Key already exists", result)
        self.assertIn("[key: welcome_message]", result)
    
    def test_format_validation_issue_complete(self):
        """Test formatting a validation issue with all fields"""
        issue = {
            "code": "INVALID_FORMAT",
            "message": "Invalid string format",
            "line": 15,
            "column": 8,
            "key": "greeting"
        }
        result = format_validation_issue(issue)
        self.assertIn("INVALID_FORMAT", result)
        self.assertIn("Invalid string format", result)
        self.assertIn("line 15", result)
        self.assertIn("column 8", result)
        self.assertIn("[key: greeting]", result)
    
    def test_format_validation_issue_missing_fields(self):
        """Test formatting a validation issue with missing optional fields"""
        issue = {
            "code": "UNKNOWN_ERROR",
            "message": "An error occurred"
        }
        result = format_validation_issue(issue)
        self.assertIn("UNKNOWN_ERROR", result)
        self.assertIn("An error occurred", result)
        # Should not contain location or key info
        self.assertNotIn("line", result)
        self.assertNotIn("column", result)
        self.assertNotIn("[key:", result)
    
    def test_format_validation_issue_empty_dict(self):
        """Test formatting an empty validation issue dict"""
        issue = {}
        result = format_validation_issue(issue)
        self.assertIn("UNKNOWN", result)
        self.assertIn("Unknown issue", result)


class UploadFileValidationTest(unittest.TestCase):
    """Test cases for validation error/warning handling in upload_file"""
    
    def setUp(self):
        """Create a temporary file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write("test content")
        self.temp_file.close()
        self.temp_file_path = self.temp_file.name
        self.temp_dir = os.path.dirname(self.temp_file_path)
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    @patch('gettranslated_cli.main.requests.post')
    def test_upload_file_with_validation_errors(self, mock_post):
        """Test that upload_file correctly extracts validation errors"""
        # Mock successful response with validation errors
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "validation_errors": [
                {
                    "code": "INVALID_KEY",
                    "message": "Key contains invalid characters",
                    "line": 5,
                    "key": "test_key"
                }
            ],
            "validation_warnings": []
        }
        mock_post.return_value = mock_response
        
        result = upload_file(self.temp_file_path, self.temp_dir, "fake_token")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["validation_errors"]), 1)
        self.assertEqual(result["validation_errors"][0]["code"], "INVALID_KEY")
        self.assertEqual(len(result["validation_warnings"]), 0)
    
    @patch('gettranslated_cli.main.requests.post')
    def test_upload_file_with_validation_warnings(self, mock_post):
        """Test that upload_file correctly extracts validation warnings"""
        # Mock successful response with validation warnings
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "validation_errors": [],
            "validation_warnings": [
                {
                    "code": "DEPRECATED_FORMAT",
                    "message": "Using deprecated format",
                    "line": 10
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = upload_file(self.temp_file_path, self.temp_dir, "fake_token")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["validation_errors"]), 0)
        self.assertEqual(len(result["validation_warnings"]), 1)
        self.assertEqual(result["validation_warnings"][0]["code"], "DEPRECATED_FORMAT")
    
    @patch('gettranslated_cli.main.requests.post')
    def test_upload_file_with_both_errors_and_warnings(self, mock_post):
        """Test that upload_file correctly extracts both errors and warnings"""
        # Mock successful response with both validation errors and warnings
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "validation_errors": [
                {
                    "code": "ERROR_1",
                    "message": "First error"
                }
            ],
            "validation_warnings": [
                {
                    "code": "WARNING_1",
                    "message": "First warning"
                },
                {
                    "code": "WARNING_2",
                    "message": "Second warning"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = upload_file(self.temp_file_path, self.temp_dir, "fake_token")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["validation_errors"]), 1)
        self.assertEqual(len(result["validation_warnings"]), 2)
        self.assertEqual(result["validation_errors"][0]["code"], "ERROR_1")
        self.assertEqual(result["validation_warnings"][0]["code"], "WARNING_1")
        self.assertEqual(result["validation_warnings"][1]["code"], "WARNING_2")
    
    @patch('gettranslated_cli.main.requests.post')
    def test_upload_file_without_validation_fields(self, mock_post):
        """Test that upload_file handles responses without validation fields"""
        # Mock successful response without validation fields
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True
        }
        mock_post.return_value = mock_response
        
        result = upload_file(self.temp_file_path, self.temp_dir, "fake_token")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["validation_errors"], [])
        self.assertEqual(result["validation_warnings"], [])
    
    @patch('gettranslated_cli.main.requests.post')
    def test_upload_file_failed_upload(self, mock_post):
        """Test that upload_file handles failed uploads correctly"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        result = upload_file(self.temp_file_path, self.temp_dir, "fake_token")
        
        self.assertFalse(result["success"])
        self.assertIn("error_message", result)
        self.assertIn("400", result["error_message"])
        # Should not have validation fields on failure
        self.assertNotIn("validation_errors", result)
        self.assertNotIn("validation_warnings", result)
    
    @patch('gettranslated_cli.main.requests.post')
    def test_upload_file_with_language_parameter(self, mock_post):
        """Test that upload_file uses the language parameter correctly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "validation_errors": [],
            "validation_warnings": []
        }
        mock_post.return_value = mock_response
        
        upload_file(self.temp_file_path, self.temp_dir, "fake_token", language="es")
        
        # Verify the URL includes the language code
        call_args = mock_post.call_args
        self.assertIn("/sync/file/es/", call_args[0][0])
    
    @patch('gettranslated_cli.main.requests.post')
    def test_upload_file_with_force_parameter(self, mock_post):
        """Test that upload_file uses the force parameter correctly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "validation_errors": [],
            "validation_warnings": []
        }
        mock_post.return_value = mock_response
        
        upload_file(self.temp_file_path, self.temp_dir, "fake_token", force=True)
        
        # Verify the data includes force parameter
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]["data"], {"force": "true"})


class BypassValidationTest(unittest.TestCase):
    """Test cases for bypass_validation flag functionality"""
    
    def setUp(self):
        """Create a temporary file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write("test content")
        self.temp_file.close()
        self.temp_file_path = self.temp_file.name
        self.temp_dir = os.path.dirname(self.temp_file_path)
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    @patch('gettranslated_cli.main.requests.post')
    def test_upload_file_validation_errors_still_returned_with_bypass_validation(self, mock_post):
        """Test that validation errors are still returned even when bypass_validation is True"""
        # Mock successful response with validation errors
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "validation_errors": [
                {
                    "code": "INVALID_KEY",
                    "message": "Key contains invalid characters"
                }
            ],
            "validation_warnings": []
        }
        mock_post.return_value = mock_response
        
        # upload_file doesn't take bypass_validation - it always returns validation errors
        # The bypass_validation flag is handled in run_upload_mode
        result = upload_file(self.temp_file_path, self.temp_dir, "fake_token")
        
        # Validation errors should still be present in the result
        self.assertTrue(result["success"])
        self.assertEqual(len(result["validation_errors"]), 1)
        # The bypass_validation logic is handled in run_upload_mode, not upload_file


if __name__ == '__main__':
    unittest.main()

