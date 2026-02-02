from django.db import models
# from django.core.validators import MinValueValidator
# from decimal import Decimal


# class Product(models.Model):
#     """
#     Product model representing items available for purchase.
#     Optimized with indexes for fast queries at scale.
#     """
#     name = models.CharField(max_length=200, db_index=True)
#     description = models.TextField()
#     price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal('0.01'))],
#         help_text="Price in Ugandan Shillings (UGX)"
#     )
#     stock_quantity = models.PositiveIntegerField(
#         default=0,
#         validators=[MinValueValidator(0)]
#     )
#     image_url = models.URLField(max_length=500, blank=True, null=True)
#     is_active = models.BooleanField(default=True, db_index=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     # Analytics fields
#     total_ordered = models.PositiveIntegerField(default=0)
    
#     class Meta:
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['name', 'is_active']),
#             models.Index(fields=['-created_at']),
#             models.Index(fields=['-total_ordered']),
#         ]
#         verbose_name = 'Product'
#         verbose_name_plural = 'Products'
    
#     def __str__(self):
#         return f"{self.name} - UGX {self.price:,.2f}"
    
#     def is_in_stock(self):
#         """Check if product is available in stock."""
#         return self.stock_quantity > 0
    
#     def can_fulfill_quantity(self, quantity):
#         """
#         Check if requested quantity can be fulfilled.
#         Uses defensive programming for validation.
#         """
#         if not isinstance(quantity, int) or quantity <= 0:
#             return False
#         return self.stock_quantity >= quantity
    
#     def reduce_stock(self, quantity):
#         """
#         Reduce stock by specified quantity.
#         Implements validation and atomic update.
#         """
#         if not self.can_fulfill_quantity(quantity):
#             raise ValueError(f"Insufficient stock. Available: {self.stock_quantity}, Requested: {quantity}")
        
#         self.stock_quantity -= quantity
#         self.total_ordered += quantity
#         self.save(update_fields=['stock_quantity', 'total_ordered', 'updated_at'])
    
#     def restore_stock(self, quantity):
#         """Restore stock when order is cancelled."""
#         self.stock_quantity += quantity
#         self.total_ordered = max(0, self.total_ordered - quantity)
#         self.save(update_fields=['stock_quantity', 'total_ordered', 'updated_at'])

# api/models.py
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.IntegerField(default=0)
    photo = models.ImageField(upload_to="item_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name