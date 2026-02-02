from rest_framework import serializers
from .models import Cart, CartItem, Item


class AddToCartSerializer(serializers.Serializer):
    """
    Serializer for adding items to cart.
    """
    item_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)

    def validate_item_id(self, value):
        """Ensure item exists."""
        if not Item.objects.filter(id=value).exists():
            raise serializers.ValidationError("Item not found.")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """
    Serializer for updating cart item quantity.
    """
    quantity = serializers.IntegerField(required=True, min_value=1)

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual cart items.
    """
    item_name = serializers.CharField(source='product.name', read_only=True)  # Keep 'product' field in CartItem
    item_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.SerializerMethodField()
    formatted_subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',        # refers to Item in your CartItem model
            'item_name',
            'item_price',
            'quantity',
            'subtotal',
            'formatted_subtotal',
            'added_at',
        ]
        read_only_fields = ['id', 'added_at']

    def get_subtotal(self, obj):
        return str(obj.get_subtotal())

    def get_formatted_subtotal(self, obj):
        return f"UGX {obj.get_subtotal():,.2f}"


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the whole cart.
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
        return str(obj.calculate_total())

    def get_formatted_total(self, obj):
        return f"UGX {obj.calculate_total():,.2f}"

    def get_item_count(self, obj):
        return obj.get_items().count()

    def get_total_quantity(self, obj):
        return obj.get_item_count()
