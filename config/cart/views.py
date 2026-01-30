from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer
)
from products.models import Product
import logging

logger = logging.getLogger(__name__)


class CartListView(APIView):
    """
    Retrieve current user's cart with all items.
    GET: Returns user's cart data with items and totals.
    """
    permission_classes = [IsAuthenticated]
    
    def get_or_create_cart(self, user):
        """
        Get or create cart for user.
        Ensures one cart per user with atomic operation.
        """
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created new cart for user {user.username}")
        return cart
    
    def get(self, request):
        """
        Get current user's cart with all items.
        Optimized query with prefetch_related for scaling.
        """
        cart = self.get_or_create_cart(request.user)
        
        # Use optimized query to get cart with items
        cart = Cart.objects.prefetch_related(
            'items',
            'items__product'
        ).get(id=cart.id)
        
        # Convert to dictionary using functional approach
        cart_data = cart.to_dict()
        
        return Response({
            'success': True,
            'data': cart_data
        })


class CartAddItemView(APIView):
    """
    Add item to cart or update quantity if exists.
    POST: Adds product to cart with specified quantity.
    """
    permission_classes = [IsAuthenticated]
    
    def get_or_create_cart(self, user):
        """Get or create cart for user."""
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created new cart for user {user.username}")
        return cart
    
    def post(self, request):
        """
        Add item to cart or update quantity if exists.
        Uses transaction for data integrity.
        """
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        with transaction.atomic():
            cart = self.get_or_create_cart(request.user)
            product = get_object_or_404(Product, id=product_id, is_active=True)
            
            # Check if item already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Update existing item quantity
                new_quantity = cart_item.quantity + quantity
                
                # Validate stock availability
                if not product.can_fulfill_quantity(new_quantity):
                    return Response({
                        'success': False,
                        'error': {
                            'message': f'Insufficient stock. Only {product.stock_quantity} units available.',
                            'code': 'insufficient_stock'
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                cart_item.quantity = new_quantity
                cart_item.save()
                logger.info(f"Updated cart item quantity for {product.name}")
            else:
                logger.info(f"Added {product.name} to cart")
            
            # Refresh cart data
            cart.refresh_from_db()
            cart_data = cart.to_dict()
        
        return Response({
            'success': True,
            'message': f'{product.name} added to cart successfully',
            'data': cart_data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CartUpdateItemView(APIView):
    """
    Update cart item quantity.
    PUT: Updates the quantity of a specific cart item.
    """
    permission_classes = [IsAuthenticated]
    
    def get_or_create_cart(self, user):
        """Get or create cart for user."""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    def put(self, request, item_id):
        """
        Update cart item quantity.
        Validates stock availability before update.
        """
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quantity = serializer.validated_data['quantity']
        
        with transaction.atomic():
            cart = self.get_or_create_cart(request.user)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            # Validate stock
            if not cart_item.product.can_fulfill_quantity(quantity):
                return Response({
                    'success': False,
                    'error': {
                        'message': f'Insufficient stock. Only {cart_item.product.stock_quantity} units available.',
                        'code': 'insufficient_stock'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            cart_item.quantity = quantity
            cart_item.save()
            
            logger.info(f"Updated cart item {cart_item.product.name} quantity to {quantity}")
            
            cart.refresh_from_db()
            cart_data = cart.to_dict()
        
        return Response({
            'success': True,
            'message': 'Cart item updated successfully',
            'data': cart_data
        })


class CartRemoveItemView(APIView):
    """
    Remove item from cart.
    DELETE: Removes a specific item from the cart.
    """
    permission_classes = [IsAuthenticated]
    
    def get_or_create_cart(self, user):
        """Get or create cart for user."""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    def delete(self, request, item_id):
        """
        Remove item from cart.
        Uses atomic transaction for consistency.
        """
        with transaction.atomic():
            cart = self.get_or_create_cart(request.user)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            product_name = cart_item.product.name
            cart_item.delete()
            
            logger.info(f"Removed {product_name} from cart")
            
            cart.refresh_from_db()
            cart_data = cart.to_dict()
        
        return Response({
            'success': True,
            'message': f'{product_name} removed from cart',
            'data': cart_data
        })


class CartClearView(APIView):
    """
    Clear all items from cart.
    DELETE: Removes all items from the user's cart.
    """
    permission_classes = [IsAuthenticated]
    
    def get_or_create_cart(self, user):
        """Get or create cart for user."""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    def delete(self, request):
        """
        Clear all items from cart.
        Useful after successful checkout.
        """
        with transaction.atomic():
            cart = self.get_or_create_cart(request.user)
            items_count = cart.items.count()
            cart.clear()
            
            logger.info(f"Cleared {items_count} items from cart")
        
        return Response({
            'success': True,
            'message': 'Cart cleared successfully',
            'data': {
                'items': [],
                'item_count': 0,
                'total_quantity': 0,
                'total': '0.00',
                'formatted_total': 'UGX 0.00'
            }
        })