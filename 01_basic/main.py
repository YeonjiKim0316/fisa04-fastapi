# from fastapi import FastAPI

# app = FastAPI()

# @app.get('/')
# def read_root():
#     return {'hello':'world'}

# # {변수명}으로 기본 경로 매개변수를 사용합니다.
# # str으로 전달됩니다.
# @app.get('/items/{item_id}') # <변수명>
# def get_item(item_id):
#     return {'item_id': item_id}

# @app.get('/items2/{item_id}') # <변수명>
# def get_item2(item_id: float):  # (변수명: 자료형)
#     return {'item_id': item_id}

from typing import Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/items/")
def create_item(item: Item):
    return {"item": item}

# pagination: skip과 limit이라는 쿼리 매개변수를 사용하여 데이터를 건너뛰고 제한하는 방식으로 동작
#  /items/?skip=2&limit=5로 요청하면, 서버는 데이터를 10개 건너뛰고 그다음 5개를 반환하도록 설계
@app.get("/items/")
def read_items(skip: int = Query(0), limit: int = Query(10)):
    return {"skip": skip, "limit": limit}


## 매개변수 사용
# 1. {변수명}으로 기본적인 경로 매개변수 사용 - 123, 가나다 넣고 확인
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

# ▶ 사용 예시:
# GET /items/123
# → {"item_id": 123}


# 2. 여러 개의 경로 매개변수 사용
@app.get("/users/{user_id}/items/{item_id}")
def read_user_item(user_id: int, item_id: str):
    return {"user_id": user_id, "item_id": item_id}

# ▶ 사용 예시:
# GET /users/42/items/abc123
# → {"user_id": 42, "item_id": "abc123"}


# 3. 경로 매개변수 + 쿼리 매개변수 혼합
@app.get("/products/{product_id}")
def get_product(product_id: int, q: str = None):
    return {"product_id": product_id, "query": q}

# ▶ 사용 예시:
# GET /products/10?q=shoes
# → {"product_id": 10, "query": "shoes"}


# 4. 경로 매개변수에서 값 제한하기 (enum, regex 등 가능)
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    return {"model_name": model_name}

# ▶ 사용 예시:
# GET /models/resnet
# → {"model_name": "resnet"}

# GET /models/unknown
# → 422 Unprocessable Entity (잘못된 값)