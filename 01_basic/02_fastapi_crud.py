# 02_fastapi_crud.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 데이터 모델 정의
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    on_offer: bool = False  # swagger에서는 true, false로 bool 타입을 전달합니다.


# 데이터 저장소 (메모리 내 데이터베이스)
# items = []
items = [
    Item(id=1, name="연필", description="Description 1", price=10.0),
    Item(id=2, name="공책", description="Description 2", price=20.0, on_offer=True),
    Item(id=3, name="책갈피", description="Description 3", price=30.0, on_offer=False),
]


# Create: 새로운 아이템 추가
@app.post(
    "/items/",
    response_model=Item,
    summary="Create a new item",
    description="새로운 아이템을 추가합니다. 아이템의 ID는 고유해야 하며, 중복된 ID는 허용되지 않습니다."
)
def create_item(item: Item):
    # ID 중복 확인
    for existing_item in items:
        if existing_item.id == item.id:
            raise HTTPException(status_code=400, detail="Item with this ID already exists")
    items.append(item)
    return item

# Read: 모든 아이템 조회
# @app.get(
#     "/items/",
#     response_model=list[Item],
#     summary="Get all items",
#     description="저장된 모든 아이템을 조회합니다."
# )
# def get_items():
#     return items

@app.get(
    "/items/",
    response_model=list[Item],
    summary="Get all items with pagination",
    description="저장된 모든 아이템을 조회합니다. 페이지네이션을 지원합니다."
)
def read_items(skip: int = Query(0), limit: int = Query(10)):
    """
    아이템 목록 조회 (페이지네이션)
    - skip: 건너뛸 아이템 수 (기본값: 0)
    - limit: 반환할 아이템 수 (기본값: 10)
    """
    return items[skip: skip + limit]


# Read: 특정 아이템 조회
@app.get(
    "/items/{item_id}",
    response_model=Item,
    summary="Get a specific item",
    description="특정 ID를 가진 아이템을 조회합니다. 아이템이 존재하지 않으면 404 에러를 반환합니다."
)
def get_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# Update: 특정 아이템 수정
@app.put(
    "/items/{item_id}",
    response_model=Item,
    summary="Update an item",
    description="특정 ID를 가진 아이템을 수정합니다. 아이템이 존재하지 않으면 404 에러를 반환합니다."
)
def update_item(item_id: int, updated_item: Item):
    for index, item in enumerate(items):
        if item.id == item_id:
            items[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

# Patch: 특정 아이템 부분 수정
@app.patch(
    "/items/{item_id}",
    response_model=Item,
    summary="Partially update an item",
    description="특정 ID를 가진 아이템의 일부 필드를 수정합니다. 아이템이 존재하지 않으면 404 에러를 반환합니다."
)
def patch_item(item_id: int, updated_fields: dict):
    for item in items:
        if item.id == item_id:
            # 업데이트할 필드만 수정
            for key, value in updated_fields.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# Delete: 특정 아이템 삭제
@app.delete(
    "/items/{item_id}",
    summary="Delete an item",
    description="특정 ID를 가진 아이템을 삭제합니다. 아이템이 존재하지 않으면 404 에러를 반환합니다."
)
def delete_item(item_id: int):
    for index, item in enumerate(items):
        if item.id == item_id:
            del items[index]
            return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")