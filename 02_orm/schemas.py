from pydantic import BaseModel

# 요청 데이터 스키마 정의
class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "user"  # 역할 필드 추가 (기본값: user)
