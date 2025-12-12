"""
Integration tests for PackUpdate
Tests the interaction between multiple modules
"""
import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.package_json = {
            'name': 'test-package',
            'version': '1.0.0',
            'dependencies': {
                'express': '4.0.0',
                'lodash': '4.0.0'
            },
            'scripts': {
                'build': 'echo "build success"',
                'test': 'echo "test success"'
            }
        }
        
        # Create package.json
        package_json_path = os.path.join(self.test_dir, 'package.json')
        with open(package_json_path, 'w') as f:
            json.dump(self.package_json, f)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_project_validation_and_script_execution(self):
        """Test that project validation works with script execution"""
        from packUpdate.updatePackages import validate_project_path, execute_script_if_exist
        
        # Should not raise exception
        validate_project_path(self.test_dir)
        
        # Should execute script successfully
        result = execute_script_if_exist(self.test_dir, 'build', quiet_mode=True)
        self.assertTrue(result)

    @patch('packUpdate.services.package_service.get_outdated_packages')
    def test_empty_outdated_packages_handling(self, mock_get_outdated):
        """Test handling when no packages are outdated"""
        mock_get_outdated.return_value = {}
        
        from packUpdate.updatePackages import resolve_update_order
        
        order = resolve_update_order({}, {'dependencies': {}})
        self.assertEqual(len(order), 0)

    def test_cli_and_validation_integration(self):
        """Test CLI parsing integrates with validation"""
        from packUpdate.utils.cli import parse_cli_args
        from packUpdate.updatePackages import validate_project_path
        
        original_argv = sys.argv.copy()
        try:
            sys.argv = ['packUpdate', self.test_dir]
            args = parse_cli_args()
            
            # Should not raise exception
            validate_project_path(args['project_path'])
        finally:
            sys.argv = original_argv


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""

    def test_invalid_package_json(self):
        """Test handling of invalid package.json"""
        from packUpdate.updatePackages import execute_script_if_exist
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create invalid package.json
            package_json_path = os.path.join(tmpdir, 'package.json')
            with open(package_json_path, 'w') as f:
                f.write('invalid json content')
            
            result = execute_script_if_exist(tmpdir, 'test', quiet_mode=True)
            self.assertFalse(result)

    def test_missing_dependency_tree_keys(self):
        """Test handling of missing keys in dependency tree"""
        from packUpdate.updatePackages import resolve_update_order
        
        outdated_packages = {
            'package-a': {'current': '1.0.0', 'latest': '2.0.0'}
        }
        
        # Empty dependency tree
        order = resolve_update_order(outdated_packages, {})
        self.assertEqual(len(order), 1)
        
        # Dependency tree without 'dependencies' key
        order = resolve_update_order(outdated_packages, {'other_key': {}})
        self.assertEqual(len(order), 1)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_single_package_update(self):
        """Test updating a single package"""
        from packUpdate.updatePackages import resolve_update_order
        
        outdated_packages = {
            'single-package': {'current': '1.0.0', 'latest': '2.0.0'}
        }
        dependency_tree = {'dependencies': {}}
        
        order = resolve_update_order(outdated_packages, dependency_tree)
        self.assertEqual(len(order), 1)
        self.assertEqual(order[0], 'single-package')

    def test_many_packages_no_dependencies(self):
        """Test updating many packages with no interdependencies"""
        from packUpdate.updatePackages import resolve_update_order
        
        # Create 50 packages
        outdated_packages = {
            f'package-{i}': {'current': '1.0.0', 'latest': '2.0.0'}
            for i in range(50)
        }
        dependency_tree = {'dependencies': {}}
        
        order = resolve_update_order(outdated_packages, dependency_tree)
        self.assertEqual(len(order), 50)

    def test_version_with_special_characters(self):
        """Test handling versions with special characters"""
        from packUpdate.utils.version import is_minor_update
        
        # Should handle versions with prerelease tags
        result = is_minor_update('1.0.0-alpha.1', '1.1.0-beta.2')
        self.assertIsInstance(result, bool)
        
        # Should handle versions with build metadata
        result = is_minor_update('1.0.0+build.123', '1.1.0+build.456')
        self.assertIsInstance(result, bool)

    def test_cli_with_multiple_equal_signs(self):
        """Test CLI parsing with values containing equal signs"""
        from packUpdate.utils.cli import parse_cli_args
        
        original_argv = sys.argv.copy()
        try:
            # Token might contain equal signs
            sys.argv = ['packUpdate', '--token=abc=def=ghi']
            args = parse_cli_args()
            
            # Should handle the value correctly
            self.assertIn('token', args)
        finally:
            sys.argv = original_argv


if __name__ == '__main__':
    unittest.main()
