from typing import List, Optional
from bson import ObjectId
from ...domain.entities import Item
from ...domain.repositories import ItemRepository
from ...infrastructure.db import Database

class MongoItemRepository(ItemRepository):
    def __init__(self, db: Database):
        self.db = db

    async def _coll(self):
        d = await self.db.db()
        return d.get_collection("items")

    def _map(self, d) -> Item:
        return Item(
            id=str(d["_id"]),
            name=d["name"],
            description=d.get("description"),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
        )

    async def create(self, item: Item) -> Item:
        coll = await self._coll()
        doc = {
            "name": item.name,
            "description": item.description,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
        res = await coll.insert_one(doc)
        item.id = str(res.inserted_id)
        return item

    async def get(self, item_id: str) -> Optional[Item]:
        try:
            oid = ObjectId(item_id)
        except Exception:
            return None
        coll = await self._coll()
        d = await coll.find_one({"_id": oid})
        return self._map(d) if d else None

    async def list(self) -> List[Item]:
        coll = await self._coll()
        items: List[Item] = []
        async for d in coll.find({}).sort("created_at", -1):
            items.append(self._map(d))
        return items

    async def update(self, item: Item) -> Item:
        coll = await self._coll()
        oid = ObjectId(item.id)
        await coll.update_one({"_id": oid}, {"$set": {
            "name": item.name,
            "description": item.description,
            "updated_at": item.updated_at,
        }})
        return item

    async def delete(self, item_id: str) -> bool:
        coll = await self._coll()
        try:
            oid = ObjectId(item_id)
        except Exception:
            return False
        res = await coll.delete_one({"_id": oid})
        return bool(res.deleted_count)
