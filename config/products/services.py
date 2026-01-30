from .models import Item
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

class ItemService:
    @staticmethod
    def create_item(name: str, description: str = "", photo=None) -> Item:
        if not name:
            raise ValidationError("Name is required")
        
        try:
            item = Item.objects.create(
                name=name,
                description=description,
                photo=photo
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
