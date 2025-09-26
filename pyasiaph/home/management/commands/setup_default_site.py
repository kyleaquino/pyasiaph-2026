from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time
from wagtail.models import Site, Page
from pyasiaph.home.models import HomePage


class Command(BaseCommand):
    help = 'Set up a default Wagtail site'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if sites already exist',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Check if sites already exist
        if Site.objects.exists() and not force:
            self.stdout.write(
                self.style.WARNING('Sites already exist. Use --force to override.')
            )
            return

        try:
            # Find or create the first HomePage
            home_page = HomePage.objects.first()
            if not home_page:
                self.stdout.write('No HomePage found. Creating a new HomePage...')
                home_page = self.create_homepage()
                if not home_page:
                    self.stdout.write(
                        self.style.ERROR('Failed to create HomePage.')
                    )
                    return

            # Clear any existing default sites if force is used
            if force:
                Site.objects.update(is_default_site=False)
                self.stdout.write('Cleared existing default sites.')

            # Create the default site
            site, created = Site.objects.get_or_create(
                hostname='localhost',
                port=8000,
                defaults={
                    'root_page': home_page,
                    'is_default_site': True,
                    'site_name': 'PyAsiaPH 2026'
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS('Default site created successfully!')
                )
            else:
                # Update existing site
                site.root_page = home_page
                site.is_default_site = True
                site.site_name = 'PyAsiaPH 2026'
                site.save()
                self.stdout.write(
                    self.style.SUCCESS('Default site updated successfully!')
                )

            self.stdout.write(f'Site details:')
            self.stdout.write(f'  - Hostname: {site.hostname}')
            self.stdout.write(f'  - Port: {site.port}')
            self.stdout.write(f'  - Root Page: {site.root_page.title}')
            self.stdout.write(f'  - Site Name: {site.site_name}')
            self.stdout.write(f'  - Default Site: {site.is_default_site}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating default site: {e}')
            )

    def create_homepage(self):
        """Create a new HomePage with default values"""
        try:
            # Get or create the root page
            root_page = Page.objects.filter(depth=1).first()
            if not root_page:
                self.stdout.write(
                    self.style.ERROR('No root page found. Please run migrations first.')
                )
                return None

            # Generate a unique slug
            base_slug = 'home'
            slug = base_slug
            counter = 1
            while Page.objects.filter(slug=slug, path__startswith=root_page.path).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Create the HomePage
            home_page = HomePage(
                title='PyAsiaPH 2026',
                slug=slug,
                date_start=date(2026, 1, 1),  # Default date - should be updated
                date_end=date(2026, 1, 2),    # Default date - should be updated
                time_start=time(9, 0),        # 9:00 AM
                location_main='TBD',
                location_city='TBD',
                keynote_title='Keynote Speakers',
                keynote_subtitle='Meet our amazing keynote speakers',
                speaker_title='Speakers',
                speaker_subtitle='Learn from industry experts',
                schedule_title='Schedule',
                schedule_subtitle='Conference program',
                sponsor_title='Sponsors',
                sponsor_subtitle='Our amazing sponsors',
                banner_title='Welcome to PyAsiaPH 2026',
                banner_call_to_action='Get Tickets',
                banner_link='https://example.com/tickets'
            )
            
            root_page.add_child(instance=home_page)
            home_page.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'HomePage created successfully: {home_page.title} (slug: {home_page.slug})')
            )
            return home_page
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating HomePage: {e}')
            )
            return None
