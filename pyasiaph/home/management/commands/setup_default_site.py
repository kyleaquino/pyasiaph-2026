import json
import os
from datetime import date, time

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from pyasiaph.home.models import HomePage
from config.environment import settings, BASE_DIR


class Command(BaseCommand):
    help = "Set up a default Wagtail site"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force creation even if sites already exist",
        )

    def handle(self, *args, **options):
        force = options["force"]

        # Check if sites already exist
        if Site.objects.exists() and not force:
            self.stdout.write(self.style.WARNING("Sites already exist. Use --force to override."))
            return

        try:
            # Handle HomePage creation/overwrite based on force flag
            if force:
                # Clear any existing default sites
                Site.objects.update(is_default_site=False)
                self.stdout.write("Cleared existing default sites.")

                # Delete existing HomePage if force is used
                existing_homepage = HomePage.objects.first()
                if existing_homepage:
                    self.stdout.write(f"Deleting existing HomePage: {existing_homepage.title}")
                    existing_homepage.delete()

                # Create a new HomePage
                self.stdout.write("Creating a new HomePage...")
                home_page = self.create_homepage()
                if not home_page:
                    self.stdout.write(self.style.ERROR("Failed to create HomePage."))
                    return
            else:
                # Find or create the first HomePage (existing behavior)
                home_page = HomePage.objects.first()
                if not home_page:
                    self.stdout.write("No HomePage found. Creating a new HomePage...")
                    home_page = self.create_homepage()
                    if not home_page:
                        self.stdout.write(self.style.ERROR("Failed to create HomePage."))
                        return

            # Create the default site
            site, created = Site.objects.get_or_create(
                hostname=settings.HOSTNAME,
                port=settings.PORT,
                defaults={
                    "root_page": home_page,
                    "is_default_site": True,
                    "site_name": settings.SITE_NAME,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS("Default site created successfully!"))
            else:
                # Update existing site
                site.root_page = home_page
                site.is_default_site = True
                site.site_name = "PyAsiaPH 2026"
                site.save()
                self.stdout.write(self.style.SUCCESS("Default site updated successfully!"))

            self.stdout.write("Site details:")
            self.stdout.write(f"  - Hostname: {site.hostname}")
            self.stdout.write(f"  - Port: {site.port}")
            self.stdout.write(f"  - Root Page: {site.root_page.title}")
            self.stdout.write(f"  - Site Name: {site.site_name}")
            self.stdout.write(f"  - Default Site: {site.is_default_site}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating default site: {e}"))

    def load_homepage_data(self):
        """Load homepage data from JSON file"""
        json_path = os.path.join(BASE_DIR, "data", "homepage_content.json")
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            return data.get("homepage", {})
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f"JSON file not found at {json_path}. Using default values."))
            return {}
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Error parsing JSON file: {e}"))
            return {}

    def create_homepage(self):
        """Create a new HomePage with default values"""
        try:
            # Get or create the root page
            root_page = Page.objects.filter(depth=1).first()
            if not root_page:
                self.stdout.write(self.style.ERROR("No root page found. Please run migrations first."))
                return None

            # Generate a unique slug
            base_slug = "home"
            slug = base_slug
            counter = 1
            while Page.objects.filter(slug=slug, path__startswith=root_page.path).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Load data from JSON file
            homepage_data = self.load_homepage_data()

            # Parse dates and time from JSON
            date_start = date.fromisoformat(homepage_data.get("date_start"))
            date_end = date.fromisoformat(homepage_data.get("date_end"))
            time_start = time.fromisoformat(homepage_data.get("time_start"))

            # Create the HomePage
            home_page = HomePage(
                title=homepage_data.get("title"),
                slug=slug,
                date_start=date_start,
                date_end=date_end,
                time_start=time_start,
                location_main=homepage_data.get("location_main"),
                location_city=homepage_data.get("location_city"),
                keynote_title=homepage_data.get("keynote_title"),
                keynote_subtitle=homepage_data.get("keynote_subtitle"),
                speaker_title=homepage_data.get("speaker_title"),
                speaker_subtitle=homepage_data.get("speaker_subtitle"),
                schedule_title=homepage_data.get("schedule_title"),
                schedule_subtitle=homepage_data.get("schedule_subtitle"),
                sponsor_title=homepage_data.get("sponsor_title"),
                sponsor_subtitle=homepage_data.get("sponsor_subtitle"),
                banner_title=homepage_data.get("banner_title"),
                banner_call_to_action=homepage_data.get("banner_call_to_action"),
                banner_link=homepage_data.get("banner_link"),
            )

            root_page.add_child(instance=home_page)
            home_page.save()

            self.stdout.write(
                self.style.SUCCESS(f"HomePage created successfully: {home_page.title} (slug: {home_page.slug})")
            )
            return home_page

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating HomePage: {e}"))
            return None
