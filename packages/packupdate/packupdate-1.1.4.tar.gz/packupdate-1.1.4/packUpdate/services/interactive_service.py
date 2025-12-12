"""Interactive service for package selection"""
import inquirer
from typing import Dict, List, Optional

class PackageChoice:
    def __init__(self, name: str, current: str, wanted: str, latest: str, update_type: str):
        self.name = name
        self.current = current
        self.wanted = wanted
        self.latest = latest
        self.update_type = update_type

class InteractiveService:
    @staticmethod
    def select_packages(outdated_packages: Dict[str, Dict[str, str]]) -> List[PackageChoice]:
        """Select packages interactively"""
        if not outdated_packages:
            print('✅ No outdated packages found!')
            return []

        print('\n📦 Found outdated packages:\n')
        
        choices = []
        for name, info in outdated_packages.items():
            has_minor = info['current'] != info['wanted']
            has_major = info['wanted'] != info['latest']
            
            description = f"{name}: {info['current']}"
            if has_minor:
                description += f" → {info['wanted']} (minor)"
            if has_major:
                description += f" → {info['latest']} (major)"
            
            choices.append((description, {'name': name, **info}))

        questions = [
            inquirer.Checkbox(
                'selected_packages',
                message='Select packages to update:',
                choices=choices,
            )
        ]

        answers = inquirer.prompt(questions)
        selected_packages = answers.get('selected_packages', [])

        if not selected_packages:
            print('No packages selected for update.')
            return []

        package_choices = []

        for pkg in selected_packages:
            has_minor = pkg['current'] != pkg['wanted']
            has_major = pkg['wanted'] != pkg['latest']
            
            update_options = []
            if has_minor:
                update_options.append(f"Minor: {pkg['current']} → {pkg['wanted']}")
            if has_major:
                update_options.append(f"Major: {pkg['current']} → {pkg['latest']}")
            update_options.append('Skip this package')

            if len(update_options) == 1:
                continue

            questions = [
                inquirer.List(
                    'update_type',
                    message=f"How do you want to update {pkg['name']}?",
                    choices=update_options,
                )
            ]

            answer = inquirer.prompt(questions)
            update_choice = answer['update_type']

            if 'Skip' in update_choice:
                continue

            update_type = 'major' if 'Major:' in update_choice else 'minor'
            
            package_choices.append(PackageChoice(
                name=pkg['name'],
                current=pkg['current'],
                wanted=pkg['wanted'],
                latest=pkg['latest'],
                update_type=update_type
            ))

        return package_choices

    @staticmethod
    def confirm_updates(choices: List[PackageChoice]) -> bool:
        """Confirm updates with user"""
        if not choices:
            return False

        print('\n📋 Update Summary:')
        for choice in choices:
            target_version = choice.latest if choice.update_type == 'major' else choice.wanted
            print(f"  {choice.name}: {choice.current} → {target_version} ({choice.update_type})")

        questions = [
            inquirer.Confirm(
                'confirm',
                message='Proceed with these updates?',
                default=True
            )
        ]

        answer = inquirer.prompt(questions)
        return answer.get('confirm', False)
