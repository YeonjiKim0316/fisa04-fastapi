from fastapi import HTTPException, Depends, Form # Form: jinja와 Form으로 값을 입력받을 때 
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
import numpy as np
import logging
import joblib
from db import get_db 
from models import IrisPrediction

# 머신러닝 모델 로드
model = joblib.load("iris_model.joblib")

router = APIRouter()
# directory안에 저장된 html 파일에 진자 템플릿을 적용 
# 기본값이 directory="templates" 입니다.
templates = Jinja2Templates(directory="templates", auto_reload=True)


@router.get("/")
def read_form(request: Request):
    return templates.TemplateResponse("input_form.html", {"request":request})


# 예측 및 데이터베이스 저장 엔드포인트 정의
@router.post("/predict")
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
    
