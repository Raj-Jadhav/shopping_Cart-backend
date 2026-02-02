from .models import Item
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

class ItemService:
    @staticmethod
    def create_item(name: str, description: str = "", photo=None, price:float=0) -> Item:
        if not name:
            raise ValidationError("Name is required")
        
        try:
            item = Item.objects.create(
                name=name,
                description=description,
                photo=photo,
                price=price
            )
            return item
        except Exception as e:
            print(e)
            raise e
    
    @staticmethod
    def fetch_items(limit: int = 100) -> QuerySet[Item]:
        """
        Fetch items from DB. Optional limit.
        """
        return Item.objects.all()[:limit]
    
    def update(self, request, id):
        try:
            item = Item.objects.get(pk=int(id))
        except Item.DoesNotExist:
            return {
                "message": "Item not found",
                "success": False,
            }

        # Update text fields only if provided
        if "name" in request.data:
            item.name = request.data.get("name")

        if "description" in request.data:
            item.description = request.data.get("description")

        if "price" in request.data:
            item.price = request.data.get("price")

        # Update photo ONLY if a new file was uploaded
        if "photo" in request.FILES:
            item.photo = request.FILES["photo"]

        item.save()

        return {
            "message": f"Updated {id} successfully",
            "success": True,
        }

        
        
    
