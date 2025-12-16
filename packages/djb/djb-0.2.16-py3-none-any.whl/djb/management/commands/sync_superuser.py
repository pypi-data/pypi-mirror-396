"""Sync Django superuser from encrypted secrets."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from djb.secrets import load_secrets


class Command(BaseCommand):
    help = "Create or update superuser from encrypted secrets"

    def add_arguments(self, parser):
        parser.add_argument(
            "--environment",
            "-e",
            type=str,
            default=None,
            help="Environment to load secrets from (default: auto-detect from DYNO/ENVIRONMENT)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def handle(self, *args, **options):
        import os
        from pathlib import Path

        from django.conf import settings

        User = get_user_model()

        dry_run = options["dry_run"]

        # Try environment variables first (for Heroku where age key isn't available)
        username = os.environ.get("SUPERUSER_USERNAME")
        email = os.environ.get("SUPERUSER_EMAIL")
        password = os.environ.get("SUPERUSER_PASSWORD")

        if all([username, email, password]):
            self.stdout.write("Loading superuser credentials from environment variables")
        else:
            # Fall back to encrypted secrets
            environment = options["environment"]
            if environment is None:
                if "DYNO" in os.environ:
                    environment = "heroku_prod"
                else:
                    environment = os.environ.get("ENVIRONMENT", "dev")

            self.stdout.write(f"Loading secrets for environment: {environment}")

            try:
                secrets = load_secrets(
                    environment=environment,
                    secrets_dir=Path(settings.BASE_DIR) / "secrets",
                )
            except Exception as e:
                raise CommandError(f"Failed to load secrets: {e}")

            # Get superuser credentials
            superuser_config = secrets.get("superuser")
            if not superuser_config:
                raise CommandError(
                    f"No 'superuser' configuration found in {environment} secrets. "
                    "Add a superuser section with username, email, and password."
                )

            username = superuser_config.get("username")
            email = superuser_config.get("email")
            password = superuser_config.get("password")

        if not all([username, email, password]):
            raise CommandError(
                "Superuser config must include 'username', 'email', and 'password'"
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"[DRY RUN] Would sync superuser: {username} ({email})")
            )
            return

        # Check if user exists
        try:
            user = User.objects.get(username=username)
            # Update existing user
            user.email = email
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"Updated superuser: {username} ({email})")
            )
        except User.DoesNotExist:
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Created superuser: {username} ({email})")
            )
