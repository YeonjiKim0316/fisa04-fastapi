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

# directory안에 저장된 html 파일에 진자 템플릿을 적용 
# 기본값이 directory="templates" 입니다.
templates = Jinja2Templates(directory="templates", auto_reload=True)


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

# 데이터베이스 세션 종속성 정의
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_form(request: Request):
    return templates.TemplateResponse("input_form.html", {"request":request})


# 예측 및 데이터베이스 저장 엔드포인트 정의
@app.post("/predict")
def predict(
    request: Request,
    sepal_length: float = Form(...),
    sepal_width: float = Form(...),
    petal_length: float = Form(...),
    petal_width: float = Form(...),
    db: Session = Depends(get_db)
):
    """
    입력 데이터를 기반으로 머신러닝 모델을 사용하여 예측을 수행하고,
    결과를 데이터베이스에 저장한 후 결과 페이지를 반환합니다.
    """
    try:
        # 입력 데이터를 NumPy 배열로 변환
        features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
        # 머신러닝 모델을 사용하여 예측 수행
        prediction = model.predict(features)
        pred = int(prediction[0])  # 예측 결과를 정수로 변환

        # 데이터베이스에 예측 결과 저장
        new_prediction = IrisPrediction(
            sepal_length=sepal_length,
            sepal_width=sepal_width,
            petal_length=petal_length,
            petal_width=petal_width,
            prediction=pred
        )
        db.add(new_prediction)  # 새 데이터 추가
        db.commit()  # 트랜잭션 커밋
        db.refresh(new_prediction)  # 새로 추가된 데이터 갱신

        # 예측 결과 페이지 반환
        return templates.TemplateResponse("result.html", {
            "request": request,
            "sepal_length": sepal_length,
            "sepal_width": sepal_width,
            "petal_length": petal_length,
            "petal_width": petal_width,
            "prediction": pred
        })
    except Exception as e:
        # 예외 발생 시 에러 메시지 출력 및 HTTP 500 에러 반환
        logging.error(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
# # 예측 및 데이터베이스 저장 엔드포인트 정의
# @app.post("/predict")
# def predict(request: Request, data: IrisInput, db: Session = Depends(get_db)):
#     """
#     입력 데이터를 기반으로 머신러닝 모델을 사용하여 예측을 수행하고,
#     결과를 데이터베이스에 저장한 후 반환합니다.
#     """
#     try:
#         # 입력 데이터를 NumPy 배열로 변환
#         features = np.array([[data.sepal_length, data.sepal_width,
#                               data.petal_length, data.petal_width]])
#         # 머신러닝 모델을 사용하여 예측 수행
#         prediction = model.predict(features)
#         pred = int(prediction[0])  # 예측 결과를 정수로 변환

#         # 데이터베이스에 예측 결과 저장
#         new_prediction = IrisPrediction(
#             sepal_length=data.sepal_length,
#             sepal_width=data.sepal_width,
#             petal_length=data.petal_length,
#             petal_width=data.petal_width,
#             prediction=pred
#         )
#         db.add(new_prediction)  # 새 데이터 추가
#         db.commit()  # 트랜잭션 커밋
#         db.refresh(new_prediction)  # 새로 추가된 데이터 갱신

#         # 예측 결과 반환
#         return templates.TemplateResponse("result.html", {"request":request, "prediction": pred})
#     except Exception as e:
#         # 예외 발생 시 에러 메시지 출력 및 HTTP 500 에러 반환
#         logging.error(f"Error during prediction: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")