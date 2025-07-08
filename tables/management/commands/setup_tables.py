from django.core.management.base import BaseCommand
from tables.models import Table

class Command(BaseCommand):
    help = 'Setup default tables with icons'

    def handle(self, *args, **options):
        # Create sample tables if they don't exist
        for i in range(1, 11):  # Create 10 tables
            table, created = Table.objects.get_or_create(
                table_number=i,
                defaults={
                    'capacity': 4,
                    'is_available': True,
                    'icon': 'table_icons/table_with_chairs.png'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created table {i}')
                )
            else:
                # Update existing table to have the new icon
                table.icon = 'table_icons/table_with_chairs.png'
                table.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated table {i} with new icon')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up tables with icons')
        )