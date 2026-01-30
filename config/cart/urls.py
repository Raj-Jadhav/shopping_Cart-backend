from django.urls import path
from .views import (
    CartListView,
    CartAddItemView,
    CartUpdateItemView,
    CartRemoveItemView,
    CartClearView
)

urlpatterns = [
    path('', CartListView.as_view(), name='cart-list'),
    path('add-item/', CartAddItemView.as_view(), name='cart-add-item'),
    path('update-item/<int:item_id>/', CartUpdateItemView.as_view(), name='cart-update-item'),
    path('remove-item/<int:item_id>/', CartRemoveItemView.as_view(), name='cart-remove-item'),
    path('clear/', CartClearView.as_view(), name='cart-clear'),
]