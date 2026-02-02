# from rest_framework.generics import ListAPIView
# from rest_framework.permissions import AllowAny
# from .models import Product
# from .serializers import ProductSerializer

# class ProductListView(ListAPIView):
#     queryset = Product.objects.all()[:3]  # Only 3 items
#     serializer_class = ProductSerializer
#     permission_classes = [AllowAny]
# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .services import ItemService
from django.conf import settings
from .models import Item
import logging

logger = logging.getLogger(__name__)

_itemService = ItemService()
class AddItemView(APIView):
    """
    Create a new item with photo upload.
    POST: Accepts multipart/form-data or JSON to create an item.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Add an Item.
        Accepts multipart/form-data or JSON.
        """
        try:
            # Multipart/form-data (for file upload)
            name = request.data.get("name")
            description = request.data.get("description", "")
            photo = request.FILES.get("photo")  # None if not uploaded
            price = request.data.get('price')

            item = ItemService.create_item(name=name, description=description, photo=photo, price=price)

            return Response(
                {"id": item.id, "message": "Item created successfully"},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error creating item: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListItemsView(APIView):
    """
    Retrieve all items with optional photo URL.
    GET: Returns a list of all items.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Fetch items.
        """
        try:
            items = ItemService.fetch_items()
            # Convert to simple dicts for JSON response
            data = [
                {
                    "id": i.id,
                    "name": i.name,
                    "description": i.description,
                    'photo': f"{settings.BACKEND_URL}{i.photo.url}" if i.photo else None,
                    'price': i.price
                }
                for i in items
            ]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching items: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeleteItemView(APIView):
    """
    Delete a specific item by ID.
    DELETE: Removes an item from the database.
    """
    permission_classes = [AllowAny]
    
    def delete(self, request, id):
        """
        Delete an item.
        """
        try:
            item = Item.objects.get(id=id)
            item.delete()
            return Response({"success": True},
                status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UpdateItemView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, id):
        update = _itemService.update(request, id)
        if update['success'] == False:
            return Response({
                "message": "an error occured"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "message": "successful"
            }, status=status.HTTP_200_OK)
