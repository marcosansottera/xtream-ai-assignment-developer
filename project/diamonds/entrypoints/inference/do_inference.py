from pathlib import Path
from typing import Union

import numpy as np

from diamonds.entrypoints.data_generation.do_preprocess_data import (
    BasicDataPreprocess,
    CategoricalDataPreprocess,
)
from diamonds.inference.inference import InferencePipeline
from diamonds.paths import DiamondsDataDir


def run_inference(data_processor: Union[BasicDataPreprocess, CategoricalDataPreprocess], data: np.ndarray, model_path: Path, model_type: str) -> np.ndarray:
    inference_pipeline = InferencePipeline(data_processor, model_path)
    inference_pipeline.load_model()
    predictions = inference_pipeline.predict(data)
    if model_type == "lr":
        predictions = np.exp(predictions)

    return predictions


def setup_data_processor(data_dir: Path, filename: str, preprocess_type: str) -> tuple[Union[BasicDataPreprocess, CategoricalDataPreprocess], np.ndarray, np.ndarray]:
    data_processor_class = {
        "basic": BasicDataPreprocess,
        "categorical": CategoricalDataPreprocess
    }[preprocess_type]

    data_processor = data_processor_class(data_dir / filename)
    data, gt_prices = data_processor.load_dataset()
    return data_processor, data, gt_prices


def main():
    diamonds_clean_data = DiamondsDataDir("clean_data")
    diamonds_models = DiamondsDataDir("models")

    diamonds_filename = "diamonds.csv"
    model_details = [
        ("lr", "basic", "lr_20240627_234107.sav"),
        ("xgb", "categorical", "xgb_tuned_20240627_234216.sav")
    ]
    predictions = {}
    for model_type, preprocess_type, model_timestamp in model_details:
        data_processor, data, gt_prices = setup_data_processor(
            diamonds_clean_data.path, diamonds_filename, preprocess_type)
        model_path = diamonds_models.path / f"{model_type}/{model_timestamp}"
        predictions[model_timestamp] = run_inference(data_processor, data, model_path, model_type)

    for model_timestamp, preds in predictions.items():
        print(f"Predictions with {model_timestamp}: {[int(pred) for pred in preds[0:5]]}")
    print(f"Ground Truth Prices: {gt_prices.to_list()[0:5]}")


if __name__ == "__main__":
    main()
