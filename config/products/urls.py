from django.urls import path
from .views import AddItemView, ListItemsView, DeleteItemView, UpdateItemView

urlpatterns = [
    # path("", ProductListView.as_view()),
    path("items/add/", AddItemView.as_view(), name="add-item"),
    path("items/get/", ListItemsView.as_view(), name="list-items"),
    path("items/delete/<int:id>/", DeleteItemView.as_view(), name="delete-item"),
    path("items/update/<int:id>/", UpdateItemView.as_view(), name="update-item"),
]
