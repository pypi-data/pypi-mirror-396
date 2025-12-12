"""
Test safe mode revert logic
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestSafeModeRevert(unittest.TestCase):
    """Test the Latest → Wanted → Revert logic in safe mode"""

    @patch('packUpdate.updatePackages.run_tests')
    @patch('packUpdate.updatePackages.install_package')
    @patch('packUpdate.services.report_service.get_safe_packages_for_update')
    def test_latest_version_succeeds(self, mock_safe_packages, mock_install, mock_run_tests):
        """Test when latest version works on first try"""
        from packUpdate.updatePackages import update_packages_in_order
        
        mock_safe_packages.return_value = []
        mock_install.return_value = True
        mock_run_tests.return_value = None  # No exception = success
        
        outdated_packages = {
            'express': {
                'current': '4.0.0',
                'wanted': '4.21.0',
                'latest': '5.0.0'
            }
        }
        dependency_tree = {'dependencies': {}}
        
        updated, failed = update_packages_in_order(
            outdated_packages, dependency_tree, '/fake/path', 
            safe_mode=True, quiet_mode=True
        )
        
        # Should have tried latest version
        mock_install.assert_called_with('express', '5.0.0', '/fake/path', True, True)
        
        # Should succeed with latest
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0], ('express', '4.0.0', '5.0.0'))
        self.assertEqual(len(failed), 0)

    @patch('packUpdate.updatePackages.run_tests')
    @patch('packUpdate.updatePackages.install_package')
    @patch('packUpdate.services.report_service.get_safe_packages_for_update')
    def test_latest_fails_wanted_succeeds(self, mock_safe_packages, mock_install, mock_run_tests):
        """Test when latest fails but wanted version works"""
        from packUpdate.updatePackages import update_packages_in_order
        
        mock_safe_packages.return_value = []
        mock_install.return_value = True
        
        # First call (latest) fails, second call (wanted) succeeds, third call (if needed) succeeds
        mock_run_tests.side_effect = [
            Exception("Tests failed for latest"),  # Latest fails
            None,  # Wanted succeeds
        ]
        
        outdated_packages = {
            'express': {
                'current': '4.0.0',
                'wanted': '4.21.0',
                'latest': '5.0.0'
            }
        }
        dependency_tree = {'dependencies': {}}
        
        updated, failed = update_packages_in_order(
            outdated_packages, dependency_tree, '/fake/path',
            safe_mode=True, quiet_mode=True
        )
        
        # Should have tried latest, then wanted
        calls = mock_install.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], ('express', '5.0.0', '/fake/path', True, True))
        self.assertEqual(calls[1][0], ('express', '4.21.0', '/fake/path', True, True))
        
        # Should succeed with wanted version
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0], ('express', '4.0.0', '4.21.0'))
        self.assertEqual(len(failed), 0)

    @patch('packUpdate.updatePackages.run_tests')
    @patch('packUpdate.updatePackages.install_package')
    @patch('packUpdate.services.report_service.get_safe_packages_for_update')
    def test_both_fail_reverts_to_original(self, mock_safe_packages, mock_install, mock_run_tests):
        """Test when both latest and wanted fail, reverts to original"""
        from packUpdate.updatePackages import update_packages_in_order
        
        mock_safe_packages.return_value = []
        mock_install.return_value = True
        
        # Latest fails, wanted fails, revert succeeds
        mock_run_tests.side_effect = [
            Exception("Tests failed for latest"),  # Latest fails
            Exception("Tests failed for wanted"),  # Wanted fails
            None,  # Revert succeeds
        ]
        
        outdated_packages = {
            'express': {
                'current': '4.0.0',
                'wanted': '4.21.0',
                'latest': '5.0.0'
            }
        }
        dependency_tree = {'dependencies': {}}
        
        updated, failed = update_packages_in_order(
            outdated_packages, dependency_tree, '/fake/path',
            safe_mode=True, quiet_mode=True
        )
        
        # Should have tried latest, wanted, then revert
        calls = mock_install.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0][0], ('express', '5.0.0', '/fake/path', True, True))
        self.assertEqual(calls[1][0], ('express', '4.21.0', '/fake/path', True, True))
        self.assertEqual(calls[2][0], ('express', '4.0.0', '/fake/path', True, True))
        
        # Should "succeed" by reverting to original
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0], ('express', '4.0.0', '4.0.0'))
        self.assertEqual(len(failed), 0)

    @patch('packUpdate.updatePackages.run_tests')
    @patch('packUpdate.updatePackages.install_package')
    @patch('packUpdate.services.report_service.get_safe_packages_for_update')
    def test_complete_failure_even_revert_fails(self, mock_safe_packages, mock_install, mock_run_tests):
        """Test when everything fails including revert"""
        from packUpdate.updatePackages import update_packages_in_order
        
        mock_safe_packages.return_value = []
        mock_install.return_value = True
        
        # Everything fails
        mock_run_tests.side_effect = [
            Exception("Tests failed for latest"),
            Exception("Tests failed for wanted"),
            Exception("Tests failed for revert"),
        ]
        
        outdated_packages = {
            'express': {
                'current': '4.0.0',
                'wanted': '4.21.0',
                'latest': '5.0.0'
            }
        }
        dependency_tree = {'dependencies': {}}
        
        updated, failed = update_packages_in_order(
            outdated_packages, dependency_tree, '/fake/path',
            safe_mode=True, quiet_mode=True
        )
        
        # Should have tried all three versions
        calls = mock_install.call_args_list
        self.assertEqual(len(calls), 3)
        
        # Should be marked as failed
        self.assertEqual(len(updated), 1)
        self.assertEqual(updated[0], ('express', '4.0.0', '4.0.0'))
        self.assertEqual(len(failed), 1)
        self.assertIn('express', failed)

    @patch('packUpdate.updatePackages.run_tests')
    @patch('packUpdate.updatePackages.install_package')
    @patch('packUpdate.services.report_service.get_safe_packages_for_update')
    def test_wanted_same_as_latest_skips_wanted(self, mock_safe_packages, mock_install, mock_run_tests):
        """Test when wanted version is same as latest, skips wanted attempt"""
        from packUpdate.updatePackages import update_packages_in_order
        
        mock_safe_packages.return_value = []
        mock_install.return_value = True
        
        # Latest fails, revert succeeds (wanted is skipped)
        mock_run_tests.side_effect = [
            Exception("Tests failed for latest"),
            None,  # Revert succeeds
        ]
        
        outdated_packages = {
            'express': {
                'current': '4.0.0',
                'wanted': '5.0.0',  # Same as latest
                'latest': '5.0.0'
            }
        }
        dependency_tree = {'dependencies': {}}
        
        updated, failed = update_packages_in_order(
            outdated_packages, dependency_tree, '/fake/path',
            safe_mode=True, quiet_mode=True
        )
        
        # Should have tried latest, then revert (skipping wanted)
        calls = mock_install.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], ('express', '5.0.0', '/fake/path', True, True))
        self.assertEqual(calls[1][0], ('express', '4.0.0', '/fake/path', True, True))

    @patch('packUpdate.updatePackages.run_tests')
    @patch('packUpdate.updatePackages.install_package')
    @patch('packUpdate.services.report_service.get_safe_packages_for_update')
    def test_safe_packages_prioritized(self, mock_safe_packages, mock_install, mock_run_tests):
        """Test that safe packages are updated before risky ones"""
        from packUpdate.updatePackages import update_packages_in_order
        
        # Mark 'lodash' as safe
        mock_safe_packages.return_value = ['lodash']
        mock_install.return_value = True
        mock_run_tests.return_value = None
        
        outdated_packages = {
            'express': {'current': '4.0.0', 'wanted': '4.21.0', 'latest': '5.0.0'},
            'lodash': {'current': '4.0.0', 'wanted': '4.17.0', 'latest': '4.17.21'},
        }
        dependency_tree = {'dependencies': {}}
        
        updated, failed = update_packages_in_order(
            outdated_packages, dependency_tree, '/fake/path',
            safe_mode=True, quiet_mode=True
        )
        
        # Should update both packages
        self.assertEqual(len(updated), 2)
        
        # Lodash (safe) should be first
        self.assertEqual(updated[0][0], 'lodash')
        self.assertEqual(updated[1][0], 'express')


if __name__ == '__main__':
    unittest.main()
