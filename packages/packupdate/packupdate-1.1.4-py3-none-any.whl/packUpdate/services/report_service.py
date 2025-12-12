"""
Security and dependency report generation
"""
import subprocess
import json
import os
from datetime import datetime
from ..utils.logger import log, write_log, get_log_dir
from .package_service import get_outdated_packages

def generate_security_report(project_path):
    """Generate security audit report."""
    try:
        result = subprocess.run(['npm', 'audit', '--json'], cwd=project_path, capture_output=True, text=True)
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except:
        return {}

def generate_dependency_report(project_path):
    """Generate dependency tree report."""
    try:
        result = subprocess.run(['npm', 'ls', '--json', '--all'], cwd=project_path, capture_output=True, text=True)
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except:
        return {}

def find_circular_dependencies(deps, visited=None, path=None):
    """Find circular dependencies in the dependency tree."""
    if visited is None:
        visited = set()
    if path is None:
        path = []
    
    circular = []
    if not deps or 'dependencies' not in deps:
        return circular
    
    for name, info in deps['dependencies'].items():
        if name in visited:
            if name in path:
                circular.append(' → '.join(path + [name]))
            continue
        visited.add(name)
        circular.extend(find_circular_dependencies(info, visited, path + [name]))
    
    return circular

def check_breaking_changes(package_name, current_version, latest_version):
    """Check for breaking changes in package updates"""
    # Check if major version change (likely breaking)
    try:
        current_major = int(current_version.split('.')[0])
        latest_major = int(latest_version.split('.')[0])
        has_major_change = latest_major > current_major
    except:
        has_major_change = False
    
    # Get package info for changelog analysis
    try:
        result = subprocess.run(['npm', 'info', package_name, '--json'], capture_output=True, text=True)
        package_info = json.loads(result.stdout) if result.stdout.strip() else {}
    except:
        package_info = {}
    
    return {
        'hasMajorVersionChange': has_major_change,
        'riskLevel': 'high' if has_major_change else 'low',
        'changelog': package_info.get('homepage', ''),
        'repository': package_info.get('repository', {}).get('url', '') if isinstance(package_info.get('repository'), dict) else '',
        'hasBreakingChanges': has_major_change,
        'migrationRequired': has_major_change
    }

def check_peer_dependencies(package_name, project_path):
    """Check peer dependency compatibility"""
    try:
        result = subprocess.run(['npm', 'info', package_name, 'peerDependencies', '--json'], 
                              cwd=project_path, capture_output=True, text=True)
        peer_deps = json.loads(result.stdout) if result.stdout.strip() else {}
    except:
        peer_deps = {}
    
    return {
        'hasPeerDependencies': len(peer_deps) > 0,
        'peerDependencies': peer_deps,
        'compatibilityIssues': []  # Simplified for now
    }

def analyze_breaking_changes(outdated_packages, project_path):
    """Analyze breaking changes for all outdated packages"""
    analysis = {
        'safeUpdates': [],
        'riskyUpdates': [],
        'breakingChanges': {},
        'peerDependencyIssues': {}
    }
    
    for package_name, details in outdated_packages.items():
        breaking_analysis = check_breaking_changes(package_name, details.get('current', ''), details.get('latest', ''))
        peer_analysis = check_peer_dependencies(package_name, project_path)
        
        analysis['breakingChanges'][package_name] = breaking_analysis
        analysis['peerDependencyIssues'][package_name] = peer_analysis
        
        # Categorize as safe or risky
        if breaking_analysis['riskLevel'] == 'low' and not peer_analysis['hasPeerDependencies']:
            analysis['safeUpdates'].append(package_name)
        else:
            analysis['riskyUpdates'].append(package_name)
    
    return analysis

def generate_comprehensive_report(project_path):
    """Generate comprehensive security and dependency report."""
    log("\n=== Generating Comprehensive Security & Dependency Report ===")
    
    security_report = generate_security_report(project_path)
    dependency_report = generate_dependency_report(project_path)
    outdated_packages = get_outdated_packages(project_path)
    breaking_change_analysis = analyze_breaking_changes(outdated_packages, project_path)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'project': project_path,
        'security': {
            'vulnerabilities': security_report.get('vulnerabilities', {}),
            'summary': security_report.get('metadata', {}),
            'vulnerable_packages': list(security_report.get('vulnerabilities', {}).keys())
        },
        'dependencies': {
            'total': len(dependency_report.get('dependencies', {})),
            'circular': find_circular_dependencies(dependency_report),
            'outdated': len(outdated_packages),
            'outdated_list': outdated_packages
        },
        'breakingChanges': {
            'safeUpdates': breaking_change_analysis['safeUpdates'],
            'riskyUpdates': breaking_change_analysis['riskyUpdates'],
            'analysis': breaking_change_analysis['breakingChanges'],
            'peerDependencyIssues': breaking_change_analysis['peerDependencyIssues']
        },
        'recommendations': []
    }
    
    # Add recommendations
    if report['security']['vulnerable_packages']:
        report['recommendations'].append("Run with --security-only to update vulnerable packages")
    if report['dependencies']['circular']:
        report['recommendations'].append("Review circular dependencies for potential refactoring")
    if report['dependencies']['outdated'] > 0:
        report['recommendations'].append("Consider updating outdated packages with --minor-only for safer updates")
    if report['breakingChanges']['safeUpdates']:
        report['recommendations'].append(f"{len(report['breakingChanges']['safeUpdates'])} packages can be safely updated without breaking changes")
    if report['breakingChanges']['riskyUpdates']:
        report['recommendations'].append(f"{len(report['breakingChanges']['riskyUpdates'])} packages may have breaking changes - review before updating")
    
    report_file = os.path.join(get_log_dir(), f"security-report-{datetime.now().isoformat().replace(':', '-').replace('.', '-')}.json")
    if not os.path.exists(get_log_dir()):
        os.makedirs(get_log_dir(), exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Display summary
    display_report_summary(report, report_file)
    write_log(f"Comprehensive report generated: {report_file}")

def display_report_summary(report, report_file):
    """Display formatted report summary to console"""
    log(f"\n📊 SECURITY & DEPENDENCY REPORT")
    log(f"📁 Project: {report['project']}")
    log(f"🔒 Vulnerabilities: {len(report['security']['vulnerable_packages'])}")
    log(f"📦 Total Dependencies: {report['dependencies']['total']}")
    log(f"🔄 Circular Dependencies: {len(report['dependencies']['circular'])}")
    log(f"⚠️  Outdated Packages: {report['dependencies']['outdated']}")
    
    # Breaking changes summary
    log(f"\n🔍 BREAKING CHANGE ANALYSIS")
    log(f"✅ Safe Updates: {len(report['breakingChanges']['safeUpdates'])}")
    log(f"⚠️  Risky Updates: {len(report['breakingChanges']['riskyUpdates'])}")
    
    if report['security']['vulnerable_packages']:
        log(f"\n🚨 VULNERABLE PACKAGES:")
        for pkg in report['security']['vulnerable_packages']:
            log(f"  - {pkg}")
    
    if report['dependencies']['circular']:
        log(f"\n🔄 CIRCULAR DEPENDENCIES:")
        for cycle in report['dependencies']['circular']:
            log(f"  - {cycle}")
    
    if report['breakingChanges']['safeUpdates']:
        log(f"\n✅ SAFE UPDATES (No Breaking Changes):")
        for pkg in report['breakingChanges']['safeUpdates']:
            log(f"  - {pkg}")
    
    if report['breakingChanges']['riskyUpdates']:
        log(f"\n⚠️  RISKY UPDATES (Potential Breaking Changes):")
        for pkg in report['breakingChanges']['riskyUpdates']:
            log(f"  - {pkg}")
    
    log(f"\n💡 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        log(f"  - {rec}")
    
    log(f"\n📄 Full report saved: {report_file}")

def get_safe_packages_for_update(project_path):
    """Get safe packages for priority updating"""
    outdated_packages = get_outdated_packages(project_path)
    breaking_change_analysis = analyze_breaking_changes(outdated_packages, project_path)
    return breaking_change_analysis['safeUpdates']
