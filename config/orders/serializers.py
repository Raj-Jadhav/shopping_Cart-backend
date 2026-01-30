from rest_framework import serializers
from .models import Order, OrderItem
from decimal import Decimal


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer for checkout process.
    Validates payment amount against cart total.
    """
    amount_paid = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        required=True
    )
    
    def validate_amount_paid(self, value):
        """
        Validate payment amount is positive.
        Defensive programming for payment validation.
        """
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "Payment amount must be greater than zero."
            )
        
        if value > Decimal('100000000'):  # 100 million UGX max
            raise serializers.ValidationError(
                "Payment amount is unreasonably high."
            )
        
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    formatted_price = serializers.SerializerMethodField()
    formatted_subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_price',
            'formatted_price',
            'quantity',
            'subtotal',
            'formatted_subtotal',
        ]
    
    def get_formatted_price(self, obj):
        return f"UGX {obj.product_price:,.2f}"
    
    def get_formatted_subtotal(self, obj):
        return f"UGX {obj.subtotal:,.2f}"


class OrderSerializer(serializers.ModelSerializer):
    """
    Complete order serializer.
    Includes all items and payment calculations.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    formatted_total = serializers.SerializerMethodField()
    formatted_paid = serializers.SerializerMethodField()
    formatted_change = serializers.SerializerMethodField()
    can_complete = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'items',
            'total_amount',
            'formatted_total',
            'amount_paid',
            'formatted_paid',
            'change_amount',
            'formatted_change',
            'can_complete',
            'total_items',
            'created_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'change_amount',
            'created_at',
            'completed_at',
        ]
    
    def get_formatted_total(self, obj):
        return f"UGX {obj.total_amount:,.2f}"
    
    def get_formatted_paid(self, obj):
        return f"UGX {obj.amount_paid:,.2f}"
    
    def get_formatted_change(self, obj):
        return f"UGX {obj.change_amount:,.2f}"
    
    def get_can_complete(self, obj):
        return obj.can_complete()
    
    def get_total_items(self, obj):
        return obj.get_total_items()


class OrderListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for order lists.
    Optimized for performance.
    """
    formatted_total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'total_amount',
            'formatted_total',
            'item_count',
            'created_at',
            'completed_at',
        ]
    
    def get_formatted_total(self, obj):
        return f"UGX {obj.total_amount:,.2f}"
    
    def get_item_count(self, obj):
        return obj.items.count()