from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor

from diamonds.entrypoints.data_generation.do_preprocess_data import (
    BasicDataPreprocess,
    CategoricalDataPreprocess,
)
from diamonds.paths import DiamondsDataDir
from diamonds.training.models_pipeline import (
    create_model_pipeline,
    tune_xgboost_model,
)


def train_models():
    diamonds_clean_data = DiamondsDataDir("clean_data")
    diamonds_filename = "diamonds.csv"

    model_configs = [
        {
            "data_processor": BasicDataPreprocess(diamonds_clean_data.path / diamonds_filename),
            "model": LinearRegression(),
            "model_name": "lr",
            "model_dir": DiamondsDataDir("models/lr").path
        },
        {
            "data_processor": CategoricalDataPreprocess(diamonds_clean_data.path / diamonds_filename),
            "model": XGBRegressor(enable_categorical=True, random_state=42),
            "model_name": "xgb",
            "model_dir": DiamondsDataDir("models/xgb").path
        }
    ]

    for config in model_configs:
        model_pipeline = create_model_pipeline(
            data_processor=config["data_processor"],
            model=config["model"],
            model_name=config["model_name"],
            model_dir=config["model_dir"]
        )
        model_pipeline.train_model()
        model_pipeline.evaluate_model()
        model_pipeline.save_model()
        model_pipeline.plot_gof()

    best_params = tune_xgboost_model(diamonds_clean_data, diamonds_filename)

    final_pipeline = create_model_pipeline(
        data_processor=CategoricalDataPreprocess(diamonds_clean_data.path / diamonds_filename),
        model=XGBRegressor(**best_params, enable_categorical=True, random_state=42),
        model_name="xgb_tuned",
        model_dir=DiamondsDataDir("models/xgb").path
    )
    final_pipeline.train_model()
    final_pipeline.evaluate_model()
    final_pipeline.save_model()
    final_pipeline.plot_gof()


if __name__ == "__main__":
    train_models()
