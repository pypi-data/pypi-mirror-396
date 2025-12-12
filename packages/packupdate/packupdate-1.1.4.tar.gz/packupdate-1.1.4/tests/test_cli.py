"""
Test CLI argument parsing
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packUpdate.utils.cli import parse_cli_args


class TestCLIParsing(unittest.TestCase):
    """Test CLI argument parsing"""

    def setUp(self):
        """Store original sys.argv"""
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        """Restore original sys.argv"""
        sys.argv = self.original_argv

    def test_default_arguments(self):
        """Test parsing with no arguments"""
        sys.argv = ['packUpdate']
        args = parse_cli_args()
        
        # project_path defaults to current directory (may be absolute path)
        self.assertTrue(os.path.isdir(args['project_path']))
        self.assertFalse(args['safe_mode'])
        self.assertFalse(args['interactive'])
        self.assertFalse(args['minor_only'])
        self.assertFalse(args['generate_report'])
        self.assertFalse(args['remove_unused'])
        self.assertFalse(args['dedupe_packages'])
        self.assertFalse(args['quiet_mode'])
        self.assertEqual(args['passes'], 1)
        self.assertIsNone(args['update_version'])
        self.assertFalse(args['automate'])

    def test_project_path_argument(self):
        """Test parsing with project path"""
        sys.argv = ['packUpdate', '/path/to/project']
        args = parse_cli_args()
        
        self.assertEqual(args['project_path'], '/path/to/project')

    def test_safe_mode_flag(self):
        """Test --safe flag"""
        sys.argv = ['packUpdate', '--safe']
        args = parse_cli_args()
        
        self.assertTrue(args['safe_mode'])

    def test_interactive_flag(self):
        """Test --interactive flag"""
        sys.argv = ['packUpdate', '--interactive']
        args = parse_cli_args()
        
        self.assertTrue(args['interactive'])

    def test_minor_only_flag(self):
        """Test --minor-only flag"""
        sys.argv = ['packUpdate', '--minor-only']
        args = parse_cli_args()
        
        self.assertTrue(args['minor_only'])

    def test_generate_report_flag(self):
        """Test --generate-report flag"""
        sys.argv = ['packUpdate', '--generate-report']
        args = parse_cli_args()
        
        self.assertTrue(args['generate_report'])

    def test_remove_unused_flag(self):
        """Test --remove-unused flag"""
        sys.argv = ['packUpdate', '--remove-unused']
        args = parse_cli_args()
        
        self.assertTrue(args['remove_unused'])

    def test_dedupe_packages_flag(self):
        """Test --dedupe-packages flag"""
        sys.argv = ['packUpdate', '--dedupe-packages']
        args = parse_cli_args()
        
        self.assertTrue(args['dedupe_packages'])

    def test_quiet_mode_flag(self):
        """Test --quiet flag"""
        sys.argv = ['packUpdate', '--quiet']
        args = parse_cli_args()
        
        self.assertTrue(args['quiet_mode'])

    def test_passes_argument(self):
        """Test --pass argument"""
        sys.argv = ['packUpdate', '--pass=3']
        args = parse_cli_args()
        
        self.assertEqual(args['passes'], 3)

    def test_update_version_major(self):
        """Test --update-version=major"""
        sys.argv = ['packUpdate', '--update-version=major']
        args = parse_cli_args()
        
        self.assertEqual(args['update_version'], 'major')

    def test_update_version_minor(self):
        """Test --update-version=minor"""
        sys.argv = ['packUpdate', '--update-version=minor']
        args = parse_cli_args()
        
        self.assertEqual(args['update_version'], 'minor')

    def test_update_version_patch(self):
        """Test --update-version=patch"""
        sys.argv = ['packUpdate', '--update-version=patch']
        args = parse_cli_args()
        
        self.assertEqual(args['update_version'], 'patch')

    def test_update_version_specific(self):
        """Test --update-version with specific version"""
        sys.argv = ['packUpdate', '--update-version=2.5.1']
        args = parse_cli_args()
        
        self.assertEqual(args['update_version'], '2.5.1')

    def test_automate_flag(self):
        """Test --automate flag"""
        sys.argv = ['packUpdate', '--automate', '--platform=github', '--repository=org/repo']
        args = parse_cli_args()
        
        self.assertTrue(args['automate'])

    def test_combined_flags(self):
        """Test multiple flags combined"""
        sys.argv = ['packUpdate', '/my/project', '--safe', '--quiet', '--minor-only', '--pass=2']
        args = parse_cli_args()
        
        self.assertEqual(args['project_path'], '/my/project')
        self.assertTrue(args['safe_mode'])
        self.assertTrue(args['quiet_mode'])
        self.assertTrue(args['minor_only'])
        self.assertEqual(args['passes'], 2)

    def test_automation_arguments(self):
        """Test automation-specific arguments"""
        sys.argv = [
            'packUpdate',
            '--automate',
            '--platform=bitbucket-server',
            '--endpoint=https://bitbucket.example.com',
            '--token=abc123',
            '--repository=WORKSPACE/repo',
            '--base-branch=main',
            '--feature-branch=feature/updates',
            '--ticket-no=JIRA-123',
            '--reviewers=user1,user2'
        ]
        args = parse_cli_args()
        
        self.assertTrue(args['automate'])
        self.assertEqual(args['platform'], 'bitbucket-server')
        self.assertEqual(args['endpoint'], 'https://bitbucket.example.com')
        self.assertEqual(args['token'], 'abc123')
        self.assertEqual(args['repository'], 'WORKSPACE/repo')
        self.assertEqual(args['base_branch'], 'main')
        self.assertEqual(args['feature_branch'], 'feature/updates')
        self.assertEqual(args['ticket_no'], 'JIRA-123')
        self.assertEqual(args['reviewers'], 'user1,user2')


if __name__ == '__main__':
    unittest.main()
