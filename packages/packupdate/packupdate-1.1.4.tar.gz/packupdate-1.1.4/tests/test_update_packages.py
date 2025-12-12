"""
Test updatePackages module functionality
"""
import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packUpdate.updatePackages import (
    validate_project_path,
    resolve_update_order,
    execute_script_if_exist,
    run_tests
)


class TestValidateProjectPath(unittest.TestCase):
    """Test project path validation"""

    def test_valid_directory(self):
        """Test validation with valid directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise exception
            try:
                validate_project_path(tmpdir)
            except SystemExit:
                self.fail("validate_project_path raised SystemExit for valid directory")

    def test_invalid_directory(self):
        """Test validation with invalid directory"""
        invalid_path = "/nonexistent/path/to/project"
        with self.assertRaises(SystemExit):
            validate_project_path(invalid_path)

    def test_file_instead_of_directory(self):
        """Test validation with file path instead of directory"""
        with tempfile.NamedTemporaryFile() as tmpfile:
            with self.assertRaises(SystemExit):
                validate_project_path(tmpfile.name)


class TestResolveUpdateOrder(unittest.TestCase):
    """Test dependency resolution for update order"""

    def test_no_dependencies(self):
        """Test packages with no interdependencies"""
        outdated_packages = {
            'package-a': {'current': '1.0.0', 'latest': '2.0.0'},
            'package-b': {'current': '1.0.0', 'latest': '2.0.0'},
            'package-c': {'current': '1.0.0', 'latest': '2.0.0'}
        }
        dependency_tree = {'dependencies': {}}
        
        order = resolve_update_order(outdated_packages, dependency_tree)
        
        # All packages should be in the order
        self.assertEqual(len(order), 3)
        self.assertIn('package-a', order)
        self.assertIn('package-b', order)
        self.assertIn('package-c', order)

    def test_linear_dependencies(self):
        """Test packages with linear dependency chain"""
        outdated_packages = {
            'package-a': {'current': '1.0.0', 'latest': '2.0.0'},
            'package-b': {'current': '1.0.0', 'latest': '2.0.0'},
            'package-c': {'current': '1.0.0', 'latest': '2.0.0'}
        }
        dependency_tree = {
            'dependencies': {
                'package-c': {'requires': {'package-b': '1.0.0'}},
                'package-b': {'requires': {'package-a': '1.0.0'}},
                'package-a': {'requires': {}}
            }
        }
        
        order = resolve_update_order(outdated_packages, dependency_tree)
        
        # package-a should come before package-b, package-b before package-c
        self.assertEqual(len(order), 3)
        self.assertLess(order.index('package-a'), order.index('package-b'))
        self.assertLess(order.index('package-b'), order.index('package-c'))

    def test_complex_dependencies(self):
        """Test packages with complex dependency graph"""
        outdated_packages = {
            'package-a': {'current': '1.0.0', 'latest': '2.0.0'},
            'package-b': {'current': '1.0.0', 'latest': '2.0.0'},
            'package-c': {'current': '1.0.0', 'latest': '2.0.0'},
            'package-d': {'current': '1.0.0', 'latest': '2.0.0'}
        }
        dependency_tree = {
            'dependencies': {
                'package-d': {'requires': {'package-b': '1.0.0', 'package-c': '1.0.0'}},
                'package-c': {'requires': {'package-a': '1.0.0'}},
                'package-b': {'requires': {'package-a': '1.0.0'}},
                'package-a': {'requires': {}}
            }
        }
        
        order = resolve_update_order(outdated_packages, dependency_tree)
        
        # package-a should come first
        self.assertEqual(order[0], 'package-a')
        # package-d should come last
        self.assertEqual(order[-1], 'package-d')
        # package-b and package-c should come before package-d
        self.assertLess(order.index('package-b'), order.index('package-d'))
        self.assertLess(order.index('package-c'), order.index('package-d'))

    def test_circular_dependencies(self):
        """Test handling of circular dependencies"""
        outdated_packages = {
            'package-a': {'current': '1.0.0', 'latest': '2.0.0'},
            'package-b': {'current': '1.0.0', 'latest': '2.0.0'}
        }
        dependency_tree = {
            'dependencies': {
                'package-a': {'requires': {'package-b': '1.0.0'}},
                'package-b': {'requires': {'package-a': '1.0.0'}}
            }
        }
        
        # Should not hang or crash
        order = resolve_update_order(outdated_packages, dependency_tree)
        self.assertEqual(len(order), 2)


class TestExecuteScriptIfExist(unittest.TestCase):
    """Test script execution functionality"""

    def test_script_exists_and_succeeds(self):
        """Test execution when script exists and succeeds"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package.json with test script
            package_json = {
                'name': 'test-package',
                'scripts': {
                    'test': 'echo "test passed"'
                }
            }
            package_json_path = os.path.join(tmpdir, 'package.json')
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f)
            
            result = execute_script_if_exist(tmpdir, 'test', quiet_mode=True)
            self.assertTrue(result)

    def test_script_does_not_exist(self):
        """Test execution when script doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package.json without test script
            package_json = {
                'name': 'test-package',
                'scripts': {}
            }
            package_json_path = os.path.join(tmpdir, 'package.json')
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f)
            
            result = execute_script_if_exist(tmpdir, 'test', quiet_mode=True)
            self.assertTrue(result)  # Should return True when script doesn't exist

    def test_no_package_json(self):
        """Test execution when package.json doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = execute_script_if_exist(tmpdir, 'test', quiet_mode=True)
            self.assertFalse(result)

    def test_script_fails(self):
        """Test execution when script fails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package.json with failing script
            package_json = {
                'name': 'test-package',
                'scripts': {
                    'test': 'exit 1'
                }
            }
            package_json_path = os.path.join(tmpdir, 'package.json')
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f)
            
            result = execute_script_if_exist(tmpdir, 'test', quiet_mode=True)
            self.assertFalse(result)


class TestRunTests(unittest.TestCase):
    """Test the run_tests function"""

    @patch('packUpdate.updatePackages.execute_script_if_exist')
    def test_both_scripts_succeed(self, mock_execute):
        """Test when both build and test scripts succeed"""
        mock_execute.return_value = True
        
        try:
            run_tests('/fake/path', quiet_mode=True)
        except Exception:
            self.fail("run_tests raised exception when scripts succeed")

    @patch('packUpdate.updatePackages.execute_script_if_exist')
    def test_build_fails(self, mock_execute):
        """Test when build script fails"""
        mock_execute.side_effect = [False, True]  # build fails, test succeeds
        
        with self.assertRaises(Exception) as context:
            run_tests('/fake/path', quiet_mode=True)
        self.assertIn("Tests failed", str(context.exception))

    @patch('packUpdate.updatePackages.execute_script_if_exist')
    def test_test_fails(self, mock_execute):
        """Test when test script fails"""
        mock_execute.side_effect = [True, False]  # build succeeds, test fails
        
        with self.assertRaises(Exception) as context:
            run_tests('/fake/path', quiet_mode=True)
        self.assertIn("Tests failed", str(context.exception))

    @patch('packUpdate.updatePackages.execute_script_if_exist')
    def test_both_scripts_fail(self, mock_execute):
        """Test when both scripts fail"""
        mock_execute.return_value = False
        
        with self.assertRaises(Exception) as context:
            run_tests('/fake/path', quiet_mode=True)
        self.assertIn("Tests failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()
