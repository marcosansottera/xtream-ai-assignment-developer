from datetime import datetime, timezone
from typing import List

import joblib
import pandas as pd
import sqlite_utils
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from diamonds.entrypoints.data_processing.do_preprocess_data import (
    BasicDataPreprocess,
    CategoricalDataPreprocess,
)
from diamonds.paths import DiamondsDataDir

app = FastAPI()

class DiamondFeatures(BaseModel):
    carat: float
    cut: str
    color: str
    clarity: str
    depth: float
    table: float
    x: float
    y: float
    z: float

class PredictionResponse(BaseModel):
    predicted_value: int

class SimilarSamplesRequest(BaseModel):
    carat: float
    cut: str
    color: str
    clarity: str
    n: int

class SimilarSamplesResponse(BaseModel):
    samples: List[dict]

diamonds_clean_data = DiamondsDataDir("clean_data")
diamonds_filename = "diamonds.csv"

data_processor_categorical = CategoricalDataPreprocess(diamonds_clean_data.path / diamonds_filename)
data_categorical, gt_prices_categorical = data_processor_categorical.load_dataset()

data_processor_basic = BasicDataPreprocess(diamonds_clean_data.path / diamonds_filename)
data_basic, gt_prices_basic = data_processor_basic.load_dataset()

diamonds_models = DiamondsDataDir("models")
model_path_lr = diamonds_models.lr.path / "lr_20240628_114528.sav"
model_path_xgb = diamonds_models.xgb.path / "xgb_tuned_20240628_114612.sav"

model_lr = joblib.load(model_path_lr)
model_xgb = joblib.load(model_path_xgb)

def get_db_connection():
    return sqlite_utils.Database("logs.db")

def log_request_response(endpoint, request_data, response_data):
    db = get_db_connection()
    db["logs"].insert({
        "endpoint": endpoint,
        "request_data": request_data,
        "response_data": response_data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.post("/predict", response_model=PredictionResponse)
def predict(diamond: DiamondFeatures):
    input_data = pd.DataFrame([diamond.model_dump()])
    processed_data = data_processor_categorical.postprocess(input_data)
    prediction = model_xgb.predict(processed_data)
    predicted_value = int(prediction[0])
    response = {"predicted_value": predicted_value}

    log_request_response("/predict", diamond.model_dump(), response)

    return response

@app.post("/similar_samples", response_model=SimilarSamplesResponse)
def similar_samples(request: SimilarSamplesRequest):
    filtered_data = data_categorical[
        (data_categorical["cut"] == request.cut) &
        (data_categorical["color"] == request.color) &
        (data_categorical["clarity"] == request.clarity)
    ]

    if filtered_data.empty:
        raise HTTPException(status_code=404, detail="No samples found with the specified criteria.")

    filtered_data["weight_diff"] = (filtered_data["carat"] - request.carat).abs()
    similar_samples = filtered_data.nsmallest(request.n, "weight_diff").drop(columns="weight_diff")
    response = {"samples": similar_samples.to_dict(orient="records")}

    log_request_response("/similar_samples", request.dict(), response)

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
