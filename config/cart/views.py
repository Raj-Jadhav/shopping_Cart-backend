from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Item  # Use your Item model
from .serializers import AddToCartSerializer, UpdateCartItemSerializer
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# -------------------------------
# Helper: Volatile Cart (single instance)
# -------------------------------
def get_or_create_volatile_cart():
    """
    Get or create a single cart for volatile (unauthenticated) use.
    Always uses Cart with id=1, creates if not exists.
    """
    cart, created = Cart.objects.get_or_create(id=1)
    if created:
        logger.info("Created volatile cart (id=1)")
    return cart

# -------------------------------
# Cart Views
# -------------------------------

class CartListView(APIView):
    """List all items in the volatile cart."""
    
    def get(self, request):
        cart = get_or_create_volatile_cart()
        cart_data = cart.to_dict()
        return Response({"success": True, "data": cart_data})


class CartAddItemView(APIView):
    """Add an item to the volatile cart or increase quantity."""

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data['item_id']  # <-- fixed
        quantity = serializer.validated_data['quantity']

        with transaction.atomic():
            cart = get_or_create_volatile_cart()
            item = get_object_or_404(Item, id=item_id)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item=item,  # <-- fixed field name
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            cart.refresh_from_db()
            cart_data = cart.to_dict()

        return Response({
            "success": True,
            "message": f"{item.name} added to cart",
            "data": cart_data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)



class CartUpdateItemView(APIView):
    """Update quantity of an item in the volatile cart."""

    def put(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']

        with transaction.atomic():
            cart = get_or_create_volatile_cart()
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            cart_item.quantity = quantity
            cart_item.save()

            cart.refresh_from_db()
            cart_data = cart.to_dict()

        return Response({
            "success": True,
            "message": "Cart item updated",
            "data": cart_data
        })


class CartRemoveItemView(APIView):
    """Remove an item from the volatile cart."""

    def delete(self, request, item_id):
        with transaction.atomic():
            cart = get_or_create_volatile_cart()
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            item_name = cart_item.product.name
            cart_item.delete()

            cart.refresh_from_db()
            cart_data = cart.to_dict()

        return Response({
            "success": True,
            "message": f"{item_name} removed from cart",
            "data": cart_data
        })


class CartClearView(APIView):
    """Clear all items from the volatile cart."""

    def delete(self, request):
        with transaction.atomic():
            cart = get_or_create_volatile_cart()
            cart.clear()

        return Response({
            "success": True,
            "message": "Cart cleared",
            "data": {
                "items": [],
                "item_count": 0,
                "total_quantity": 0,
                "total": "0.00",
                "formatted_total": "UGX 0.00"
            }
        })
