
import json
import os
from django.core.management.base import BaseCommand
from alexander.models import Suppliers 

class Command(BaseCommand):
    help = 'Load suppliers from a JSON file into the database'

    def handle(self, *args, **kwargs):
        # Absolute path to the JSON file
        json_file_path = 'C:\\Users\\assaf\\myproject\\mysite\\data.json'

        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_file_path}'))
            return

        with open(json_file_path, 'r', encoding='utf-16') as file:
            data = json.load(file)

            for item in data:
                model = item['model']
                if model == 'alexander.Suppliers':
                    pk = item['pk']
                    fields = item['fields']
                    name = fields.get('Name', '')
                    email = fields.get('Email', '')
                    phone = fields.get('phone', '')

                    # Use get_or_create to avoid duplicate entries
                    Suppliers.objects.update_or_create(
                        pk=pk,
                        defaults={'Name': name, 'Email': email, 'phone': phone}
                    )

        self.stdout.write(self.style.SUCCESS('Successfully loaded suppliers'))
