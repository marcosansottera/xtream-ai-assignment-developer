import json
from datetime import datetime
from pathlib import Path
from typing import Union

import joblib
import matplotlib.pyplot as plt
import numpy as np
import optuna
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from diamonds.entrypoints.data_processing.do_preprocess_data import (
    BasicDataPreprocess,
    CategoricalDataPreprocess,
)
from diamonds.paths import DiamondsDataDir


class ModelPipeline:
    def __init__(self, data_processor: Union[BasicDataPreprocess,CategoricalDataPreprocess], model, model_name: str, model_path: Path):
        self.data_processor = data_processor
        self.model_name = model_name
        self.model_path = model_path
        self.pipeline = Pipeline([
            (model_name, model)
        ])
        self.metrics = {}
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None
        self.y_pred = None

    def load_data(self) -> None:
        self.data_processor.load_train_test_from_csv()
        self.x_train, self.y_train, self.x_test, self.y_test = self.data_processor.get_train_test()

    def split_train_dataset(self):
        return self.data_processor.split_train_dataset()

    def train_model(self):
        if self.model_name == "lr":
            self.pipeline.fit(self.x_train, np.log(self.y_train))
            self.y_pred = np.exp(self.pipeline.predict(self.x_test))
        else:
            self.pipeline.fit(self.x_train, self.y_train)
            self.y_pred = self.pipeline.predict(self.x_test)

    def tune_model(self, x_train, x_val, y_train):
        self.pipeline.fit(x_train, y_train)
        return self.pipeline.predict(x_val)

    def evaluate_model(self):
        r2 = r2_score(self.y_test, self.y_pred)
        mae = mean_absolute_error(self.y_test, self.y_pred)
        self.metrics = {"r2_score": r2, "mae": mae}

    def save_model(self):
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{self.model_name}_{datetime_str}.sav"
        metrics_filename = model_filename.replace(".sav", ".json")
        joblib.dump(self.pipeline, self.model_path / model_filename)
        with (self.model_path / metrics_filename).open("w") as f:
            json.dump(self.metrics, f)

    def plot_gof(self):
        plt.plot(self.y_test, self.y_pred, ".")
        plt.plot(self.y_test, self.y_test, linewidth=3, c="black")
        plt.xlabel("Actual")
        plt.ylabel("Predicted")
        plt.show()

def create_model_pipeline(data_processor, model, model_name, model_dir):
    pipeline = ModelPipeline(
        data_processor=data_processor,
        model=model,
        model_name=model_name,
        model_path=model_dir
    )
    pipeline.load_data()
    return pipeline

def tune_xgboost_model(diamonds_clean_data, diamonds_filename):
    def objective(trial: optuna.trial.Trial) -> float:
        param = {
            "lambda": trial.suggest_float("lambda", 1e-8, 1.0, log=True),
            "alpha": trial.suggest_float("alpha", 1e-8, 1.0, log=True),
            "colsample_bytree": trial.suggest_categorical("colsample_bytree", [0.3, 0.4, 0.5, 0.7]),
            "subsample": trial.suggest_categorical("subsample", [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]),
            "learning_rate": trial.suggest_float("learning_rate", 1e-8, 1.0, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 9),
            "random_state": 42,
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "enable_categorical": True
        }
        model_pipeline = create_model_pipeline(
            data_processor=CategoricalDataPreprocess(diamonds_clean_data.path / diamonds_filename),
            model=XGBRegressor(**param),
            model_name="xgb_tuned",
            model_dir=DiamondsDataDir("models/xgb").path
        )
        x_train, x_val, y_train, y_val = model_pipeline.split_train_dataset()
        y_pred = model_pipeline.tune_model(x_train, x_val, y_train)
        return mean_absolute_error(y_val, y_pred)

    study = optuna.create_study(direction="minimize", study_name="Diamonds XGBoost")
    study.optimize(objective, n_trials=100)
    print("Best hyperparameters: ", study.best_params)
    return study.best_params
