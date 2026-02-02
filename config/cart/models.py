from django.db import models
from decimal import Decimal
from functools import reduce
from products.models import Item

class Cart(models.Model):
    """
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.created_at}"

    def get_items(self):
        return self.items.select_related('item').all()

    def calculate_total(self):
        items = self.get_items()
        total = reduce(lambda acc, item: acc + item.get_subtotal(), items, Decimal('0.00'))
        return total

    def get_item_count(self):
        items = self.get_items()
        return sum(item.quantity for item in items)

    def clear(self):
        self.items.all().delete()

    def to_dict(self):
        items_data = [item.to_dict() for item in self.get_items()]
        return {
            'id': self.id,
            'items': items_data,
            'item_count': len(items_data),
            'total_quantity': sum(i['quantity'] for i in items_data),
            'subtotal': str(self.calculate_total()),
            'total': str(self.calculate_total()),
            'formatted_total': f"UGX {self.calculate_total():,.2f}",
        }


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)  # <- must match name
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'item')  # <- ok
        ordering = ['-added_at']


    def __str__(self):
        return f"{self.quantity}x {self.item.name} in Cart"

    def get_subtotal(self):
        return Decimal(self.item.price) * self.quantity

    def to_dict(self):
        return {
            'id': self.id,
            'item': {
                'id': self.item.id,
                'name': self.item.name,
                'price': str(self.item.price),
                'formatted_price': f"UGX {self.item.price:,.2f}",
                'photo': self.item.photo.url if self.item.photo else None,
            },
            'quantity': self.quantity,
            'subtotal': str(self.get_subtotal()),
            'formatted_subtotal': f"UGX {self.get_subtotal():,.2f}",
        }
