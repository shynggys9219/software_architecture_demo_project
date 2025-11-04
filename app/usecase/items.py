from typing import List, Optional
from ..domain.entities import Item
from ..domain.repositories import ItemRepository

class ItemService:
    def __init__(self, repo: ItemRepository):
        self.repo = repo

    async def create_item(self, name: str, description: Optional[str]) -> Item:
        item = Item(name=name, description=description)
        if not item.name:
            raise ValueError("name required")
        return await self.repo.create(item)

    async def list_items(self) -> List[Item]:
        return await self.repo.list()

    async def get_item(self, item_id: str) -> Item:
        item = await self.repo.get(item_id)
        if not item:
            raise KeyError("not found")
        return item

    async def update_item(self, item_id: str, name: str, description: Optional[str]) -> Item:
        item = await self.get_item(item_id)
        item.rename(name, description)
        return await self.repo.update(item)

    async def delete_item(self, item_id: str) -> bool:
        ok = await self.repo.delete(item_id)
        if not ok:
            raise KeyError("not found")
        return ok
