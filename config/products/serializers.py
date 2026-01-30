from rest_framework import serializers
from .models import Product
from decimal import Decimal


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    Includes custom validation and computed fields.
    """
    in_stock = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock_quantity',
            'image_url',
            'is_active',
            'in_stock',
            'formatted_price',
            'total_ordered',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_ordered']
    
    def get_in_stock(self, obj):
        """Check if product is in stock."""
        return obj.is_in_stock()
    
    def get_formatted_price(self, obj):
        """Format price with UGX currency."""
        return f"UGX {obj.price:,.2f}"
    
    def validate_price(self, value):
        """
        Validate price is positive and reasonable.
        Defensive programming for data integrity.
        """
        if value <= Decimal('0'):
            raise serializers.ValidationError("Price must be greater than zero.")
        
        if value > Decimal('1000000000'):  # 1 billion UGX max
            raise serializers.ValidationError("Price is unreasonably high.")
        
        return value
    
    def validate_stock_quantity(self, value):
        """Validate stock quantity."""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product lists.
    Optimized for performance with minimal fields.
    """
    in_stock = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'formatted_price',
            'image_url',
            'in_stock',
        ]
    
    def get_in_stock(self, obj):
        return obj.is_in_stock()
    
    def get_formatted_price(self, obj):
        return f"UGX {obj.price:,.2f}"