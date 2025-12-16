import json
import os
import tempfile
import zipfile
from collections import defaultdict
from urllib.request import urlretrieve
from django.core.management.base import BaseCommand
from django.db import transaction
from cmShoppingList.models import MarketType, ItemEquivalence


class Command(BaseCommand):
    help = 'Populate Market Types and Item Equivalences from ESI static data export'

    def handle(self, *args, **kwargs):
        # Step 1: Get the latest build number
        self.stdout.write('Fetching latest build number from ESI...')
        latest_url = 'https://developers.eveonline.com/static-data/tranquility/latest.jsonl'

        with tempfile.TemporaryDirectory() as temp_dir:
            latest_file = os.path.join(temp_dir, 'latest.jsonl')
            urlretrieve(latest_url, latest_file)

            with open(latest_file, 'r', encoding='utf-8') as f:
                latest_data = json.loads(f.readline())
                build_number = latest_data['buildNumber']

            self.stdout.write(f'Latest build number: {build_number}')

            # Step 2: Download the static data ZIP
            zip_url = f'https://developers.eveonline.com/static-data/tranquility/eve-online-static-data-{build_number}-jsonl.zip'
            self.stdout.write(f'Downloading static data from {zip_url}...')

            zip_path = os.path.join(temp_dir, 'static-data.zip')
            urlretrieve(zip_url, zip_path)

            self.stdout.write('Extracting ZIP file...')
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Step 3: Load the JSONL files
            type_dogma_path = os.path.join(temp_dir, 'typeDogma.jsonl')
            types_path = os.path.join(temp_dir, 'types.jsonl')

            if not os.path.exists(type_dogma_path) or not os.path.exists(types_path):
                self.stdout.write(self.style.ERROR(
                    'Required JSONL files not found in extracted data.'
                ))
                return
            
            self.stdout.write('Loading types.jsonl...')
            types = {}
            type_count = 0
            with open(types_path, 'r', encoding='utf-8') as f:
                for line in f:
                    item = json.loads(line)

                    if 'marketGroupID' in item and item.get('published', False):
                        type_id = item['_key']
                        name = item.get('name').get('en')
                        types[item['_key']] = item

                        marketype, created = MarketType.objects.update_or_create(
                            id=type_id,
                            defaults = {
                                'name': name
                            }
                        )

                        if created:
                            type_count += 1                       

            self.stdout.write('Loading typeDogma.jsonl...')
            type_dogma = {}
            with open(type_dogma_path, 'r', encoding='utf-8') as f:
                for line in f:
                    item = json.loads(line)
                    type_dogma[item['_key']] = item

            self.stdout.write('Finding equivalents...')

            # Group items by their dogma attributes and variationParentTypeID
            dogma_groups = defaultdict(list)
            for type_id, dogma in type_dogma.items():
                if 'dogmaAttributes' in dogma:
                    # Create a hashable key from dogma attributes and variationParentTypeID
                    attrs = tuple(sorted((d['attributeID'], d['value']) for d in dogma['dogmaAttributes']))
                    variation_parent = types.get(type_id, {}).get('variationParentTypeID', None)
                    if not variation_parent:
                        continue
                    key = (attrs, variation_parent)
                    dogma_groups[key].append(type_id)

            # Collect equivalent items (only groups with 2+ items)
            equivalent_groups = []
            for group in dogma_groups.values():
                if len(group) > 1:
                    # Filter to only published items with marketGroupID (likely modules/items)
                    filtered = [tid for tid in group if tid in types]
                    if len(filtered) > 1:
                        equivalent_groups.append(filtered)

            self.stdout.write(f'Found {len(equivalent_groups)} equivalence groups')

            # Get all valid MarketType IDs
            self.stdout.write('Loading MarketType IDs from database...')
            valid_market_type_ids = set(MarketType.objects.values_list('id', flat=True))

            self.stdout.write('Populating ItemEquivalence table...')

            # Clear existing equivalences
            ItemEquivalence.objects.all().delete()

            created_count = 0
            skipped_groups = 0

            with transaction.atomic():
                for group in equivalent_groups:
                    # Filter to only items that exist in MarketType
                    valid_item_ids = [item_id for item_id in group if item_id in valid_market_type_ids]

                    # Only create mappings if we have at least 2 valid items
                    if len(valid_item_ids) >= 2:
                        # Create bidirectional mappings
                        # Each item can be substituted by any other item in the group
                        for original_id in valid_item_ids:
                            for equivalent_id in valid_item_ids:
                                if original_id != equivalent_id:
                                    ItemEquivalence.objects.create(
                                        original_item_id=original_id,
                                        equivalent_item_id=equivalent_id
                                    )
                                    created_count += 1
                    else:
                        skipped_groups += 1

            self.stdout.write(self.style.SUCCESS(
                f'Successfully created {type_count} market types. '
                f'Successfully created {created_count} equivalence mappings. '
                f'Skipped {skipped_groups} groups with insufficient items in MarketType.'
            ))
