"""Version service for updating project version"""
import json
import os
import re
from typing import Optional
from ..utils.logger import log

class VersionService:
    @staticmethod
    def update_project_version(project_path: str, version_type: str, quiet_mode: bool = False) -> None:
        """Update project version in package.json and package-lock.json"""
        try:
            package_json_path = os.path.join(project_path, 'package.json')
            
            if not os.path.exists(package_json_path):
                log('⚠️  No package.json found, skipping version update')
                return

            with open(package_json_path, 'r') as f:
                package_json = json.load(f)
            
            current_version = package_json.get('version', '1.0.0')
            
            if VersionService._is_valid_semver(version_type):
                new_version = version_type
            else:
                new_version = VersionService._calculate_new_version(current_version, version_type)
                if not new_version:
                    log(f'❌ Invalid version type: {version_type}. Use major, minor, patch, or x.y.z format')
                    return

            # Update package.json
            package_json['version'] = new_version
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f, indent=2)
                f.write('\n')
            
            # Update package-lock.json if it exists
            package_lock_path = os.path.join(project_path, 'package-lock.json')
            if os.path.exists(package_lock_path):
                with open(package_lock_path, 'r') as f:
                    package_lock = json.load(f)
                
                package_lock['version'] = new_version
                if 'packages' in package_lock and '' in package_lock['packages']:
                    package_lock['packages']['']['version'] = new_version
                
                with open(package_lock_path, 'w') as f:
                    json.dump(package_lock, f, indent=2)
                    f.write('\n')

            log(f'📦 Updated project version: {current_version} → {new_version}')
            
        except Exception as error:
            log(f'❌ Failed to update project version: {error}')

    @staticmethod
    def _is_valid_semver(version: str) -> bool:
        """Check if string is valid semver format (x.y.z)"""
        semver_regex = r'^\d+\.\d+\.\d+$'
        return bool(re.match(semver_regex, version))

    @staticmethod
    def _calculate_new_version(current_version: str, version_type: str) -> Optional[str]:
        """Calculate new version based on current version and type"""
        try:
            parts = [int(x) for x in current_version.split('.')]
            if len(parts) != 3:
                return None

            major, minor, patch = parts

            if version_type.lower() == 'major':
                major += 1
                minor = 0
                patch = 0
            elif version_type.lower() == 'minor':
                minor += 1
                patch = 0
            elif version_type.lower() == 'patch':
                patch += 1
            else:
                return None

            return f'{major}.{minor}.{patch}'
        except (ValueError, IndexError):
            return None
