from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Item:
    id: Optional[str] = None
    name: str = ""
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def rename(self, new_name: str, new_desc: Optional[str] = None):
        if not new_name or len(new_name) > 200:
            raise ValueError("invalid name")
        self.name = new_name
        self.description = new_desc
        self.updated_at = datetime.utcnow()
