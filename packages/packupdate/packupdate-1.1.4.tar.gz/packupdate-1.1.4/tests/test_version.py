"""
Test version comparison utilities
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packUpdate.utils.version import is_minor_update


class TestIsMinorUpdate(unittest.TestCase):
    """Test minor update detection"""

    def test_minor_update(self):
        """Test detection of minor version updates"""
        self.assertTrue(is_minor_update('1.0.0', '1.1.0'))
        self.assertTrue(is_minor_update('1.5.0', '1.6.0'))
        self.assertTrue(is_minor_update('2.3.5', '2.4.0'))

    def test_patch_update(self):
        """Test detection of patch updates (same major version)"""
        # Patch updates should also return True (same major version)
        self.assertTrue(is_minor_update('1.0.0', '1.0.1'))

    def test_major_update(self):
        """Test detection of major updates"""
        self.assertFalse(is_minor_update('1.0.0', '2.0.0'))  # Major update
        self.assertFalse(is_minor_update('1.5.0', '2.1.0'))  # Major update

    def test_same_version(self):
        """Test with same version"""
        self.assertFalse(is_minor_update('1.0.0', '1.0.0'))

    def test_versions_with_prerelease(self):
        """Test with prerelease versions"""
        # Should handle versions with prerelease tags
        result = is_minor_update('1.0.0-beta', '1.1.0')
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
