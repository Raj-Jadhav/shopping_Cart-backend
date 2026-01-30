from django.contrib import admin
from .models import Item
# from .models import Product

# Register your models here.
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = [
#         'name',
#         'price',
#         'stock_quantity',
#         'total_ordered',
#         'is_active',
#         'created_at'
#     ]
#     list_filter = ['is_active', 'created_at']
#     search_fields = ['name', 'description']
#     list_editable = ['price', 'stock_quantity', 'is_active']
#     readonly_fields = ['total_ordered', 'created_at', 'updated_at']
    
#     fieldsets = (
#         ('Product Information', {
#             'fields': ('name', 'description', 'image_url')
#         }),
#         ('Pricing & Stock', {
#             'fields': ('price', 'stock_quantity', 'is_active')
#         }),
#         ('Analytics', {
#             'fields': ('total_ordered',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at')
#         }),
#     )

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name']