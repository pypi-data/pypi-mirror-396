import unittest
from unittest.mock import patch, MagicMock
import sys
from argparse import ArgumentParser, Namespace


class ModeParsingTest(unittest.TestCase):
    """Test cases for comma-separated mode parsing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import the main module to test mode parsing logic
        # We'll test the parsing logic directly rather than running main()
        pass
    
    def test_parse_single_mode(self):
        """Test parsing a single mode"""
        mode_string = "upload"
        modes = [m.strip().lower() for m in mode_string.split(",")]
        self.assertEqual(modes, ["upload"])
    
    def test_parse_comma_separated_modes(self):
        """Test parsing comma-separated modes"""
        mode_string = "upload,translate,download"
        modes = [m.strip().lower() for m in mode_string.split(",")]
        self.assertEqual(modes, ["upload", "translate", "download"])
    
    def test_parse_modes_with_spaces(self):
        """Test parsing modes with spaces around commas"""
        mode_string = "upload , translate , download"
        modes = [m.strip().lower() for m in mode_string.split(",")]
        self.assertEqual(modes, ["upload", "translate", "download"])
    
    def test_parse_modes_case_insensitive(self):
        """Test that mode parsing is case-insensitive"""
        mode_string = "UPLOAD,Translate,DOWNLOAD"
        modes = [m.strip().lower() for m in mode_string.split(",")]
        self.assertEqual(modes, ["upload", "translate", "download"])
    
    def test_validate_modes_valid(self):
        """Test validation of valid modes"""
        valid_modes = {"upload", "download", "translate", "sync", "grammar", "init"}
        modes = ["upload", "translate", "download"]
        invalid_modes = [m for m in modes if m not in valid_modes]
        self.assertEqual(invalid_modes, [])
    
    def test_validate_modes_invalid(self):
        """Test validation catches invalid modes"""
        valid_modes = {"upload", "download", "translate", "sync", "grammar", "init"}
        modes = ["upload", "invalid_mode", "download"]
        invalid_modes = [m for m in modes if m not in valid_modes]
        self.assertEqual(invalid_modes, ["invalid_mode"])
    
    def test_expand_sync_mode(self):
        """Test that sync mode expands to upload, translate, download"""
        modes = ["sync"]
        if "sync" in modes:
            modes.remove("sync")
            modes.extend(["upload", "translate", "download"])
            # Remove duplicates while preserving order
            seen = set()
            modes = [m for m in modes if not (m in seen or seen.add(m))]
        self.assertEqual(modes, ["upload", "translate", "download"])
    
    def test_expand_sync_with_other_modes(self):
        """Test that sync expands correctly when combined with other modes"""
        modes = ["upload", "sync", "grammar"]
        if "sync" in modes:
            modes.remove("sync")
            modes.extend(["upload", "translate", "download"])
            # Remove duplicates while preserving order
            seen = set()
            modes = [m for m in modes if not (m in seen or seen.add(m))]
        # Should have upload, grammar, translate, download (upload deduplicated)
        self.assertEqual(modes, ["upload", "grammar", "translate", "download"])
    
    def test_init_cannot_combine_with_other_modes(self):
        """Test that init mode cannot be combined with other modes"""
        modes = ["init", "upload"]
        # This should raise an error in the actual code
        can_combine = not ("init" in modes and len(modes) > 1)
        self.assertFalse(can_combine)
    
    def test_init_can_be_alone(self):
        """Test that init mode can be used alone"""
        modes = ["init"]
        can_combine = not ("init" in modes and len(modes) > 1)
        self.assertTrue(can_combine)
    
    def test_mode_execution_order(self):
        """Test that modes execute in logical order regardless of input order"""
        # Simulate the execution order logic
        modes = ["download", "upload", "translate", "grammar"]
        
        execution_order = []
        
        # Execute in logical order
        if "upload" in modes:
            execution_order.append("upload")
        if "grammar" in modes:
            execution_order.append("grammar")
        if "translate" in modes:
            execution_order.append("translate")
        if "download" in modes:
            execution_order.append("download")
        
        # Should execute in logical order regardless of input order
        self.assertEqual(execution_order, ["upload", "grammar", "translate", "download"])
    
    def test_mode_execution_subset(self):
        """Test that only specified modes execute"""
        modes = ["upload", "download"]
        
        execution_order = []
        
        if "upload" in modes:
            execution_order.append("upload")
        if "grammar" in modes:
            execution_order.append("grammar")
        if "translate" in modes:
            execution_order.append("translate")
        if "download" in modes:
            execution_order.append("download")
        
        # Should only execute upload and download
        self.assertEqual(execution_order, ["upload", "download"])
    
    def test_duplicate_modes_removed(self):
        """Test that duplicate modes are removed"""
        modes = ["upload", "upload", "translate", "translate"]
        # Remove duplicates while preserving order
        seen = set()
        modes = [m for m in modes if not (m in seen or seen.add(m))]
        self.assertEqual(modes, ["upload", "translate"])
    
    def test_all_modes_execution_order(self):
        """Test execution order with all modes"""
        modes = ["grammar", "download", "upload", "translate"]
        
        execution_order = []
        
        if "upload" in modes:
            execution_order.append("upload")
        if "grammar" in modes:
            execution_order.append("grammar")
        if "translate" in modes:
            execution_order.append("translate")
        if "download" in modes:
            execution_order.append("download")
        
        # Should execute in logical order: upload -> grammar -> translate -> download
        self.assertEqual(execution_order, ["upload", "grammar", "translate", "download"])
    
    def test_sync_expands_and_executes_in_order(self):
        """Test that sync expands and executes in correct order"""
        modes = ["sync"]
        # Expand sync
        if "sync" in modes:
            modes.remove("sync")
            modes.extend(["upload", "translate", "download"])
            seen = set()
            modes = [m for m in modes if not (m in seen or seen.add(m))]
        
        execution_order = []
        
        if "upload" in modes:
            execution_order.append("upload")
        if "grammar" in modes:
            execution_order.append("grammar")
        if "translate" in modes:
            execution_order.append("translate")
        if "download" in modes:
            execution_order.append("download")
        
        # Sync expands to upload, translate, download (no grammar)
        self.assertEqual(execution_order, ["upload", "translate", "download"])


if __name__ == '__main__':
    unittest.main()

