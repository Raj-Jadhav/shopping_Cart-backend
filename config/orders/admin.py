from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'quantity', 'subtotal']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'status',
        'total_amount',
        'amount_paid',
        'change_amount',
        'created_at',
        'completed_at'
    ]
    list_filter = ['status', 'created_at', 'completed_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = [
        'total_amount',
        'amount_paid',
        'change_amount',
        'created_at',
        'updated_at',
        'completed_at'
    ]
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status')
        }),
        ('Payment Details', {
            'fields': ('total_amount', 'amount_paid', 'change_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order',
        'product_name',
        'product_price',
        'quantity',
        'subtotal'
    ]
    list_filter = ['created_at']
    search_fields = ['product_name', 'order__user__username']
    readonly_fields = ['subtotal', 'created_at']