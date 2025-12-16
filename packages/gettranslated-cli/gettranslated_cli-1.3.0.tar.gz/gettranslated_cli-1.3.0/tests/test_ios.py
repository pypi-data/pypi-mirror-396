import unittest
import tempfile
import os
import shutil
from unittest.mock import patch
from gettranslated_cli.main import find_files, find_files_helper, _detect_ios_languages

# Mock token for testing
MOCK_TOKEN = "test-token-123"


class IOSFileFindingTest(unittest.TestCase):
    """Test cases for iOS file finding functionality in the CLI"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="ios_test_")
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_files_helper_ios_strings(self):
        """Test that find_files_helper can find iOS .strings files"""
        # Create test .lproj directory structure
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        
        with open(os.path.join(en_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome";')
        
        # Test finding .strings files in .lproj directory
        results = find_files_helper(self.test_dir, "*.strings", "en.lproj")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("Localizable.strings"))
        self.assertIn("en.lproj", results[0])

    def test_find_files_helper_ios_stringsdict(self):
        """Test that find_files_helper can find iOS .stringsdict files"""
        # Create test .lproj directory structure
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        
        with open(os.path.join(en_lproj, "Localizable.stringsdict"), "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0">\n</plist>')
        
        # Test finding .stringsdict files in .lproj directory
        results = find_files_helper(self.test_dir, "*.stringsdict", "en.lproj")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("Localizable.stringsdict"))
        self.assertIn("en.lproj", results[0])

    def test_find_files_ios_strings_only(self):
        """Test that find_files can find iOS .strings files"""
        # Create test .lproj directory structure
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        
        with open(os.path.join(en_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome";')
        
        file_list = {
            "platform": "iOS",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("Localizable.strings"))
        self.assertIn("en.lproj", results[0])

    def test_find_files_ios_stringsdict_only(self):
        """Test that find_files can find iOS .stringsdict files"""
        # Create test .lproj directory structure
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        
        with open(os.path.join(en_lproj, "Localizable.stringsdict"), "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0">\n</plist>')
        
        file_list = {
            "platform": "iOS",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("Localizable.stringsdict"))
        self.assertIn("en.lproj", results[0])

    def test_find_files_ios_both_formats(self):
        """Test that find_files can find both .strings and .stringsdict files"""
        # Create test .lproj directory structure
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        
        with open(os.path.join(en_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome";')
        
        with open(os.path.join(en_lproj, "Localizable.stringsdict"), "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0">\n</plist>')
        
        file_list = {
            "platform": "iOS",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 2)
        
        # Check that both files are found
        strings_found = any("Localizable.strings" in result and "Localizable.stringsdict" not in result for result in results)
        stringsdict_found = any("Localizable.stringsdict" in result for result in results)
        self.assertTrue(strings_found)
        self.assertTrue(stringsdict_found)

    def test_find_files_ios_different_base_language(self):
        """Test finding iOS files with non-English base language"""
        # Create test .lproj directory structure with Spanish as base
        es_lproj = os.path.join(self.test_dir, "es.lproj")
        os.makedirs(es_lproj, exist_ok=True)
        
        with open(os.path.join(es_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Bienvenido";')
        
        file_list = {
            "platform": "iOS",
            "base_language": "es"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("Localizable.strings"))
        self.assertIn("es.lproj", results[0])

    def test_find_files_ios_no_files_found(self):
        """Test behavior when no iOS files are found"""
        # Create directory but no .lproj directories
        with open(os.path.join(self.test_dir, "random.txt"), "w") as f:
            f.write("Not an iOS file")
        
        file_list = {
            "platform": "iOS",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 0)

    def test_find_files_ios_wrong_lproj_directory(self):
        """Test that files in wrong .lproj directory are not found"""
        # Create .lproj directory for different language
        es_lproj = os.path.join(self.test_dir, "es.lproj")
        os.makedirs(es_lproj, exist_ok=True)
        
        with open(os.path.join(es_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Bienvenido";')
        
        file_list = {
            "platform": "iOS",
            "base_language": "en"  # Looking for en, but only es exists
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 0)

    def test_find_files_ios_nested_structure(self):
        """Test finding iOS files in nested directory structure"""
        # Create nested .lproj directory structure
        nested_dir = os.path.join(self.test_dir, "MyApp", "Resources", "en.lproj")
        os.makedirs(nested_dir, exist_ok=True)
        
        with open(os.path.join(nested_dir, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome";')
        
        file_list = {
            "platform": "iOS",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertIn("en.lproj", results[0])
        self.assertIn("Localizable.strings", results[0])

    def test_find_files_ios_excludes_directories(self):
        """Test that find_files excludes common directories"""
        # Create typical iOS project structure
        build_dir = os.path.join(self.test_dir, "build")
        git_dir = os.path.join(self.test_dir, ".git")
        node_modules_dir = os.path.join(self.test_dir, "node_modules")
        
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(git_dir, exist_ok=True)
        os.makedirs(node_modules_dir, exist_ok=True)
        
        # Create valid .lproj directory
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        with open(os.path.join(en_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome";')
        
        # Create files in excluded directories (should be ignored)
        build_lproj = os.path.join(build_dir, "en.lproj")
        os.makedirs(build_lproj, exist_ok=True)
        with open(os.path.join(build_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome from build";')
        
        file_list = {
            "platform": "iOS",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        
        # Should only find the valid file, not the one in build directory
        self.assertEqual(len(results), 1)
        self.assertIn("en.lproj", results[0])
        self.assertNotIn("build", results[0])

    def test_detect_ios_languages_strings(self):
        """Test _detect_ios_languages with .strings files"""
        # Create multiple .lproj directories
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        es_lproj = os.path.join(self.test_dir, "es.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        os.makedirs(es_lproj, exist_ok=True)
        
        with open(os.path.join(en_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome";')
        
        with open(os.path.join(es_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Bienvenido";')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_ios_languages(self.test_dir, MOCK_TOKEN)
        
        # Should detect both languages
        self.assertIn("en", detected)
        self.assertIn("es", detected)
        self.assertEqual(len(detected["en"]), 1)
        self.assertEqual(len(detected["es"]), 1)

    def test_detect_ios_languages_stringsdict(self):
        """Test _detect_ios_languages with .stringsdict files"""
        # Create .lproj directory with .stringsdict file
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        
        with open(os.path.join(en_lproj, "Localizable.stringsdict"), "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0">\n</plist>')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_ios_languages(self.test_dir, MOCK_TOKEN)
        
        # Should detect English
        self.assertIn("en", detected)
        self.assertEqual(len(detected["en"]), 1)
        self.assertTrue(detected["en"][0].endswith("Localizable.stringsdict"))

    def test_detect_ios_languages_both_formats(self):
        """Test _detect_ios_languages with both .strings and .stringsdict files"""
        # Create .lproj directory with both file types
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        
        with open(os.path.join(en_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome";')
        
        with open(os.path.join(en_lproj, "Localizable.stringsdict"), "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0">\n</plist>')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_ios_languages(self.test_dir, MOCK_TOKEN)
        
        # Should detect both files for English
        self.assertIn("en", detected)
        self.assertEqual(len(detected["en"]), 2)
        
        # Check that both file types are detected
        strings_found = any("Localizable.strings" in path and "Localizable.stringsdict" not in path for path in detected["en"])
        stringsdict_found = any("Localizable.stringsdict" in path for path in detected["en"])
        self.assertTrue(strings_found)
        self.assertTrue(stringsdict_found)

    def test_detect_ios_languages_excludes_directories(self):
        """Test that _detect_ios_languages excludes common directories"""
        # Create valid .lproj directory
        en_lproj = os.path.join(self.test_dir, "en.lproj")
        os.makedirs(en_lproj, exist_ok=True)
        with open(os.path.join(en_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome";')
        
        # Create .lproj in excluded directories (should be ignored)
        build_dir = os.path.join(self.test_dir, "build")
        build_lproj = os.path.join(build_dir, "en.lproj")
        os.makedirs(build_lproj, exist_ok=True)
        with open(os.path.join(build_lproj, "Localizable.strings"), "w") as f:
            f.write('"welcome" = "Welcome from build";')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_ios_languages(self.test_dir, MOCK_TOKEN)
        
        # Should only detect the valid file, not the one in build directory
        self.assertIn("en", detected)
        self.assertEqual(len(detected["en"]), 1)
        self.assertNotIn("build", detected["en"][0])


if __name__ == '__main__':
    unittest.main()

