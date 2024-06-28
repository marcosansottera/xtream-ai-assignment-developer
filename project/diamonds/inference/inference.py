from pathlib import Path
from typing import Union

import joblib

from diamonds.entrypoints.data_processing.do_preprocess_data import (
    BasicDataPreprocess,
    CategoricalDataPreprocess,
)


class InferencePipeline:
    def __init__(self, data_processor: Union[BasicDataPreprocess, CategoricalDataPreprocess], model_path: Path):
        self.data_processor = data_processor
        self.model_path = model_path
        self.pipeline = None

    def load_model(self):
        self.pipeline = joblib.load(self.model_path)

    def prepare_data(self, data):
        processed_data = self.data_processor.postprocess(data)
        return processed_data

    def predict(self, data):
        prepared_data = self.prepare_data(data)
        predictions = self.pipeline.predict(prepared_data)
        return predictions
