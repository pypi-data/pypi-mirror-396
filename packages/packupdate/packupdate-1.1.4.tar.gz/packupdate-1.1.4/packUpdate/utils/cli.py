"""
CLI argument parsing and help display
"""
import sys
import os

def parse_cli_args():
    """Parse command line arguments"""
    args = sys.argv[1:]
    flags = [arg for arg in args if arg.startswith('--')]
    non_flags = [arg for arg in args if not arg.startswith('--')]
    
    pass_arg = next((arg for arg in flags if arg.startswith("--pass=")), None)
    update_version_arg = next((arg for arg in flags if arg.startswith("--update-version=")), None)
    platform_arg = next((arg for arg in flags if arg.startswith("--platform=")), None)
    endpoint_arg = next((arg for arg in flags if arg.startswith("--endpoint=")), None)
    token_arg = next((arg for arg in flags if arg.startswith("--token=")), None)
    repository_arg = next((arg for arg in flags if arg.startswith("--repository=")), None)
    base_branch_arg = next((arg for arg in flags if arg.startswith("--base-branch=")), None)
    feature_branch_arg = next((arg for arg in flags if arg.startswith("--feature-branch=")), None)
    ticket_no_arg = next((arg for arg in flags if arg.startswith("--ticket-no=")), None)
    workspace_dir_arg = next((arg for arg in flags if arg.startswith("--workspace-dir=")), None)
    reviewers_arg = next((arg for arg in flags if arg.startswith("--reviewers=")), None)
    
    return {
        'project_path': non_flags[0] if non_flags else os.getcwd(),
        'safe_mode': "--safe" in flags,
        'interactive': "--interactive" in flags,
        'minor_only': "--minor-only" in flags,
        'generate_report': "--generate-report" in flags,
        'remove_unused': "--remove-unused" in flags,
        'dedupe_packages': "--dedupe-packages" in flags,
        'quiet_mode': "--quiet" in flags,
        'passes': int(pass_arg.split("=")[1]) if pass_arg else 1,
        'update_version': update_version_arg.split("=")[1] if update_version_arg else None,
        # Automation flags
        'automate': "--automate" in flags,
        'platform': platform_arg.split("=")[1] if platform_arg else None,
        'endpoint': endpoint_arg.split("=")[1] if endpoint_arg else os.getenv('PACKUPDATE_BITBUCKET_ENDPOINT'),
        'token': token_arg.split("=")[1] if token_arg else os.getenv('PACKUPDATE_BITBUCKET_TOKEN'),
        'repository': repository_arg.split("=")[1] if repository_arg else None,
        'base_branch': base_branch_arg.split("=")[1] if base_branch_arg else os.getenv('PACKUPDATE_BASE_BRANCH', 'develop'),
        'feature_branch': feature_branch_arg.split("=")[1] if feature_branch_arg else None,
        'ticket_no': ticket_no_arg.split("=")[1] if ticket_no_arg else None,
        'workspace_dir': workspace_dir_arg.split("=")[1] if workspace_dir_arg else os.getenv('PACKUPDATE_WORKSPACE_DIR', './temp-updates'),
        'reviewers': reviewers_arg.split("=")[1] if reviewers_arg else os.getenv('PACKUPDATE_REVIEWERS')
    }

def handle_special_flags():
    """Check for special flags that don't require main execution"""
    args = sys.argv[1:]
    flags = [arg for arg in args if arg.startswith('--')]
    
    if "--help" in flags:
        show_help()
        return True
    
    if "--version" in flags:
        show_version()
        return True
    
    if "--type" in flags:
        print("python")
        return True
    
    return False

def show_help():
    """Display help message with all available parameters."""
    print("""
PackUpdate - Python Package Updater

Usage: packUpdate [project_path] [options]
       updatepkgs [project_path] [options]
       updatenpmpackages [project_path] [options]

Arguments:
  project_path              Path to the Node.js project (default: current directory)

Options:
  --safe                   Enable safe mode (test updates before applying)
  --quiet                  Enable quiet mode (minimal console output)
  --interactive            Interactive mode for selective package updates
  --minor-only             Update only minor versions (1.2.x → 1.3.x, skip major updates)
  --generate-report        Generate comprehensive security & dependency report (no updates)
  --remove-unused          Clean up unused dependencies
  --dedupe-packages        Remove duplicate dependencies
  --update-version=<type>  Update project version after successful updates (major|minor|patch|x.y.z)
  --pass=<number>          Number of update passes (default: 1)

Automation Options:
  --automate               Enable Git automation workflow
  --platform=<type>        Git platform (bitbucket-server|github|gitlab)
  --endpoint=<url>         Bitbucket server base URL (e.g., https://your-bitbucket-server.com)
  --token=<token>          Authentication token (for bitbucket-server platform)
  --repository=<repo>      Repository in format workspace/repo or org/repo
  --base-branch=<branch>   Base branch to create feature branch from (default: develop)
  --feature-branch=<name>  Custom feature branch name (default: auto-generated)
  --ticket-no=<ticket>     Ticket number for commit messages and PR linking
  --workspace-dir=<path>   Temporary workspace directory (default: ./temp-updates)
  --reviewers=<list>       Comma-separated list of reviewers for PR

  --version                Show package version
  --type                   Show package type (python)
  --help                   Show this help message

Environment Variables:
  PACKUPDATE_BITBUCKET_TOKEN     Default Bitbucket authentication token
  PACKUPDATE_BITBUCKET_ENDPOINT  Default Bitbucket server endpoint
  PACKUPDATE_BASE_BRANCH         Default base branch
  PACKUPDATE_WORKSPACE_DIR       Default workspace directory
  PACKUPDATE_REVIEWERS           Default reviewers (comma-separated)

Examples:
  # Basic usage
  packUpdate                                  # Update current directory
  packUpdate /path/to/project                 # Update specific project
  packUpdate --safe --quiet                   # Safe and quiet mode
  packUpdate --generate-report                # Generate security & dependency report

  # Automation examples
  packUpdate --automate \\
    --platform bitbucket-server \\
    --endpoint https://your-bitbucket-server.com \\
    --token your-access-token \\
    --repository WORKSPACE/repository \\
    --ticket-no JIRA-456 \\
    --reviewers john.doe,jane.smith

  packUpdate --automate \\
    --platform github \\
    --repository myorg/myapp \\
    --minor-only \\
    --safe

  # Combined automation with existing features
  packUpdate --automate \\
    --platform bitbucket-server \\
    --repository WORKSPACE/webapp \\
    --ticket-no PROJ-789 \\
    --pass=3 \\
    --remove-unused \\
    --quiet
""")

def show_version():
    """Show package version"""
    import pkg_resources
    try:
        version = pkg_resources.get_distribution("packupdate").version
        print(version)
    except:
        print("1.0.6")
