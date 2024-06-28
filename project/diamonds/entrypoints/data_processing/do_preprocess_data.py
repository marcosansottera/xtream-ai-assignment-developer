import argparse

from diamonds.data_processing.data_preprocess import (
    BasicDataPreprocess,
    CategoricalDataPreprocess,
)
from diamonds.paths import DiamondsDataDir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess diamonds data.")
    parser.add_argument("--type", choices=["basic", "categorical"], help="Type of preprocessing to perform")
    args = parser.parse_args()

    diamonds_clean_data = DiamondsDataDir("clean_data")
    diamonds_filename = "diamonds.csv"

    if args.type == "basic":
        preprocess = BasicDataPreprocess(diamonds_clean_data.path / diamonds_filename)
    elif args.type == "categorical":
        preprocess = CategoricalDataPreprocess(diamonds_clean_data.path / diamonds_filename)
    else:
        raise ValueError("Unsupported --type argument. Choose 'basic' or 'categorical'.")

    preprocess.split_train_test()
    preprocess.save_train_test_to_csv()
