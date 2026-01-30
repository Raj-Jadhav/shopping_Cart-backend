from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from products.models import Product
from decimal import Decimal
from functools import reduce


class Cart(models.Model):
    """
    Shopping cart model for each user.
    One cart per user with session management.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def get_items(self):
        """
        Get all cart items using optimized query.
        Prefetch related products for efficiency.
        """
        return self.items.select_related('product').filter(product__is_active=True)
    
    def calculate_total(self):
        """
        Calculate cart total using functional programming with reduce.
        Dynamic programming approach for O(n) complexity.
        """
        items = self.get_items()
        
        # Using reduce (functional programming) to calculate total
        total = reduce(
            lambda acc, item: acc + item.get_subtotal(),
            items,
            Decimal('0.00')
        )
        
        return total
    
    def get_item_count(self):
        """
        Get total number of items using lambda and sum.
        Functional programming approach.
        """
        items = self.get_items()
        return sum(map(lambda item: item.quantity, items))
    
    def clear(self):
        """Clear all items from cart."""
        self.items.all().delete()
    
    def to_dict(self):
        """
        Convert cart to dictionary with all calculations.
        Optimized with single query for all items.
        """
        items = self.get_items()
        
        # Use list comprehension for efficiency
        items_data = [item.to_dict() for item in items]
        
        return {
            'id': self.id,
            'user': self.user.username,
            'items': items_data,
            'item_count': len(items_data),
            'total_quantity': sum(map(lambda i: i['quantity'], items_data)),
            'subtotal': str(self.calculate_total()),
            'total': str(self.calculate_total()),
            'formatted_total': f"UGX {self.calculate_total():,.2f}",
        }


class CartItem(models.Model):
    """
    Individual item in shopping cart.
    Includes quantity and automatic subtotal calculation.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart.user.username}'s cart"
    
    def get_subtotal(self):
        """
        Calculate subtotal for this item.
        Uses Decimal for precise currency calculations.
        """
        return self.product.price * Decimal(str(self.quantity))
    
    def to_dict(self):
        """
        Convert cart item to dictionary.
        Includes all necessary information for frontend.
        """
        return {
            'id': self.id,
            'product': {
                'id': self.product.id,
                'name': self.product.name,
                'price': str(self.product.price),
                'formatted_price': f"UGX {self.product.price:,.2f}",
                'image_url': self.product.image_url,
                'stock_quantity': self.product.stock_quantity,
            },
            'quantity': self.quantity,
            'subtotal': str(self.get_subtotal()),
            'formatted_subtotal': f"UGX {self.get_subtotal():,.2f}",
        }