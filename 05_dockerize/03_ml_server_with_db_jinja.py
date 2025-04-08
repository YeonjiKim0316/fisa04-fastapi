from fastapi import FastAPI, HTTPException, Depends, Form # Form: jinja와 Form으로 값을 입력받을 때 
from pydantic import BaseModel
import joblib
import numpy as np
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import logging
from models import Base, IrisPrediction  # ORM 모델 가져오기
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # 추가


# 로깅 설정
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# 환경 변수 로드
load_dotenv()

# 머신러닝 모델 로드
model = joblib.load("iris_model.joblib")

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
# 데이터베이스 연결 설정
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테이블 생성
Base.metadata.create_all(bind=engine)

# 입력 데이터 스키마 정의
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
