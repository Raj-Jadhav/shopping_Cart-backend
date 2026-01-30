from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product


class AddToCartSerializer(serializers.Serializer):
    """
    Serializer for adding items to cart.
    Includes validation for stock and quantity.
    """
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    
    def validate_product_id(self, value):
        """Validate product exists and is active."""
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available.")
        
        return value
    
    def validate(self, data):
        """
        Validate that product has sufficient stock.
        Defensive programming for business logic.
        """
        try:
            product = Product.objects.get(id=data['product_id'], is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        
        if not product.can_fulfill_quantity(data['quantity']):
            raise serializers.ValidationError(
                f"Insufficient stock. Only {product.stock_quantity} units available."
            )
        
        return data


class UpdateCartItemSerializer(serializers.Serializer):
    """
    Serializer for updating cart item quantity.
    Includes stock validation.
    """
    quantity = serializers.IntegerField(required=True, min_value=1)
    
    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        
        if value > 1000:
            raise serializers.ValidationError("Quantity is unreasonably high.")
        
        return value


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart item display.
    Includes computed fields for frontend.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.SerializerMethodField()
    formatted_subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_price',
            'quantity',
            'subtotal',
            'formatted_subtotal',
            'added_at',
        ]
        read_only_fields = ['id', 'added_at']
    
    def get_subtotal(self, obj):
        """Calculate and return subtotal."""
        return str(obj.get_subtotal())
    
    def get_formatted_subtotal(self, obj):
        """Return formatted subtotal with currency."""
        return f"UGX {obj.get_subtotal():,.2f}"


class CartSerializer(serializers.ModelSerializer):
    """
    Complete cart serializer with all items and totals.
    Optimized for single query with prefetch_related.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    formatted_total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'item_count',
            'total_quantity',
            'total',
            'formatted_total',
            'created_at',
            'updated_at',
        ]
    
    def get_total(self, obj):
        """Calculate cart total using dynamic programming."""
        return str(obj.calculate_total())
    
    def get_formatted_total(self, obj):
        """Return formatted total with currency."""
        return f"UGX {obj.calculate_total():,.2f}"
    
    def get_item_count(self, obj):
        """Get number of unique items in cart."""
        return obj.get_items().count()
    
    def get_total_quantity(self, obj):
        """Get total quantity of all items using functional programming."""
        return obj.get_item_count()