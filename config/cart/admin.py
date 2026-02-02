from django.contrib import admin
from .models import Cart, CartItem


# Inline for CartItem
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at', 'updated_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    # Since there's no user yet, show session_key
    list_display = ['id', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'cart',
        'item',  # changed from 'product' to 'item'
        'quantity',
        'added_at',
        'updated_at'
    ]
    list_filter = ['added_at', 'updated_at']
    readonly_fields = ['added_at', 'updated_at']
