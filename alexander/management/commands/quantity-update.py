# alexander/management/commands/update_suppliers.py
from django.core.management.base import BaseCommand
from alexander.models import Raw_Materials, Suppliers

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
           
           for product in Raw_Materials.objects.all():
                update_count=0
                product.Quantity = product.Lower_Barrier+2
                product.save()
                update_count+=1
           self.stdout.write(self.style.SUCCESS(f'Successfully updated {update_count} raw materials.'))
        except Suppliers.DoesNotExist:
            self.stdout.write(self.style.ERROR('Supplier with ID 14 does not exist.'))
