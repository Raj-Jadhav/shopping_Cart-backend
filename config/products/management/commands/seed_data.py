from django.core.management.base import BaseCommand
from products.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed database with initial products'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding products...')
        
        products = [
            {
                'name': 'Rolex Watch',
                'description': 'Luxury Swiss-made timepiece with automatic movement and sapphire crystal. Water-resistant up to 100m.',
                'price': Decimal('15000000.00'),  # 15 million UGX
                'stock_quantity': 5,
                'image_url': 'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=400'
            },
            {
                'name': 'MacBook Pro 16"',
                'description': 'Apple M3 Max chip, 36GB RAM, 1TB SSD. Perfect for developers and creative professionals.',
                'price': Decimal('8500000.00'),  # 8.5 million UGX
                'stock_quantity': 10,
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400'
            },
            {
                'name': 'iPhone 15 Pro Max',
                'description': 'Latest flagship smartphone with A17 Pro chip, titanium design, and advanced camera system. 256GB storage.',
                'price': Decimal('4800000.00'),  # 4.8 million UGX
                'stock_quantity': 15,
                'image_url': 'https://images.unsplash.com/photo-1592286927505-fdc995c3c995?w=400'
            },
        ]
        
        created_count = 0
        for product_data in products:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {product.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Already exists: {product.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Seeding complete! Created {created_count} new products.'
            )
        )