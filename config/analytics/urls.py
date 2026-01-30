from django.urls import path
from .views import DashboardStatsView, ProductAnalyticsView, RevenueAnalysisView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('products/', ProductAnalyticsView.as_view(), name='product-analytics'),
    path('revenue/', RevenueAnalysisView.as_view(), name='revenue-analysis'),
]