from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Item

class ItemRepository(ABC):
    @abstractmethod
    async def create(self, item: Item) -> Item: ...

    @abstractmethod
    async def get(self, item_id: str) -> Optional[Item]: ...

    @abstractmethod
    async def list(self) -> List[Item]: ...

    @abstractmethod
    async def update(self, item: Item) -> Item: ...

    @abstractmethod
    async def delete(self, item_id: str) -> bool: ...
