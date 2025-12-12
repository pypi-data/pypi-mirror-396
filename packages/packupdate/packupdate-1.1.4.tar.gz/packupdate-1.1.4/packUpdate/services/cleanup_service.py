"""
Package cleanup operations
"""
import subprocess
import json
import os
import shutil
from ..utils.logger import log, write_log

def remove_unused_packages(project_path, quiet_mode):
    """Remove unused dependencies from project"""
    log("\n=== Removing Unused Dependencies ===")
    
    try:
        # Try to use depcheck
        result = subprocess.run(['npx', 'depcheck', '--json'], 
                              cwd=project_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            depcheck_data = json.loads(result.stdout) if result.stdout.strip() else {}
            unused_packages = depcheck_data.get('dependencies', [])
            
            if not unused_packages:
                log("✅ No unused dependencies found.")
                return []
            
            log(f"📦 Found {len(unused_packages)} unused dependencies:")
            for pkg in unused_packages:
                log(f"  - {pkg}")
            
            # Remove unused packages
            removed_packages = []
            for pkg in unused_packages:
                try:
                    log(f"🗑️  Removing {pkg}...")
                    uninstall_result = subprocess.run(['npm', 'uninstall', pkg], 
                                                    cwd=project_path, 
                                                    capture_output=quiet_mode, text=True)
                    
                    if uninstall_result.returncode == 0:
                        removed_packages.append(pkg)
                        write_log(f"SUCCESS: Removed unused package {pkg}")
                    else:
                        write_log(f"ERROR: Failed to remove {pkg}")
                except Exception as e:
                    write_log(f"ERROR: Failed to remove {pkg}: {e}")
            
            log(f"✅ Removed {len(removed_packages)} unused dependencies.")
            return removed_packages
        else:
            # Fallback to basic analysis
            log("⚠️  Depcheck not available, using basic analysis...")
            return remove_unused_basic_analysis(project_path, quiet_mode)
            
    except Exception as e:
        log("⚠️  Depcheck not available, using basic analysis...")
        return remove_unused_basic_analysis(project_path, quiet_mode)

def remove_unused_basic_analysis(project_path, quiet_mode):
    """Basic unused package analysis when depcheck is not available"""
    package_json_path = os.path.join(project_path, "package.json")
    if not os.path.exists(package_json_path):
        return []
    
    try:
        with open(package_json_path, 'r') as f:
            package_json = json.load(f)
        
        dependencies = list(package_json.get('dependencies', {}).keys())
        
        # Simple heuristic: check if package is imported in common files
        common_files = ['src', 'lib', 'index.js', 'index.ts', 'app.js', 'app.ts']
        potentially_unused = []
        
        for dep in dependencies:
            found = False
            for file_name in common_files:
                file_path = os.path.join(project_path, file_name)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read().lower()
                            if dep.lower() in content:
                                found = True
                                break
                    except:
                        continue
            if not found:
                potentially_unused.append(dep)
        
        if potentially_unused:
            log("⚠️  Potentially unused packages (manual review recommended):")
            for pkg in potentially_unused:
                log(f"  - {pkg}")
        
        return []  # Don't auto-remove with basic analysis
    except Exception as e:
        write_log(f"ERROR: Basic analysis failed: {e}")
        return []

def dedupe_packages(project_path, quiet_mode):
    """Remove duplicate dependencies"""
    log("\n=== Deduplicating Dependencies ===")
    
    try:
        # Run npm dedupe
        log("🔄 Running npm dedupe...")
        result = subprocess.run(['npm', 'dedupe'], 
                              cwd=project_path, 
                              capture_output=quiet_mode, text=True)
        
        if result.returncode == 0:
            log("✅ Dependencies deduplicated successfully.")
            write_log("SUCCESS: npm dedupe completed")
            
            # Get dedupe statistics
            audit_result = subprocess.run(['npm', 'ls', '--depth=0'], 
                                        cwd=project_path, 
                                        capture_output=True, text=True)
            
            # Count unique packages (simplified)
            lines = audit_result.stdout.split('\n') if audit_result.stdout else []
            package_count = len([line for line in lines if '├──' in line or '└──' in line])
            
            log(f"📦 {package_count} unique packages remaining.")
            return package_count
        else:
            error_msg = "npm dedupe failed"
            log(f"❌ {error_msg}")
            write_log(f"ERROR: {error_msg}")
            return 0
    except Exception as e:
        error_msg = f"Dedupe failed: {e}"
        log(f"❌ {error_msg}")
        write_log(f"ERROR: {error_msg}")
        return 0

def cleanup_package_files(project_path, quiet_mode):
    """Clean up package-lock.json and node_modules"""
    log("\n=== Cleaning Package Files ===")
    
    try:
        # Remove node_modules and package-lock.json
        node_modules_path = os.path.join(project_path, "node_modules")
        package_lock_path = os.path.join(project_path, "package-lock.json")
        
        if os.path.exists(node_modules_path):
            log("🗑️  Removing node_modules...")
            shutil.rmtree(node_modules_path)
        
        if os.path.exists(package_lock_path):
            log("🗑️  Removing package-lock.json...")
            os.remove(package_lock_path)
        
        # Fresh install
        log("📦 Running fresh npm install...")
        result = subprocess.run(['npm', 'install'], 
                              cwd=project_path, 
                              capture_output=quiet_mode, text=True)
        
        if result.returncode == 0:
            log("✅ Fresh installation completed.")
            write_log("SUCCESS: Package files cleaned and reinstalled")
        else:
            raise Exception("npm install failed")
    except Exception as e:
        error_msg = f"Cleanup failed: {e}"
        log(f"❌ {error_msg}")
        write_log(f"ERROR: {error_msg}")
