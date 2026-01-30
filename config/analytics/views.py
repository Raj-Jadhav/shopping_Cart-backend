from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDate
from products.models import Product
from orders.models import Order, OrderItem
from datetime import datetime, timedelta
from functools import reduce
import logging

logger = logging.getLogger(__name__)


class DashboardStatsView(APIView):
    """
    Retrieve comprehensive dashboard statistics.
    GET: Returns summary stats, product performance, and order frequency data.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive dashboard statistics.
        Uses aggregation and functional programming for efficient data processing.
        """
        # Date filter (default: last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Order statistics
        orders = Order.objects.filter(
            status='completed',
            completed_at__gte=start_date
        )
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        avg_order_value = orders.aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0
        
        # Product statistics using functional programming
        product_stats = OrderItem.objects.filter(
            order__in=orders
        ).values(
            'product__id',
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal'),
            order_count=Count('order', distinct=True)
        ).order_by('-total_quantity')
        
        # Most ordered products
        most_ordered = list(product_stats[:10])
        
        # Least ordered products (with at least one order)
        least_ordered = list(product_stats.order_by('total_quantity')[:10])
        
        # Products never ordered
        ordered_product_ids = set(map(lambda x: x['product__id'], product_stats))
        never_ordered = Product.objects.filter(
            is_active=True
        ).exclude(
            id__in=ordered_product_ids
        ).values('id', 'name', 'price', 'stock_quantity')[:10]
        
        # Order frequency by date
        order_frequency = list(
            orders.annotate(
                date=TruncDate('completed_at')
            ).values('date').annotate(
                count=Count('id'),
                revenue=Sum('total_amount')
            ).order_by('date')
        )
        
        # Transform data using functional programming
        frequency_data = list(map(
            lambda item: {
                'date': item['date'].isoformat(),
                'orders': item['count'],
                'revenue': str(item['revenue'])
            },
            order_frequency
        ))
        
        return Response({
            'success': True,
            'data': {
                'summary': {
                    'total_orders': total_orders,
                    'total_revenue': str(total_revenue),
                    'formatted_revenue': f'UGX {total_revenue:,.2f}',
                    'average_order_value': str(avg_order_value),
                    'formatted_avg': f'UGX {avg_order_value:,.2f}',
                    'period_days': days
                },
                'most_ordered_products': most_ordered,
                'least_ordered_products': least_ordered,
                'never_ordered_products': list(never_ordered),
                'order_frequency': frequency_data,
            }
        })


class ProductAnalyticsView(APIView):
    """
    Retrieve detailed analytics for each product.
    GET: Returns product performance data and recommendations.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Detailed analytics for each product.
        Helps determine pricing strategies and discounts.
        """
        products = Product.objects.filter(is_active=True).annotate(
            orders_count=Count('orderitem__order', distinct=True),
            total_sold=Sum('orderitem__quantity'),
            revenue=Sum('orderitem__subtotal')
        ).order_by('-total_sold')
        
        # Categorize products using functional programming
        high_performers = list(filter(
            lambda p: (p.total_sold or 0) > 10,
            products
        ))
        
        low_performers = list(filter(
            lambda p: 0 < (p.total_sold or 0) <= 5,
            products
        ))
        
        no_sales = list(filter(
            lambda p: (p.total_sold or 0) == 0,
            products
        ))
        
        # Transform to dictionaries
        transform_product = lambda p: {
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'formatted_price': f'UGX {p.price:,.2f}',
            'stock_quantity': p.stock_quantity,
            'total_sold': p.total_sold or 0,
            'orders_count': p.orders_count or 0,
            'revenue': str(p.revenue or 0),
            'formatted_revenue': f'UGX {(p.revenue or 0):,.2f}',
            'recommendation': self._get_product_recommendation(p)
        }
        
        return Response({
            'success': True,
            'data': {
                'all_products': [transform_product(p) for p in products],
                'high_performers': [transform_product(p) for p in high_performers],
                'low_performers': [transform_product(p) for p in low_performers],
                'no_sales': [transform_product(p) for p in no_sales],
                'insights': {
                    'high_performers_count': len(high_performers),
                    'low_performers_count': len(low_performers),
                    'no_sales_count': len(no_sales)
                }
            }
        })
    
    @staticmethod
    def _get_product_recommendation(product):
        """
        Get recommendation for product based on performance.
        Helper function using business logic.
        """
        total_sold = product.total_sold or 0
        stock = product.stock_quantity
        
        if total_sold == 0:
            return 'Consider offering discount or promotion'
        elif total_sold > 20:
            if stock < 10:
                return 'High demand! Restock immediately'
            return 'Best seller! Consider increasing price'
        elif total_sold < 5:
            return 'Low sales. Consider discount or bundle deals'
        else:
            return 'Moderate performance. Monitor trends'


class RevenueAnalysisView(APIView):
    """
    Retrieve revenue analysis and trends over time.
    GET: Returns daily revenue data with growth calculations.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Revenue analysis over time with trends.
        Useful for business decision making.
        """
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Daily revenue
        daily_revenue = Order.objects.filter(
            status='completed',
            completed_at__gte=start_date
        ).annotate(
            date=TruncDate('completed_at')
        ).values('date').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id'),
            avg_order=Avg('total_amount')
        ).order_by('date')
        
        # Calculate growth using reduce
        revenue_list = list(daily_revenue)
        
        if len(revenue_list) > 1:
            first_day = float(revenue_list[0]['revenue'])
            last_day = float(revenue_list[-1]['revenue'])
            growth_rate = ((last_day - first_day) / first_day * 100) if first_day > 0 else 0
        else:
            growth_rate = 0
        
        total = reduce(
            lambda acc, item: acc + float(item['revenue']),
            revenue_list,
            0
        )
        
        return Response({
            'success': True,
            'data': {
                'daily_revenue': [
                    {
                        'date': item['date'].isoformat(),
                        'revenue': str(item['revenue']),
                        'formatted_revenue': f"UGX {item['revenue']:,.2f}",
                        'orders': item['orders'],
                        'avg_order': str(item['avg_order']),
                        'formatted_avg': f"UGX {item['avg_order']:,.2f}"
                    }
                    for item in revenue_list
                ],
                'summary': {
                    'total_revenue': str(total),
                    'formatted_total': f'UGX {total:,.2f}',
                    'growth_rate': round(growth_rate, 2),
                    'period_days': days
                }
            }
        })