"""
Test module imports to catch import errors early
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestImports(unittest.TestCase):
    """Test that all modules can be imported without errors"""

    def test_main_module_import(self):
        """Test main updatePackages module imports"""
        try:
            from packUpdate import updatePackages
            self.assertIsNotNone(updatePackages)
        except ImportError as e:
            self.fail(f"Failed to import updatePackages: {e}")

    def test_utils_imports(self):
        """Test utils module imports"""
        try:
            from packUpdate.utils import logger
            from packUpdate.utils import cli
            from packUpdate.utils import version
            self.assertIsNotNone(logger)
            self.assertIsNotNone(cli)
            self.assertIsNotNone(version)
        except ImportError as e:
            self.fail(f"Failed to import utils: {e}")

    def test_services_imports(self):
        """Test services module imports"""
        try:
            from packUpdate.services import package_service
            from packUpdate.services import report_service
            from packUpdate.services import automation_service
            from packUpdate.services import interactive_service
            from packUpdate.services import version_service
            from packUpdate.services import cleanup_service
            self.assertIsNotNone(package_service)
            self.assertIsNotNone(report_service)
            self.assertIsNotNone(automation_service)
            self.assertIsNotNone(interactive_service)
            self.assertIsNotNone(version_service)
            self.assertIsNotNone(cleanup_service)
        except ImportError as e:
            self.fail(f"Failed to import services: {e}")

    def test_lazy_imports_in_functions(self):
        """Test that lazy imports within functions work correctly"""
        from packUpdate.updatePackages import update_packages_in_order, handle_cleanup_operations
        
        # These functions have lazy imports - just verify they're callable
        self.assertTrue(callable(update_packages_in_order))
        self.assertTrue(callable(handle_cleanup_operations))

    def test_entry_point_imports(self):
        """Test entry point imports from __init__.py"""
        try:
            from packUpdate import main, run_update_process
            self.assertTrue(callable(main))
            self.assertTrue(callable(run_update_process))
        except ImportError as e:
            self.fail(f"Failed to import entry points: {e}")


if __name__ == '__main__':
    unittest.main()
