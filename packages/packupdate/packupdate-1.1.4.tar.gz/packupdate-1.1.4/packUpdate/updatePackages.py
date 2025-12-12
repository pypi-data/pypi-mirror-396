"""
PackUpdate - Python Package Updater
Main entry point for the application
"""
import os
import sys
from .utils.logger import set_quiet_mode, write_log, log, get_log_file
from .utils.cli import parse_cli_args, handle_special_flags
from .services.report_service import generate_comprehensive_report
from .services.package_service import get_outdated_packages, get_dependency_tree, install_package
from .services.interactive_service import InteractiveService
from .services.automation_service import (
    create_automation_config, validate_automation_config, setup_workspace,
    commit_and_push, create_pull_request, cleanup_workspace
)
from .services.version_service import VersionService

def validate_project_path(project_path):
    """Validate project path exists and is a directory"""
    if not os.path.isdir(project_path):
        error_msg = f"Error: {project_path} is not a valid directory."
        print(error_msg)
        write_log(f"ERROR: {error_msg}")
        sys.exit(1)

def resolve_update_order(outdated_packages, dependency_tree):
    """Determine the order of updates based on interdependencies among outdated packages."""
    resolved_order = []
    visited = set()

    def visit(package):
        if package in visited:
            return
        visited.add(package)
        dependencies = dependency_tree.get('dependencies', {}).get(package, {}).get('requires', {})
        for dep in dependencies:
            if dep in outdated_packages:
                visit(dep)
        resolved_order.append(package)

    for package in outdated_packages:
        visit(package)
    
    return resolved_order

def execute_script_if_exist(project_path, script_name, quiet_mode):
    """Check if the project has a script in package.json."""
    import json
    import subprocess
    
    package_json_path = os.path.join(project_path, "package.json")
    if not os.path.isfile(package_json_path):
        return False
        
    try:
        with open(package_json_path, "r") as f:
            package_data = json.load(f)
        script_exists = script_name in package_data.get("scripts", {})
        returnCode = 0
        if script_exists:
            script_execute = subprocess.run(["npm", "run", script_name], cwd=project_path, 
                                          capture_output=quiet_mode, text=True)
            returnCode = script_execute.returncode
        else:
            returnCode = 0
            log(f"No {script_name} script found in package.json. Skipping.")
        return returnCode == 0
    except Exception as e:
        error_msg = f"Error reading package.json: {e}"
        print(error_msg)
        write_log(f"ERROR: {error_msg}")
        return False

def run_tests(project_path, quiet_mode):
    """Run build and test scripts"""
    log("\nRunning build...")
    resultBuild = execute_script_if_exist(project_path, "build", quiet_mode)
    log("\nRunning tests...")
    resultTest = execute_script_if_exist(project_path, "test", quiet_mode)
    if resultBuild == False or resultTest == False:
        error_msg = "Tests failed."
        write_log(f"ERROR: {error_msg}")
        raise Exception(error_msg)

def update_packages_in_order(outdated_packages, dependency_tree, project_path, safe_mode, quiet_mode):   
    """Update packages in the resolved order."""
    from .services.report_service import get_safe_packages_for_update
    
    original_order = resolve_update_order(outdated_packages, dependency_tree)
    
    # Get safe packages and prioritize them
    safe_packages = get_safe_packages_for_update(project_path)
    safe_in_order = [pkg for pkg in original_order if pkg in safe_packages]
    risky_in_order = [pkg for pkg in original_order if pkg not in safe_packages]
    
    log(f"\n🔍 UPDATE PRIORITIZATION:")
    log(f"✅ Safe packages (no breaking changes): {len(safe_in_order)}")
    log(f"⚠️  Risky packages (potential breaking changes): {len(risky_in_order)}")
    
    update_order = safe_in_order + risky_in_order
    log("\nFinal Update Order: " + ", ".join(update_order))
    
    failed_updates = []
    updated_packages = []

    for package in update_order:
        details = outdated_packages[package]
        current_version = details.get("current")
        wanted_version = details.get("wanted")
        latest_version = details.get("latest")
        original_version = current_version  # Store the actual original version
        final_version = current_version
        is_safe = package in safe_packages
        
        log(f"\n{'✅' if is_safe else '⚠️'} Updating {package} ({'safe' if is_safe else 'risky'})...")
        
        update_successful = False
        
        if safe_mode:
            # Try latest → wanted → revert (with tests after each)
            
            # Try latest version first
            try:
                log(f"  Trying latest version {latest_version}...")
                install_package(package, latest_version, project_path, safe_mode, quiet_mode)
                run_tests(project_path, quiet_mode)
                final_version = latest_version
                update_successful = True
                log(f"  ✅ Latest version {latest_version} works!")
            except Exception as error:
                log(f"  ❌ Latest version {latest_version} failed: {error}")
                
                # Try wanted version
                if wanted_version and wanted_version != latest_version and wanted_version != original_version:
                    try:
                        log(f"  Trying wanted version {wanted_version}...")
                        install_package(package, wanted_version, project_path, safe_mode, quiet_mode)
                        run_tests(project_path, quiet_mode)
                        final_version = wanted_version
                        update_successful = True
                        log(f"  ✅ Wanted version {wanted_version} works!")
                    except Exception as error:
                        log(f"  ❌ Wanted version {wanted_version} failed: {error}")
                
                # Revert to original version if both failed
                if not update_successful:
                    try:
                        log(f"  Reverting to original version {original_version}...")
                        install_package(package, original_version, project_path, safe_mode, quiet_mode)
                        run_tests(project_path, quiet_mode)
                        final_version = original_version
                        log(f"  ✅ Reverted to original version {original_version}")
                    except Exception as error:
                        log(f"  ❌ Even revert failed: {error}")
                        failed_updates.append(package)
                        write_log(f"FAILED: {package} update failed completely")
                        updated_packages.append((package, current_version, final_version))
                        continue
            
            # Log success
            if update_successful:
                write_log(f"SUCCESS: Updated {package} from {current_version} to {final_version} ({'safe' if is_safe else 'risky'})")
        else:
            # Without safe mode, just try latest
            if current_version and latest_version and current_version != latest_version:
                try:
                    install_package(package, latest_version, project_path, safe_mode, quiet_mode)
                    final_version = latest_version
                    update_successful = True
                    write_log(f"SUCCESS: Updated {package} from {current_version} to {latest_version} ({'safe' if is_safe else 'risky'})")
                except Exception as e:
                    error_msg = f"Failed to update {package}: {e}"
                    write_log(f"ERROR: {error_msg}")
                    failed_updates.append(package)
                    write_log(f"FAILED: {package} update failed")
            else:
                log(f"Skipping {package}, already at latest version or missing version info.")
        
        updated_packages.append((package, current_version, final_version))
    return updated_packages, failed_updates

def run_update_process(project_path, safe_mode, passes, minor_only, quiet_mode, update_version=None):
    """Execute update process with multiple passes"""
    import subprocess
    
    all_updated_packages = []
    all_failed_updates = []
    
    for i in range(passes):
        log(f"\n=== Pass {i + 1} ===")
        outdated_packages = get_outdated_packages(project_path, minor_only)
        if not outdated_packages:
            log("No more outdated packages found.")
            break
        
        dependency_tree = get_dependency_tree(project_path)
        updated_packages, failed_updates = update_packages_in_order(outdated_packages, dependency_tree, project_path, safe_mode, quiet_mode)
        all_updated_packages.append((i + 1, updated_packages))
        all_failed_updates.extend(failed_updates)
    
    log("\nRunning final npm audit and build...")
    subprocess.run(["npm", "audit", "fix"], cwd=project_path, capture_output=quiet_mode, text=True)
    execute_script_if_exist(project_path, "build", quiet_mode)
    print_update_summary(all_updated_packages, all_failed_updates)
    
    # Update project version if requested and updates were successful
    if update_version and any(updated_packages for _, updated_packages in all_updated_packages):
        VersionService.update_project_version(project_path, update_version, quiet_mode)

def print_update_summary(all_updated_packages, all_failed_updates):
    """Print the final summary of updated packages for standard update process."""
    log("\nFinal Update Summary:")
    log("{:<40} {:<10} {:<10}".format("Package", "Old Version", "New Version"))
    log("-" * 60)
    for pass_num, updated_packages in all_updated_packages:
        log(f"\n=== Pass {pass_num} ===")
        for package, old_version, new_version in updated_packages:
            log("{:<40} {:<10} {:<10}".format(package, old_version, new_version))
    log("-" * 60)

    if all_failed_updates:
        log("\nPackages that failed to update:")
        for package in set(all_failed_updates):
            log(f"- {package}")

def run_interactive_mode(project_path, safe_mode, quiet_mode, update_version=None):
    """Execute interactive mode for selective package updates"""
    try:
        log("🔍 Checking for outdated packages...")
        outdated_packages = get_outdated_packages(project_path)
        
        if not outdated_packages:
            log("✅ All packages are up to date!")
            return

        selected_packages = InteractiveService.select_packages(outdated_packages)
        
        if not selected_packages:
            log("No packages selected for update.")
            return

        confirmed = InteractiveService.confirm_updates(selected_packages)
        if not confirmed:
            log("Update cancelled by user.")
            return

        log("\n🚀 Starting interactive updates...")
        
        # Process selected packages
        updated_packages = []
        failed_updates = []
        
        for choice in selected_packages:
            target_version = choice.latest if choice.update_type == 'major' else choice.wanted
            log(f"\nUpdating {choice.name} from {choice.current} to {target_version}...")
            
            try:
                success = install_package(choice.name, target_version, project_path, safe_mode, quiet_mode)
                if success:
                    updated_packages.append((choice.name, choice.current, target_version))
                    log(f"✅ Successfully updated {choice.name}")
                else:
                    failed_updates.append(choice.name)
                    log(f"❌ Failed to update {choice.name}")
            except Exception as error:
                failed_updates.append(choice.name)
                log(f"❌ Failed to update {choice.name}: {error}")

        # Print summary
        log("\n" + "=" * 60)
        log("Interactive Update Summary:")
        log("{:<40} {:<10} {:<10}".format("Package", "Old Version", "New Version"))
        log("-" * 60)
        
        if updated_packages:
            for package, old_version, new_version in updated_packages:
                log("{:<40} {:<10} {:<10}".format(package, old_version, new_version))
        
        if failed_updates:
            log("\nPackages that failed to update:")
            for package in failed_updates:
                log(f"- {package}")
        
        # Update project version if requested and updates were successful
        if update_version and updated_packages:
            VersionService.update_project_version(project_path, update_version, quiet_mode)
            
    except Exception as error:
        log(f"❌ Interactive mode failed: {error}")
        raise error

def handle_cleanup_operations(project_path, remove_unused, dedupe_packages, quiet_mode):
    """Handle cleanup operations"""
    from .services.cleanup_service import remove_unused_packages, dedupe_packages as dedupe_func
    
    log("\n=== Package Cleanup Operations ===")
    
    if remove_unused:
        removed_packages = remove_unused_packages(project_path, quiet_mode)
        log(f"\n✅ Cleanup Summary: Removed {len(removed_packages)} unused packages")
    
    if dedupe_packages:
        package_count = dedupe_func(project_path, quiet_mode)
        log(f"\n✅ Dedupe Summary: {package_count} unique packages remaining")
    
    write_log(f"Cleanup operations completed - Log file: {get_log_file()}")
    print(f"Log file created: {get_log_file()}")

def execute_automation_workflow(cli_args):
    """Execute automation workflow"""
    config = create_automation_config(cli_args)
    
    try:
        # Validate configuration
        validate_automation_config(config)
        
        log("\n🤖 Starting PackUpdate Automation Workflow")
        log(f"📁 Repository: {config['repository']}")
        log(f"🌿 Feature Branch: {config['feature_branch']}")
        log(f"🎯 Base Branch: {config['base_branch']}")
        
        # Setup workspace and clone repository
        setup_result = setup_workspace(config)
        if not setup_result['success']:
            raise Exception(setup_result['message'])
        
        # Generate initial report in the cloned repository
        log("\n📊 Generating pre-update report...")
        report_path = config['workspace_dir']
        
        # Generate comprehensive report (this will be used for PR description)
        report_data = {}
        try:
            generate_comprehensive_report(report_path)
            
            # Get outdated packages for the report
            outdated_packages = get_outdated_packages(report_path)
            report_data = {
                'dependencies': {
                    'outdated': len(outdated_packages),
                    'outdated_list': outdated_packages
                },
                'security': {'vulnerable_packages': []},
                'breakingChanges': {'safeUpdates': [], 'riskyUpdates': []},
                'recommendations': []
            }
        except Exception as error:
            log(f"⚠️  Report generation failed: {error}")
        
        # Execute package updates in the cloned repository
        log("\n🚀 Executing package updates...")
        minor_only = cli_args['minor_only']
        quiet_mode = cli_args['quiet_mode']
        passes = cli_args['passes']
        update_version = cli_args['update_version']
        safe_mode = True  # Always use safe mode for automation to ensure tests pass
        
        log("🛡️  Safe mode enabled for automation - tests will run after each update")
        
        all_results = []
        for i in range(passes):
            log(f"\n=== Pass {i + 1} ===")
            result = run_single_update_pass(report_path, safe_mode, minor_only, quiet_mode)
            all_results.append(result)

            if not result.get('updated'):
                log("No more outdated packages found.")
                break
        
        # Update project version if requested and updates were successful
        if update_version and any(result.get('updated') for result in all_results):
            VersionService.update_project_version(report_path, update_version, quiet_mode)
        
        # Print summary
        print_automation_summary(all_results, passes)
        
        # Commit and push changes
        commit_result = commit_and_push(config, all_results)
        if not commit_result['success']:
            if all(not result.get('updated') for result in all_results):
                log("✅ No packages needed updating - repository is already up to date!")
                log("🎉 Automation workflow completed successfully (no changes needed)!")
                return
            else:
                raise Exception(commit_result['message'])
        
        # Create pull request
        pr_result = create_pull_request(config, all_results, report_data)
        if pr_result['success'] and pr_result.get('pr_url'):
            log(f"✅ Pull request created: {pr_result['pr_url']}")
        else:
            log(f"⚠️  {pr_result['message']}")
        
        log("\n🎉 Automation workflow completed successfully!")
        
    except Exception as error:
        log(f"❌ Automation workflow failed: {error}")
        raise error
    finally:
        # Always cleanup workspace
        cleanup_workspace(config)

def run_single_update_pass(project_path, safe_mode, minor_only, quiet_mode):
    """Run a single update pass and return results"""
    outdated_packages = get_outdated_packages(project_path, minor_only)
    
    if not outdated_packages:
        return {'updated': [], 'failed': []}
    
    dependency_tree = get_dependency_tree(project_path)
    update_order = resolve_update_order(outdated_packages, dependency_tree)
    
    updated_packages = []
    failed_updates = []
    
    for package in update_order:
        details = outdated_packages[package]
        target_version = details['latest']
        
        log(f"Updating {package} from {details['current']} to {target_version}...")
        
        try:
            success = install_package(package, target_version, project_path, safe_mode, quiet_mode)
            if success:
                updated_packages.append((package, details['current'], target_version))
                log(f"✅ Successfully updated {package}")
            else:
                failed_updates.append(package)
                log(f"❌ Failed to update {package}")
        except Exception as error:
            failed_updates.append(package)
            log(f"❌ Failed to update {package}: {error}")
    
    return {'updated': updated_packages, 'failed': failed_updates}

def print_automation_summary(all_results, passes):
    """Print final summary of all update passes for automation workflow"""
    log("\n" + "=" * 60)
    log("Final Update Summary:")
    log("{:<40} {:<12} {:<12}".format("Package", "Old Version", "New Version"))
    log("-" * 60)
    
    total_updated = 0
    total_failed = 0
    
    for i, result in enumerate(all_results):
        if result.get('updated'):
            log(f"\n=== Pass {i + 1} ===")
            for package, old_version, new_version in result['updated']:
                log("{:<40} {:<12} {:<12}".format(package, old_version, new_version))
                total_updated += 1
        
        total_failed += len(result.get('failed', []))
    
    if total_failed > 0:
        log(f"\nPackages that failed to update across all passes: {total_failed}")
        for result in all_results:
            for package in result.get('failed', []):
                log(f"- {package}")
    
    log(f"\nTotal packages updated: {total_updated}")
    log(f"Total packages failed: {total_failed}")

def main():
    """Main application entry point"""
    # Handle special flags first (help, version, type)
    if handle_special_flags():
        return

    # Parse CLI arguments
    cli_args = parse_cli_args()
    project_path = cli_args['project_path']
    safe_mode = cli_args['safe_mode']
    interactive = cli_args['interactive']
    minor_only = cli_args['minor_only']
    generate_report = cli_args['generate_report']
    remove_unused = cli_args['remove_unused']
    dedupe_packages = cli_args['dedupe_packages']
    quiet_mode = cli_args['quiet_mode']
    passes = cli_args['passes']
    update_version = cli_args['update_version']
    automate = cli_args['automate']

    # Set up logging
    set_quiet_mode(quiet_mode)
    write_log(f"PackUpdate started - Project: {project_path}, Safe Mode: {safe_mode}, Interactive: {interactive}, Minor Only: {minor_only}, Generate Report: {generate_report}, Remove Unused: {remove_unused}, Dedupe: {dedupe_packages}, Passes: {passes}, Update Version: {update_version or 'none'}, Quiet: {quiet_mode}, Automate: {automate or False}")
    
    # Handle automation workflow
    if automate:
        execute_automation_workflow(cli_args)
        return
    
    # Validate project path for non-automation workflows
    validate_project_path(project_path)
    
    # Handle cleanup operations
    if remove_unused or dedupe_packages:
        handle_cleanup_operations(project_path, remove_unused, dedupe_packages, quiet_mode)
        return
    
    # Handle report generation (no updates)
    if generate_report:
        generate_comprehensive_report(project_path)
        return
    
    # Handle interactive mode
    if interactive:
        run_interactive_mode(project_path, safe_mode, quiet_mode, update_version)
        return
    
    # Execute update process
    run_update_process(project_path, safe_mode, passes, minor_only, quiet_mode, update_version)
    
    # Log completion
    write_log(f"PackUpdate completed - Log file: {get_log_file()}")
    print(f"Log file created: {get_log_file()}")

if __name__ == "__main__":
    main()
