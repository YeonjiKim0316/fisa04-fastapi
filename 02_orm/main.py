from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from models import User
from schemas import UserCreate

# FastAPI 애플리케이션 생성
app = FastAPI()

# 인증 토큰 검증 함수
def get_current_user(token: str, db: Session = Depends(get_db)):
    """
    인증 토큰을 검증하고 사용자 정보를 반환하는 함수.
    - 실제로는 토큰을 디코딩하거나 데이터베이스에서 사용자 정보를 조회해야 함.
    """
    user = db.query(User).filter(User.name == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# 권한 확인 함수
def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    현재 사용자가 관리자 권한을 가지고 있는지 확인하는 함수.
    - 관리자 권한이 없으면 HTTP 403 에러를 반환.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user

# 사용자 생성 엔드포인트
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    새로운 사용자를 생성하는 엔드포인트.
    - `Depends(get_db)`를 사용하여 데이터베이스 세션을 주입받습니다.
    """
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 새로운 사용자 생성
    new_user = User(name=user.name, email=user.email, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # 새로 추가된 사용자 정보 갱신
    return {"id": new_user.id, "name": new_user.name, "email": new_user.email, "role": new_user.role}

# 사용자 목록 조회 엔드포인트
@app.get("/users/")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    사용자 목록을 조회하는 엔드포인트.
    - `Depends(get_db)`를 사용하여 데이터베이스 세션을 주입받습니다.
    - `skip`과 `limit`을 사용하여 페이징 처리.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# 사용자 프로필 조회 엔드포인트
# http://127.0.0.1:8000/profile?token=alice
@app.get("/profile")
def read_profile(current_user: User = Depends(get_current_user)):
    """
    현재 사용자의 프로필 정보를 반환하는 엔드포인트.
    - 모든 인증된 사용자가 접근 가능.
    """
    return {"id": current_user.id, "name": current_user.name, "email": current_user.email, "role": current_user.role}

# 관리자 전용 엔드포인트
@app.get("/admin")
def read_admin_data(admin_user: User = Depends(get_admin_user)):
    """
    관리자만 접근할 수 있는 엔드포인트.
    - 관리자 권한이 없는 사용자는 HTTP 403 에러를 반환.
    """
    return {"message": f"Welcome, {admin_user.name}! You have admin access."}