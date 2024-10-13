# alexander/management/commands/update_suppliers.py
from django.core.management.base import BaseCommand
from alexander.models import Raw_Materials, Suppliers

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            new_supplier = Suppliers.objects.get(id=14)
            updated_count = Raw_Materials.objects.filter(Supplier=None).update(Supplier=new_supplier)
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} raw materials.'))
        except Suppliers.DoesNotExist:
            self.stdout.write(self.style.ERROR('Supplier with ID 14 does not exist.'))
