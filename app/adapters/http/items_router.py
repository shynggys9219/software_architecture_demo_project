from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from .schemas import ItemIn, ItemOut
from .auth_router import get_current_user

router = APIRouter()

def get_items_service(request: Request):
    return request.app.container.item_service  # type: ignore[attr-defined]

@router.post("/", response_model=ItemOut)
async def create_item(body: ItemIn, user=Depends(get_current_user), svc=Depends(get_items_service)):
    try:
        item = await svc.create_item(body.name, body.description)
        return ItemOut(id=item.id, name=item.name, description=item.description,
                       created_at=item.created_at, updated_at=item.updated_at)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/", response_model=List[ItemOut])
async def list_items(user=Depends(get_current_user), svc=Depends(get_items_service)):
    items = await svc.list_items()
    return [ItemOut(id=i.id, name=i.name, description=i.description,
                    created_at=i.created_at, updated_at=i.updated_at) for i in items]

@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: str, user=Depends(get_current_user), svc=Depends(get_items_service)):
    try:
        i = await svc.get_item(item_id)
        return ItemOut(id=i.id, name=i.name, description=i.description,
                       created_at=i.created_at, updated_at=i.updated_at)
    except KeyError:
        raise HTTPException(404, "not found")

@router.put("/{item_id}", response_model=ItemOut)
async def update_item(item_id: str, body: ItemIn, user=Depends(get_current_user), svc=Depends(get_items_service)):
    try:
        i = await svc.update_item(item_id, body.name, body.description)
        return ItemOut(id=i.id, name=i.name, description=i.description,
                       created_at=i.created_at, updated_at=i.updated_at)
    except KeyError:
        raise HTTPException(404, "not found")
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.delete("/{item_id}")
async def delete_item(item_id: str, user=Depends(get_current_user), svc=Depends(get_items_service)):
    try:
        await svc.delete_item(item_id)
        return {"deleted": True}
    except KeyError:
        raise HTTPException(404, "not found")
