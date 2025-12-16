import unittest
import tempfile
import os
import json
from gettranslated_cli.main import find_files, find_files_helper


class ReactNativeFileFindingTest(unittest.TestCase):
    """Test cases for React Native file finding functionality in the CLI"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="rn_test_")
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def test_find_files_helper_react_native(self):
        """Test that find_files_helper can find React Native JSON files"""
        # Create test files
        with open(os.path.join(self.test_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome"}, f)
        
        with open(os.path.join(self.test_dir, "es.json"), "w") as f:
            json.dump({"welcome": "Bienvenido"}, f)
        
        # Test finding en.json files (empty filedir means search anywhere)
        results = find_files_helper(self.test_dir, "en.json", "")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("en.json"))
        
        # Test finding all JSON files
        results = find_files_helper(self.test_dir, "*.json", "")
        self.assertEqual(len(results), 2)

    def test_find_files_react_native(self):
        """Test that find_files can find React Native files"""
        # Create test files
        with open(os.path.join(self.test_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome"}, f)
        
        with open(os.path.join(self.test_dir, "es.json"), "w") as f:
            json.dump({"welcome": "Bienvenido"}, f)
        
        # Test React Native file finding
        file_list = {
            "platform": "React Native",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("en.json"))

    def test_find_files_react_native_nested_structure(self):
        """Test finding React Native files in nested directory structure with priority"""
        # Create nested directory structure
        nested_dir = os.path.join(self.test_dir, "src", "locales")
        os.makedirs(nested_dir, exist_ok=True)
        
        with open(os.path.join(nested_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome from src/locales"}, f)
        
        with open(os.path.join(self.test_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome from root"}, f)
        
        file_list = {
            "platform": "React Native",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        # Should find only the highest priority file (src/locales comes before root)
        self.assertEqual(len(results), 1)
        self.assertIn("src/locales/en.json", results[0])

    def test_find_files_react_native_different_base_language(self):
        """Test finding React Native files with non-English base language"""
        # Create test files with Spanish as base language
        with open(os.path.join(self.test_dir, "es.json"), "w") as f:
            json.dump({"welcome": "Bienvenido"}, f)
        
        with open(os.path.join(self.test_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome"}, f)
        
        file_list = {
            "platform": "React Native",
            "base_language": "es"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("es.json"))

    def test_find_files_react_native_no_files_found(self):
        """Test behavior when no React Native files are found"""
        # Create non-JSON files
        with open(os.path.join(self.test_dir, "en.txt"), "w") as f:
            f.write("Welcome")
        
        file_list = {
            "platform": "React Native",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 0)

    def test_find_files_react_native_multiple_matches(self):
        """Test finding React Native files with priority when multiple exist"""
        # Create multiple en.json files in different priority locations
        dir1 = os.path.join(self.test_dir, "locales")
        dir2 = os.path.join(self.test_dir, "i18n")
        os.makedirs(dir1, exist_ok=True)
        os.makedirs(dir2, exist_ok=True)
        
        with open(os.path.join(dir1, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome from locales"}, f)
        
        with open(os.path.join(dir2, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome from i18n"}, f)
        
        file_list = {
            "platform": "React Native",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        # Should find only the highest priority file (locales comes before i18n)
        self.assertEqual(len(results), 1)
        self.assertIn("locales/en.json", results[0])

    def test_find_files_react_native_excludes_directories(self):
        """Test that find_files excludes common directories like node_modules"""
        # Create a typical React Native project structure
        src_dir = os.path.join(self.test_dir, "src")
        node_modules_dir = os.path.join(self.test_dir, "node_modules")
        build_dir = os.path.join(self.test_dir, "build")
        git_dir = os.path.join(self.test_dir, ".git")
        
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(node_modules_dir, exist_ok=True)
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(git_dir, exist_ok=True)
        
        # Create files in different locations
        with open(os.path.join(self.test_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome from root"}, f)
        
        # Create src/locales directory (which is in priority list)
        src_locales_dir = os.path.join(src_dir, "locales")
        os.makedirs(src_locales_dir, exist_ok=True)
        with open(os.path.join(src_locales_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome from src/locales"}, f)
        
        # These should be ignored
        with open(os.path.join(node_modules_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome"}, f)
        
        with open(os.path.join(build_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome"}, f)
        
        with open(os.path.join(git_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome"}, f)
        
        file_list = {
            "platform": "React Native",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        
        # Should only find the highest priority file (src/locales comes before root)
        self.assertEqual(len(results), 1)
        self.assertIn("src/locales/en.json", results[0])
        
        # Should not find files in excluded directories
        self.assertFalse(any("node_modules" in result for result in results))
        self.assertFalse(any("build" in result for result in results))
        self.assertFalse(any(".git" in result for result in results))

    def test_find_files_react_native_priority_directories(self):
        """Test that find_files prioritizes common React Native locale directories"""
        # Test 1: Only locales/ directory
        locales_dir = os.path.join(self.test_dir, "locales")
        os.makedirs(locales_dir, exist_ok=True)
        
        with open(os.path.join(locales_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome from locales"}, f)
        
        file_list = {
            "platform": "React Native",
            "base_language": "en"
        }
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertIn("locales/en.json", results[0])
        
        # Clean up and test next priority
        os.remove(os.path.join(locales_dir, "en.json"))
        os.rmdir(locales_dir)
        
        # Test 2: Only src/locales/ directory
        src_locales_dir = os.path.join(self.test_dir, "src", "locales")
        os.makedirs(src_locales_dir, exist_ok=True)
        
        with open(os.path.join(src_locales_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome from src/locales"}, f)
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertIn("src/locales/en.json", results[0])
        
        # Clean up and test next priority
        os.remove(os.path.join(src_locales_dir, "en.json"))
        os.rmdir(src_locales_dir)
        os.rmdir(os.path.join(self.test_dir, "src"))
        
        # Test 3: Only root directory
        with open(os.path.join(self.test_dir, "en.json"), "w") as f:
            json.dump({"welcome": "Welcome from root"}, f)
        
        results = find_files(self.test_dir, file_list)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].endswith("en.json"))
        # Should be root file (not in a subdirectory)
        self.assertTrue(results[0].endswith("/en.json"))
        self.assertFalse(any("/" in os.path.basename(result) for result in results))  # Filename should not contain slashes


if __name__ == '__main__':
    unittest.main()

