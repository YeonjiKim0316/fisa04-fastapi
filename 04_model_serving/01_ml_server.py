from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# 모델 로드
model = joblib.load("iris_model.joblib")

# FastAPI 인스턴스
app = FastAPI()

# 입력 데이터 구조 정의
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.post("/predict")
def predict(data: IrisInput):
    features = np.array([[data.sepal_length, data.sepal_width,
                          data.petal_length, data.petal_width]])
    prediction = model.predict(features)
    return {"prediction": int(prediction[0])}

# {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}