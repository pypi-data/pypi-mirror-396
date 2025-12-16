import unittest
import tempfile
import os
import shutil
from unittest.mock import patch
from gettranslated_cli.main import find_files, find_files_helper, _detect_android_languages

# Mock token for testing
MOCK_TOKEN = "test-token-123"


class AndroidFileFindingTest(unittest.TestCase):
    """Test cases for Android file finding functionality in the CLI"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="android_test_")
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_find_files_helper_android_strings_xml(self):
        """Test that find_files_helper can find Android strings.xml files"""
        # Create test values directory structure
        values_dir = os.path.join(self.test_dir, "values")
        os.makedirs(values_dir, exist_ok=True)
        
        with open(os.path.join(values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        # Test finding strings.xml files in values directory
        results = find_files_helper(self.test_dir, "strings.xml", "values")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("strings.xml"))
        self.assertIn("values", results[0])

    def test_find_files_android_base_language(self):
        """Test that find_files can find Android strings.xml files for base language (en)"""
        # Create test values directory structure
        values_dir = os.path.join(self.test_dir, "values")
        os.makedirs(values_dir, exist_ok=True)
        
        with open(os.path.join(values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        file_list = {
            "platform": "Android",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("strings.xml"))
        self.assertIn("values", results[0])
        self.assertNotIn("values-", results[0])

    def test_find_files_android_translated_language(self):
        """Test that find_files can find Android strings.xml files for translated languages"""
        # Create test values-es directory structure
        values_es_dir = os.path.join(self.test_dir, "values-es")
        os.makedirs(values_es_dir, exist_ok=True)
        
        with open(os.path.join(values_es_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        file_list = {
            "platform": "Android",
            "base_language": "en"
        }
        
        # Test finding Spanish translation files
        results = find_files(self.test_dir, file_list, language="es")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("strings.xml"))
        self.assertIn("values-es", results[0])

    def test_find_files_android_different_base_language(self):
        """Test finding Android files with non-English base language"""
        # When base language is not "en", Android looks for values-XX directory
        # Create test values-es directory structure with Spanish as base
        values_es_dir = os.path.join(self.test_dir, "values-es")
        os.makedirs(values_es_dir, exist_ok=True)
        
        with open(os.path.join(values_es_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        file_list = {
            "platform": "Android",
            "base_language": "es"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("strings.xml"))
        self.assertIn("values-es", results[0])

    def test_find_files_android_no_files_found(self):
        """Test behavior when no Android files are found"""
        # Create directory but no values directories
        with open(os.path.join(self.test_dir, "random.txt"), "w") as f:
            f.write("Not an Android file")
        
        file_list = {
            "platform": "Android",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 0)

    def test_find_files_android_wrong_language_directory(self):
        """Test that files in wrong values-XX directory are not found"""
        # Create values-es directory but look for en
        values_es_dir = os.path.join(self.test_dir, "values-es")
        os.makedirs(values_es_dir, exist_ok=True)
        
        with open(os.path.join(values_es_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        file_list = {
            "platform": "Android",
            "base_language": "en"
        }
        
        # Looking for en (values/), but only values-es exists
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 0)

    def test_find_files_android_nested_structure(self):
        """Test finding Android files in nested directory structure"""
        # Create nested values directory structure (typical Android project)
        nested_dir = os.path.join(self.test_dir, "app", "src", "main", "res", "values")
        os.makedirs(nested_dir, exist_ok=True)
        
        with open(os.path.join(nested_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        file_list = {
            "platform": "Android",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertIn("values", results[0])
        self.assertIn("strings.xml", results[0])

    def test_find_files_android_excludes_directories(self):
        """Test that find_files excludes common directories"""
        # Create typical Android project structure
        build_dir = os.path.join(self.test_dir, "build")
        git_dir = os.path.join(self.test_dir, ".git")
        
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(git_dir, exist_ok=True)
        
        # Create valid values directory
        values_dir = os.path.join(self.test_dir, "values")
        os.makedirs(values_dir, exist_ok=True)
        with open(os.path.join(values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        # Create files in excluded directories (should be ignored)
        build_values_dir = os.path.join(build_dir, "values")
        os.makedirs(build_values_dir, exist_ok=True)
        with open(os.path.join(build_values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        file_list = {
            "platform": "Android",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        
        # Should only find the valid file, not the one in build directory
        self.assertEqual(len(results), 1)
        self.assertIn("values", results[0])
        self.assertNotIn("build", results[0])

    def test_detect_android_languages_base_language(self):
        """Test _detect_android_languages with base language (values/)"""
        # Create values directory (base language, typically English)
        values_dir = os.path.join(self.test_dir, "values")
        os.makedirs(values_dir, exist_ok=True)
        
        with open(os.path.join(values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_android_languages(self.test_dir, MOCK_TOKEN)
        
        # Should detect English (values/ maps to "en")
        self.assertIn("en", detected)
        self.assertEqual(len(detected["en"]), 1)

    def test_detect_android_languages_translated_languages(self):
        """Test _detect_android_languages with translated languages (values-XX/)"""
        # Create multiple values-XX directories
        values_es_dir = os.path.join(self.test_dir, "values-es")
        values_fr_dir = os.path.join(self.test_dir, "values-fr")
        os.makedirs(values_es_dir, exist_ok=True)
        os.makedirs(values_fr_dir, exist_ok=True)
        
        with open(os.path.join(values_es_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with open(os.path.join(values_fr_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_android_languages(self.test_dir, MOCK_TOKEN)
        
        # Should detect both languages
        self.assertIn("es", detected)
        self.assertIn("fr", detected)
        self.assertEqual(len(detected["es"]), 1)
        self.assertEqual(len(detected["fr"]), 1)

    def test_detect_android_languages_mixed(self):
        """Test _detect_android_languages with both base and translated languages"""
        # Create both values/ and values-XX/ directories
        values_dir = os.path.join(self.test_dir, "values")
        values_es_dir = os.path.join(self.test_dir, "values-es")
        os.makedirs(values_dir, exist_ok=True)
        os.makedirs(values_es_dir, exist_ok=True)
        
        with open(os.path.join(values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with open(os.path.join(values_es_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_android_languages(self.test_dir, MOCK_TOKEN)
        
        # Should detect both English and Spanish
        self.assertIn("en", detected)
        self.assertIn("es", detected)
        self.assertEqual(len(detected["en"]), 1)
        self.assertEqual(len(detected["es"]), 1)

    def test_detect_android_languages_excludes_directories(self):
        """Test that _detect_android_languages excludes common directories"""
        # Create valid values directory
        values_dir = os.path.join(self.test_dir, "values")
        os.makedirs(values_dir, exist_ok=True)
        with open(os.path.join(values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        # Create values in excluded directories (should be ignored)
        build_dir = os.path.join(self.test_dir, "build")
        build_values_dir = os.path.join(build_dir, "values")
        os.makedirs(build_values_dir, exist_ok=True)
        with open(os.path.join(build_values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_android_languages(self.test_dir, MOCK_TOKEN)
        
        # Should only detect the valid file, not the one in build directory
        self.assertIn("en", detected)
        self.assertEqual(len(detected["en"]), 1)
        self.assertNotIn("build", detected["en"][0])

    def test_detect_android_languages_nested_structure(self):
        """Test _detect_android_languages with nested Android project structure"""
        # Create typical Android project structure: app/src/main/res/values/
        nested_values_dir = os.path.join(self.test_dir, "app", "src", "main", "res", "values")
        nested_values_es_dir = os.path.join(self.test_dir, "app", "src", "main", "res", "values-es")
        os.makedirs(nested_values_dir, exist_ok=True)
        os.makedirs(nested_values_es_dir, exist_ok=True)
        
        with open(os.path.join(nested_values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with open(os.path.join(nested_values_es_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_android_languages(self.test_dir, MOCK_TOKEN)
        
        # Should detect both languages even in nested structure
        self.assertIn("en", detected)
        self.assertIn("es", detected)
        self.assertEqual(len(detected["en"]), 1)
        self.assertEqual(len(detected["es"]), 1)

    def test_detect_android_languages_ignores_non_strings_xml(self):
        """Test that _detect_android_languages only detects strings.xml files"""
        # Create values directory with other XML files
        values_dir = os.path.join(self.test_dir, "values")
        os.makedirs(values_dir, exist_ok=True)
        
        # Create strings.xml (should be detected)
        with open(os.path.join(values_dir, "strings.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        # Create other XML files (should be ignored)
        with open(os.path.join(values_dir, "colors.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with open(os.path.join(values_dir, "dimens.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n</resources>')
        
        with patch('gettranslated_cli.main.get_supported_languages', return_value={'en', 'es', 'fr'}):
            detected = _detect_android_languages(self.test_dir, MOCK_TOKEN)
        
        # Should only detect strings.xml
        self.assertIn("en", detected)
        self.assertEqual(len(detected["en"]), 1)
        self.assertTrue(detected["en"][0].endswith("strings.xml"))


if __name__ == '__main__':
    unittest.main()

