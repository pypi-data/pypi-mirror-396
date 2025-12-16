import io
import json
import tarfile
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Download Carbon Design System assets (icons or pictograms) from npm.\n\n"
        "Setup:\n"
        "  1. Add to settings.py:\n"
        '     CARBON_ICONS_PATH = BASE_DIR / "carbon" / "icons"\n'
        '     CARBON_PICTOGRAMS_PATH = BASE_DIR / "carbon" / "pictograms"\n'
        "  2. Run: python manage.py fetch_carbon_assets icons\n"
        "       or: python manage.py fetch_carbon_assets pictograms\n"
        "       or: python manage.py fetch_carbon_assets all\n"
        "  3. Assets will be downloaded to the specified paths"
    )

    # Asset type configuration
    ASSET_TYPES = {
        "icons": {
            "package": "@carbon/icons",
            "setting": "CARBON_ICONS_PATH",
            "display_name": "Icons",
        },
        "pictograms": {
            "package": "@carbon/pictograms",
            "setting": "CARBON_PICTOGRAMS_PATH",
            "display_name": "Pictograms",
        },
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "asset_type",
            type=str,
            choices=["icons", "pictograms", "all"],
            help="Type of Carbon assets to download (icons, pictograms, or all)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force download even if directory exists and is not empty",
        )

    def handle(self, *args, **options):
        asset_type = options["asset_type"]

        if asset_type == "all":
            # Download both icons and pictograms
            for asset in ["icons", "pictograms"]:
                self.stdout.write(self.style.NOTICE(f"\n=== Processing {asset} ==="))
                self._fetch_asset(asset, options)
        else:
            self._fetch_asset(asset_type, options)

    def _fetch_asset(self, asset_type: str, options: dict):
        """Fetch a specific asset type (icons or pictograms)."""
        config = self.ASSET_TYPES[asset_type]
        package_name = config["package"]
        setting_name = config["setting"]
        display_name = config["display_name"]

        # Get the path from settings
        try:
            asset_path = getattr(settings, setting_name)
        except AttributeError:
            raise CommandError(
                f"{setting_name} is not set in Django settings.\n"
                f"Add to your settings.py:\n"
                f'  {setting_name} = BASE_DIR / "carbon" / "{asset_type}"'
            ) from None

        output_path = Path(asset_path)

        # Check if a directory exists and has content
        if output_path.exists() and any(output_path.iterdir()):
            if not options["force"]:
                self.stdout.write(
                    self.style.WARNING(
                        f"Directory {output_path} already exists and is not empty. "
                        "Use --force to overwrite."
                    )
                )
                return
            else:
                self.stdout.write(
                    self.style.WARNING(f"Overwriting existing {asset_type} in {output_path}")
                )

        # Create a directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Get the latest version info from npm registry
        registry_url = f"https://registry.npmjs.org/{package_name}/latest"

        self.stdout.write(f"Fetching latest Carbon {display_name} version...")

        try:
            # Safe: Only accessing npmjs.org registry with https
            with urllib.request.urlopen(registry_url) as response:  # nosec B310
                data = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            raise CommandError(f"Failed to fetch package info: {e}") from e

        # Get the tarball URL and version
        tarball_url = data["dist"]["tarball"]
        version = data["version"]

        self.stdout.write(f"Downloading Carbon {display_name} v{version}...")
        self.stdout.write(f"From: {tarball_url}")

        # Download the tarball
        try:
            # Safe: URL comes from npmjs.org registry response (https)
            with urllib.request.urlopen(tarball_url) as response:  # nosec B310
                tarball_data = response.read()
        except Exception as e:
            raise CommandError(f"Failed to download tarball: {e}") from e

        # Extract only the svg directory
        self.stdout.write("Extracting SVG files...")

        try:
            with tarfile.open(fileobj=io.BytesIO(tarball_data), mode="r:gz") as tar:
                # Filter for only svg files
                svg_members = [
                    member for member in tar.getmembers() if member.name.startswith("package/svg/")
                ]

                for member in svg_members:
                    # Strip the 'package/svg/' prefix
                    member.name = member.name.replace("package/svg/", "", 1)
                    tar.extract(member, path=output_path)
        except Exception as e:
            raise CommandError(f"Failed to extract files: {e}") from e

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully downloaded {len(svg_members)} Carbon {display_name} "
                f"(v{version}) to {output_path}"
            )
        )
