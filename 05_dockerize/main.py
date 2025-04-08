from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import model_router
from db import engine
from models import Base
import logging
import os
from datetime import datetime

# 로그 디렉토리 및 파일 설정
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # logs 디렉토리 생성 (이미 존재하면 무시)
log_file = os.path.join(log_dir, f"ml-serving-{datetime.now().strftime('%Y-%m-%d')}.log")

# 로깅 설정
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.FileHandler(log_file, encoding="utf-8"),  # 로그를 파일에 저장
#         logging.StreamHandler()  # 콘솔에도 출력
#     ]
# )


# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우터 포함
app.include_router(model_router.router)

# 애플리케이션 시작 시 로그 메시지
logging.info("info-FastAPI ML Serving application has started.")
logging.debug("debug-FastAPI ML Serving application has started.")
logging.warning("warning-FastAPI ML Serving application has started.")