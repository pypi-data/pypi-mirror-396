"""
Git automation service for PackUpdate Python
"""
import os
import subprocess
import json
import shutil
from datetime import datetime
from urllib.parse import urlparse
import requests
from ..utils.logger import log, write_log

def normalize_bitbucket_endpoint(endpoint):
    """Normalize Bitbucket server endpoint (remove trailing slash and /rest/api paths)"""
    return endpoint.rstrip('/').replace('/rest/api/1.0', '').replace('/rest/api', '')

def get_bitbucket_ssh_info(base_url, repository, token):
    """Get SSH port and hostname from Bitbucket repository info"""
    try:
        api_url = get_bitbucket_api_url(base_url, repository).replace('/pull-requests', '')
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(api_url, headers=headers)
        
        if response.ok:
            repo_info = response.json()
            ssh_clone_url = None
            for link in repo_info.get('links', {}).get('clone', []):
                if link.get('name') == 'ssh':
                    ssh_clone_url = link.get('href')
                    break
            
            if ssh_clone_url:
                # Parse SSH URL: ssh://git@hostname:port/path.git
                import re
                match = re.match(r'ssh://git@([^:]+):(\d+)/', ssh_clone_url)
                if match:
                    return {'hostname': match.group(1), 'port': int(match.group(2))}
    except Exception as error:
        log(f"⚠️  Could not detect SSH info from API, using defaults: {error}")
    
    # Fallback to defaults
    hostname = base_url.replace('https://', '').replace('http://', '').split('/')[0]
    return {'hostname': hostname, 'port': 7999}

def get_bitbucket_clone_url(base_url, repository, token=None):
    """Get Bitbucket clone URL - use SSH with auto-detected port"""
    if token:
        ssh_info = get_bitbucket_ssh_info(base_url, repository, token)
        return f"ssh://git@{ssh_info['hostname']}:{ssh_info['port']}/{repository.lower()}.git"
    
    # Fallback without token
    hostname = base_url.replace('https://', '').replace('http://', '').split('/')[0]
    return f"ssh://git@{hostname}:7999/{repository.lower()}.git"

def get_bitbucket_api_url(base_url, repository):
    """Get Bitbucket API URL from base server URL"""
    normalized_url = normalize_bitbucket_endpoint(base_url)
    workspace, repo = repository.split('/')
    return f"{normalized_url}/rest/api/1.0/projects/{workspace}/repos/{repo}/pull-requests"

def create_automation_config(cli_args):
    """Create automation configuration from CLI args"""
    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    repo_name = cli_args['repository'].replace('/', '_') if cli_args['repository'] else 'unknown'
    
    return {
        'platform': cli_args['platform'],
        'endpoint': cli_args['endpoint'],
        'token': cli_args['token'],
        'repository': cli_args['repository'],
        'base_branch': cli_args['base_branch'] or 'develop',
        'feature_branch': cli_args['feature_branch'] or f"feature/package-updates-{timestamp}",
        'ticket_no': cli_args['ticket_no'],
        'workspace_dir': os.path.abspath(os.path.join(cli_args['workspace_dir'], f"{repo_name}_{timestamp}")),
        'project_path': cli_args['project_path'],
        'reviewers': cli_args['reviewers'].split(',') if cli_args['reviewers'] else []
    }

def validate_automation_config(config):
    """Validate automation configuration"""
    if not config['platform']:
        raise ValueError("Platform is required for automation (--platform)")
    
    if not config['repository']:
        raise ValueError("Repository is required for automation (--repository)")
    
    if config['platform'] == 'bitbucket-server':
        if not config['endpoint']:
            raise ValueError("Bitbucket endpoint is required (--endpoint or PACKUPDATE_BITBUCKET_ENDPOINT)")
        if not config['token']:
            raise ValueError("Bitbucket token is required (--token or PACKUPDATE_BITBUCKET_TOKEN)")

def setup_workspace(config):
    """Setup workspace and clone repository"""
    try:
        log(f"🏗️  Setting up workspace: {config['workspace_dir']}")
        
        # Clean and create workspace directory
        if os.path.exists(config['workspace_dir']):
            shutil.rmtree(config['workspace_dir'])
        os.makedirs(config['workspace_dir'], exist_ok=True)
        
        # Determine clone URL based on platform
        if config['platform'] == 'bitbucket-server':
            clone_url = get_bitbucket_clone_url(config['endpoint'], config['repository'], config['token'])
        elif config['platform'] == 'github':
            clone_url = f"git@github.com:{config['repository']}.git"
        elif config['platform'] == 'gitlab':
            clone_url = f"git@gitlab.com:{config['repository']}.git"
        else:
            raise ValueError(f"Unsupported platform: {config['platform']}")
        
        log(f"📥 Cloning repository: {clone_url}")
        subprocess.run(['git', 'clone', clone_url, '.'], cwd=config['workspace_dir'], check=True, capture_output=True)
        
        # Check if base branch exists, fallback to master
        actual_base_branch = config['base_branch']
        try:
            subprocess.run(['git', 'show-ref', '--verify', '--quiet', f"refs/remotes/origin/{config['base_branch']}"], 
                         cwd=config['workspace_dir'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            log(f"⚠️  Base branch '{config['base_branch']}' not found, trying 'master'")
            actual_base_branch = 'master'
            try:
                subprocess.run(['git', 'show-ref', '--verify', '--quiet', 'refs/remotes/origin/master'], 
                             cwd=config['workspace_dir'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                raise ValueError("Neither 'develop' nor 'master' branch found")
        
        # Create and checkout feature branch
        log(f"🌿 Creating feature branch: {config['feature_branch']} from {actual_base_branch}")
        subprocess.run(['git', 'checkout', '-b', config['feature_branch'], f"origin/{actual_base_branch}"], 
                      cwd=config['workspace_dir'], check=True, capture_output=True)
        
        # Install dependencies to ensure npm outdated works correctly
        log("📦 Installing dependencies...")
        subprocess.run(['npm', 'install'], cwd=config['workspace_dir'], check=True, capture_output=True)
        
        return {'success': True, 'message': f"Workspace setup complete: {config['workspace_dir']}", 'branch_created': True}
        
    except Exception as error:
        return {'success': False, 'message': f"Workspace setup failed: {error}"}

def generate_pr_description(config, update_results, report_data):
    """Generate PR description with update logs and report"""
    ticket_link = f"\n**Ticket:** {config['ticket_no']}\n" if config['ticket_no'] else ''
    
    # Aggregate all update results
    all_updated = []
    all_failed = []
    for result in update_results:
        all_updated.extend(result.get('updated', []))
        all_failed.extend(result.get('failed', []))
    
    description = f"""# Package Updates{ticket_link}
## Summary
- **Updated Packages:** {len(all_updated)}
- **Failed Updates:** {len(all_failed)}
- **Total Outdated:** {report_data.get('dependencies', {}).get('outdated', 0)}

## 📦 Updated Packages
"""

    if all_updated:
        for pkg, old_ver, new_ver in all_updated:
            description += f"- `{pkg}`: {old_ver} → {new_ver}\n"
    else:
        description += "No packages were updated.\n"

    if all_failed:
        description += "\n## ❌ Failed Updates\n"
        for pkg in all_failed:
            description += f"- `{pkg}`\n"

    # Add security report summary
    if report_data.get('security'):
        description += f"""
## 🔒 Security Summary
- **Vulnerabilities:** {len(report_data['security'].get('vulnerable_packages', []))}
- **Safe Updates:** {len(report_data.get('breakingChanges', {}).get('safeUpdates', []))}
- **Risky Updates:** {len(report_data.get('breakingChanges', {}).get('riskyUpdates', []))}
"""

    # Add recommendations
    if report_data.get('recommendations'):
        description += "\n## 💡 Recommendations\n"
        for rec in report_data['recommendations']:
            description += f"- {rec}\n"

    description += "\n---\n*Generated by PackUpdate automation*"
    return description

def commit_and_push(config, update_results):
    """Commit and push changes"""
    try:
        all_updated = []
        for result in update_results:
            all_updated.extend(result.get('updated', []))
        
        if not all_updated:
            return {'success': False, 'message': "No packages were updated - no changes to commit"}
        
        # Stage all changes
        subprocess.run(['git', 'add', '.'], cwd=config['workspace_dir'], check=True, capture_output=True)
        
        # Create commit message
        ticket_prefix = f"{config['ticket_no']}: " if config['ticket_no'] else ''
        commit_message = f"""{ticket_prefix}Update {len(all_updated)} packages

Updated packages:
{chr(10).join([f"- {pkg}: {old_ver} → {new_ver}" for pkg, old_ver, new_ver in all_updated])}"""
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=config['workspace_dir'], check=True, capture_output=True)
        
        # Push feature branch
        log(f"📤 Pushing feature branch: {config['feature_branch']}")
        subprocess.run(['git', 'push', 'origin', config['feature_branch']], cwd=config['workspace_dir'], check=True, capture_output=True)
        
        # Get commit hash
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=config['workspace_dir'], capture_output=True, text=True)
        commit_hash = result.stdout.strip()
        
        return {'success': True, 'message': "Changes committed and pushed successfully", 'commit_hash': commit_hash}
        
    except Exception as error:
        return {'success': False, 'message': f"Commit/push failed: {error}"}

def create_bitbucket_pr(config, pr_data):
    """Create pull request via Bitbucket API"""
    try:
        workspace, repo = config['repository'].split('/')
        api_url = get_bitbucket_api_url(config['endpoint'], config['repository'])
        
        payload = {
            'title': pr_data['title'],
            'description': pr_data['description'],
            'fromRef': {
                'id': f"refs/heads/{pr_data['source_branch']}",
                'repository': {
                    'slug': repo,
                    'project': {'key': workspace}
                }
            },
            'toRef': {
                'id': f"refs/heads/{pr_data['target_branch']}",
                'repository': {
                    'slug': repo,
                    'project': {'key': workspace}
                }
            },
            'reviewers': [{'user': {'name': username}} for username in pr_data['reviewers']]
        }
        
        headers = {
            'Authorization': f'Bearer {config["token"]}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        pr_response = response.json()
        if pr_response.get('id'):
            pr_url = f"{config['endpoint']}/projects/{workspace}/repos/{repo}/pull-requests/{pr_response['id']}"
            return {'success': True, 'message': "Pull request created successfully", 'pr_url': pr_url}
        else:
            return {'success': False, 'message': f"PR creation failed: {pr_response}"}
            
    except Exception as error:
        return {'success': False, 'message': f"PR creation failed: {error}"}

def create_pull_request(config, update_results, report_data):
    """Create pull request"""
    try:
        all_updated = []
        for result in update_results:
            all_updated.extend(result.get('updated', []))
        
        ticket_prefix = f"{config['ticket_no']}: " if config['ticket_no'] else ''
        
        pr_data = {
            'title': f"{ticket_prefix}Package Updates - {len(all_updated)} packages updated",
            'description': generate_pr_description(config, update_results, report_data),
            'source_branch': config['feature_branch'],
            'target_branch': config['base_branch'],
            'reviewers': config['reviewers']
        }
        
        log(f"📋 Creating pull request: {pr_data['title']}")
        
        if config['platform'] == 'bitbucket-server':
            return create_bitbucket_pr(config, pr_data)
        else:
            # For GitHub/GitLab, provide manual instructions
            log(f"⚠️  Automated PR creation not yet implemented for {config['platform']}")
            log("Please create PR manually:")
            log(f"  Source: {config['feature_branch']}")
            log(f"  Target: {config['base_branch']}")
            log(f"  Title: {pr_data['title']}")
            
            return {'success': True, 'message': f"Branch pushed. Please create PR manually for {config['platform']}"}
            
    except Exception as error:
        return {'success': False, 'message': f"PR creation failed: {error}"}

def cleanup_workspace(config):
    """Cleanup workspace"""
    try:
        if os.path.exists(config['workspace_dir']):
            shutil.rmtree(config['workspace_dir'])
            log(f"🧹 Cleaned up workspace: {config['workspace_dir']}")
    except Exception as error:
        log(f"⚠️  Failed to cleanup workspace: {error}")
