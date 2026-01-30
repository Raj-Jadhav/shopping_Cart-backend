from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from products.models import Product
from decimal import Decimal
from functools import reduce


class Order(models.Model):
    """
    Order model representing a completed purchase.
    Includes payment and change calculation logic.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Payment details
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    change_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'user']),
            models.Index(fields=['status', '-created_at']),
        ]
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - UGX {self.total_amount:,.2f}"
    
    def calculate_change(self):
        """
        Calculate change to return to customer.
        Uses Decimal for precise currency calculation.
        """
        if self.amount_paid >= self.total_amount:
            return self.amount_paid - self.total_amount
        return Decimal('0.00')
    
    def can_complete(self):
        """
        Check if order can be completed.
        Validates payment is sufficient.
        """
        return self.amount_paid >= self.total_amount
    
    def complete(self):
        """
        Mark order as completed.
        Calculates and stores change amount.
        """
        if not self.can_complete():
            raise ValueError("Insufficient payment to complete order")
        
        self.status = 'completed'
        self.change_amount = self.calculate_change()
        from django.utils import timezone
        self.completed_at = timezone.now()
        self.save()
    
    def get_total_items(self):
        """Get total number of items using functional programming."""
        return sum(map(lambda item: item.quantity, self.items.all()))
    
    def to_dict(self):
        """
        Convert order to dictionary.
        Includes all payment calculations.
        """
        items = self.items.select_related('product').all()
        
        return {
            'id': self.id,
            'status': self.status,
            'items': [item.to_dict() for item in items],
            'total_amount': str(self.total_amount),
            'formatted_total': f"UGX {self.total_amount:,.2f}",
            'amount_paid': str(self.amount_paid),
            'formatted_paid': f"UGX {self.amount_paid:,.2f}",
            'change_amount': str(self.change_amount),
            'formatted_change': f"UGX {self.change_amount:,.2f}",
            'can_complete': self.can_complete(),
            'total_items': self.get_total_items(),
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class OrderItem(models.Model):
    """
    Individual item in an order.
    Stores snapshot of product at time of purchase.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    # Snapshot of product details at time of order
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} - Order #{self.order.id}"
    
    def calculate_subtotal(self):
        """Calculate subtotal for this item."""
        return self.product_price * Decimal(str(self.quantity))
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate subtotal.
        Ensures data consistency.
        """
        self.subtotal = self.calculate_subtotal()
        super().save(*args, **kwargs)
    
    def to_dict(self):
        """Convert order item to dictionary."""
        return {
            'id': self.id,
            'product_id': self.product.id,
            'product_name': self.product_name,
            'product_price': str(self.product_price),
            'formatted_price': f"UGX {self.product_price:,.2f}",
            'quantity': self.quantity,
            'subtotal': str(self.subtotal),
            'formatted_subtotal': f"UGX {self.subtotal:,.2f}",
        }