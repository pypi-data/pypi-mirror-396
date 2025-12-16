import os
import re
import shutil
import subprocess
from io import StringIO
from pathlib import Path

import httpx
from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Generate Django migration SQL preview and post/update GitLab MR comment'
    requires_system_checks: list[str] = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--target-branch',
            type=str,
            default=None,
            help='Target branch to compare against (defaults to CI_MERGE_REQUEST_TARGET_BRANCH_NAME env var)',
        )
        parser.add_argument('--dry-run', action='store_true', help='Generate SQL preview without posting to GitLab')
        parser.add_argument(
            '--comment-body',
            type=str,
            default=None,
            help='Custom comment body (if not provided, will generate migration SQL preview)',
        )
        parser.add_argument(
            '--gitlab-api-token',
            type=str,
            default=None,
            help='GitLab API token (if not provided, will use it from environment variable GITLAB_API_TOKEN)',
        )

    def handle(self, *args, **options):
        # Get environment variables
        try:
            api_url = os.environ['CI_API_V4_URL']
            project_id = os.environ['CI_PROJECT_ID']
            mr_iid = os.environ['CI_MERGE_REQUEST_IID']
            token = options['gitlab_api_token'] or os.environ['GITLAB_API_TOKEN']
        except KeyError as e:
            if options['dry_run']:
                self.stdout.write(self.style.WARNING(f'Missing environment variable {e} (ignored in dry-run mode)'))
                api_url = project_id = mr_iid = token = None
            else:
                raise CommandError(f'Missing required environment variable: {e}') from e

        # Determine target branch
        target_branch = options['target_branch'] or os.environ.get('CI_MERGE_REQUEST_TARGET_BRANCH_NAME')
        if not target_branch:
            target_branch = 'main'  # Default fallback
            self.stdout.write(self.style.WARNING(f'No target branch specified, using default: {target_branch}'))

        # Generate comment body if not provided
        if options['comment_body']:
            comment_body = options['comment_body']
        else:
            comment_body = self.generate_migration_sql_preview(target_branch)
            if not comment_body:
                self.stdout.write(self.style.SUCCESS('No new Django migration files found in this MR.'))
                return

        # Print preview in dry-run mode
        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS('Generated comment body:'))
            self.stdout.write('=' * 50)
            self.stdout.write(comment_body)
            self.stdout.write('=' * 50)
            return

        # Post/update GitLab comment
        self.post_gitlab_comment(api_url, project_id, mr_iid, token, comment_body)

    def generate_migration_sql_preview(self, target_branch: str) -> str | None:
        """Generate SQL preview for new migration files in the MR."""
        self.stdout.write('Checking for new migration files...')

        # Find new migration files
        migration_files = self._get_new_migration_files(target_branch)

        if not migration_files:
            return None

        self.stdout.write(f'Found {len(migration_files)} new migration file(s)')

        # Generate comment body
        return self._build_comment_body(migration_files)

    def _get_new_migration_files(self, target_branch: str) -> list[str]:
        """Get list of new migration files from git diff."""
        try:
            git_path = shutil.which('git') or '/usr/bin/git'
            result = subprocess.run(  # noqa: S603
                [git_path, 'diff', '--name-only', '--diff-filter=A', f'origin/{target_branch}...HEAD'],
                capture_output=True,
                text=True,
                check=True,
            )

            all_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

            # Filter for migration files using list comprehension
            return [file for file in all_files if self._is_migration_file(file)]

        except subprocess.CalledProcessError as e:
            raise CommandError(f'Failed to get git diff: {e}') from e

    def _is_migration_file(self, file_path: str) -> bool:
        """Check if a file path represents a Django migration file."""
        if not file_path:
            return False

        return (
            '/migrations/' in file_path
            and file_path.endswith('.py')
            and '__pycache__' not in file_path
            and
            # Match pattern: migrations/####_*.py
            any(part.split('_')[0].isdigit() for part in file_path.split('/') if '_' in part and part.endswith('.py'))
        )

    def _build_comment_body(self, migration_files: list[str]) -> str:
        """Build the GitLab comment body with migration SQL previews."""

        def _raise_parse_error(migration_file: str) -> None:
            raise ValueError(f"Could not parse app name or migration name from: {migration_file}")

        comment_body = "## 📋 Django Migration SQL Preview\n\n"
        comment_body += "This MR introduces new Django migrations. Here's the SQL that will be executed:\n\n"

        for migration_file in migration_files:
            self.stdout.write(f'Processing migration file: {migration_file}')

            try:
                # Extract app name and migration name from file path
                app_name, migration_name = self.parse_migration_file_path(migration_file)

                if not app_name or not migration_name:
                    _raise_parse_error(migration_file)

                self.stdout.write(f'App: {app_name}, Migration: {migration_name}')

                # Generate SQL for this migration
                sql_output = self.get_migration_sql(app_name, migration_name)

                # Add to comment body
                comment_body += f"### 🔧 `{app_name}.{migration_name}`\n\n"
                comment_body += "<details>\n<summary>Click to view SQL</summary>\n\n"
                comment_body += f"```sql\n{sql_output}\n```\n\n</details>\n\n"

            except (ValueError, IndexError) as e:
                self.stdout.write(self.style.WARNING(f'Could not parse migration file path: {migration_file} - {e}'))
                comment_body += f"### ⚠️ `{migration_file}`\n\n"
                comment_body += "Could not generate SQL preview for this migration file.\n\n"

        comment_body += "---\n*This comment was automatically generated by the CI pipeline.*"
        return comment_body

    def parse_migration_file_path(self, migration_file: str) -> tuple[str, str]:
        """
        Parse migration file path to extract app name and migration name.

        Uses multiple strategies to resolve the correct Django app label:
        1. Read apps.py file for AppConfig
        2. Match against registered Django apps
        3. Fallback to directory name

        Args:
            migration_file: Path to migration file (e.g., "myapp/migrations/0001_initial.py")

        Returns:
            Tuple of (app_label, migration_name)

        Raises:
            ValueError: If migration file path doesn't match expected pattern
        """
        # Use regex to match the pattern: directory_name/migrations/migration_file.py
        # This handles both relative paths (app/migrations/file.py) and absolute paths
        pattern = r'(?:.*?/)?([^/]+)/migrations/([^/]+)\.py$'
        match = re.match(pattern, migration_file)

        if not match:
            raise ValueError(f"Migration file path does not match expected pattern: {migration_file}")

        directory_name = match.group(1)
        migration_name = match.group(2)

        # Resolve the actual Django app label
        app_label = self._resolve_app_label(directory_name, migration_file)

        return app_label, migration_name

    def _resolve_app_label(self, directory_name: str, migration_file: str) -> str:
        """
        Resolve the correct Django app label from a directory name.

        Handles cases where directory name != app label by reading apps.py
        and falling back to registry matching.
        """
        # Strategy 1: Try directory name as-is
        if self._is_valid_django_app(directory_name):
            return directory_name

        # Strategy 2: Read apps.py file to get the real app configuration
        app_label_from_config = self._get_app_label_from_apps_py(directory_name, migration_file)
        if app_label_from_config:
            return app_label_from_config

        # Strategy 3: Match against registered Django apps
        return self._match_registered_apps(directory_name)

    def _get_app_label_from_apps_py(self, directory_name: str, migration_file: str) -> str | None:
        """
        Read the apps.py file to extract the actual app name/label from AppConfig.

        This is the most reliable method since it reads the actual Django configuration.
        """
        try:
            # Determine the path to the app directory from the migration file
            migration_path_parts = migration_file.split('/')
            migrations_index = migration_path_parts.index('migrations')
            app_dir_path = Path('/'.join(migration_path_parts[:migrations_index]))

            # Look for apps.py in the app directory
            apps_py_path = app_dir_path / 'apps.py'

            if not apps_py_path.exists():
                self.stdout.write(f'No apps.py found at {apps_py_path}')
                return None

            # Read and parse the apps.py file
            with apps_py_path.open(encoding='utf-8') as f:
                apps_py_content = f.read()

            # Extract app name using regex patterns
            app_label = self._parse_app_config(apps_py_content, directory_name)

            if app_label and self._is_valid_django_app(app_label):
                self.stdout.write(self.style.SUCCESS(f'Found app label "{app_label}" from apps.py'))
                return app_label

        except Exception as e:  # noqa: BLE001
            self.stdout.write(self.style.WARNING(f'Error reading apps.py for directory "{directory_name}": {e}'))
        return None

    def _parse_app_config(self, apps_py_content: str, directory_name: str) -> str | None:
        """
        Parse apps.py content to extract app name/label from AppConfig class.

        Handles various AppConfig patterns:
        - name = 'myapp'
        - name = 'myproject.myapp'
        - label = 'custom_label'
        """
        try:
            # Pattern 1: Look for explicit 'label' attribute (takes precedence)
            label_pattern = r"label\s*=\s*['\"]([^'\"]+)['\"]"
            label_match = re.search(label_pattern, apps_py_content)

            if label_match:
                return label_match.group(1)

            # Pattern 2: Look for 'name' attribute
            name_pattern = r"name\s*=\s*['\"]([^'\"]+)['\"]"
            name_match = re.search(name_pattern, apps_py_content)

            if name_match:
                app_name = name_match.group(1)
                # Django uses the last part of the name as the label by default
                return app_name.split('.')[-1]

            # Pattern 3: Infer from AppConfig class name
            class_pattern = r"class\s+(\w+)\s*\([^)]*AppConfig\s*\)"
            class_match = re.search(class_pattern, apps_py_content)

            if class_match:
                class_name = class_match.group(1)
                if class_name.endswith('Config'):
                    inferred_name = class_name[:-6].lower()  # Remove 'Config' suffix
                    self.stdout.write(
                        self.style.WARNING(f'Inferred app name "{inferred_name}" from AppConfig class "{class_name}"')
                    )
                    return inferred_name

        except Exception as e:  # noqa: BLE001
            self.stdout.write(self.style.WARNING(f'Error parsing apps.py content: {e}'))
        return None

    def _match_registered_apps(self, directory_name: str) -> str:
        """Match directory name against registered Django apps."""
        all_apps = apps.get_app_configs()

        # Find apps where the label ends with the directory name
        matching_apps = [
            app_config
            for app_config in all_apps
            if app_config.label.endswith(directory_name) or directory_name in app_config.name
        ]

        if len(matching_apps) == 1:
            app_label = matching_apps[0].label
            self.stdout.write(self.style.WARNING(f'Directory "{directory_name}" mapped to app "{app_label}"'))
            return app_label
        if len(matching_apps) > 1:
            app_labels = [app.label for app in matching_apps]
            self.stdout.write(
                self.style.WARNING(
                    f'Multiple possible apps found for "{directory_name}": {app_labels}. '
                    f'Using first match: {app_labels[0]}'
                )
            )
            return app_labels[0]

        # Fallback: Use directory name and let Django handle the error
        self.stdout.write(
            self.style.WARNING(
                f'Could not resolve app label for directory "{directory_name}". Using directory name as fallback.'
            )
        )
        return directory_name

    def _is_valid_django_app(self, app_name: str) -> bool:
        """Check if the app name is a valid registered Django app."""
        try:
            apps.get_app_config(app_name)
        except LookupError:
            return False
        else:
            return True

    def get_migration_sql(self, app_name: str, migration_name: str) -> str:
        """Get SQL output for a specific migration."""
        try:
            # Set environment for the sqlmigrate command
            old_env = os.environ.get('ENVIRONMENT')
            os.environ['ENVIRONMENT'] = 'test'

            # Capture the output of sqlmigrate command
            output = StringIO()
            try:
                call_command('sqlmigrate', app_name, migration_name, stdout=output)
                sql_output = output.getvalue()
            finally:
                output.close()
                # Restore original environment
                if old_env is not None:
                    os.environ['ENVIRONMENT'] = old_env
                elif 'ENVIRONMENT' in os.environ:
                    del os.environ['ENVIRONMENT']

            return sql_output.strip() if sql_output.strip() else "No SQL output generated"

        except (CommandError, OSError, ValueError) as e:
            return f"Failed to generate SQL for {app_name}.{migration_name}: {e!s}"

    def post_gitlab_comment(self, api_url: str, project_id: str, mr_iid: str, token: str, comment_body: str) -> None:
        """Post or update GitLab MR comment using httpx."""
        headers = {'PRIVATE-TOKEN': token, 'Content-Type': 'application/json'}

        # Get all notes for this MR
        notes_url = f'{api_url}/projects/{project_id}/merge_requests/{mr_iid}/notes'
        self.stdout.write('Checking for existing migration SQL preview comment...')

        try:
            with httpx.Client() as client:
                # Get existing notes
                response = client.get(notes_url, headers=headers)
                response.raise_for_status()
                notes = response.json()

                # Find existing comment with our signature
                existing_note_id = None
                for note in notes:
                    if 'Django Migration SQL Preview' in note.get('body', ''):
                        existing_note_id = note['id']
                        break

                # Prepare the payload
                payload = {'body': comment_body}

                if existing_note_id:
                    # Update existing comment
                    update_url = f'{notes_url}/{existing_note_id}'
                    self.stdout.write(f'Updating existing comment (ID: {existing_note_id})')
                    response = client.put(update_url, json=payload, headers=headers)
                else:
                    # Create new comment
                    self.stdout.write(f'Creating new comment for MR #{mr_iid}')
                    response = client.post(notes_url, json=payload, headers=headers)

                response.raise_for_status()
                action = "updated" if existing_note_id else "created"
                self.stdout.write(self.style.SUCCESS(f'Successfully {action} GitLab comment'))

        except httpx.HTTPError as e:
            raise CommandError(f'HTTP error posting to GitLab: {e}') from e
        except Exception as e:
            raise CommandError(f'Error posting to GitLab: {e}') from e
