from pathlib import Path

from loguru import logger

from diamonds.data_processing.data_cleaning import DataCleaning
from diamonds.data_processing.data_exploration import DataExploration
from diamonds.paths import DiamondsDataDir


def clean_data(raw_datapath: Path, clean_datapath: Path, filename: str):
    logger.info("Cleaning data...")
    data = DataCleaning(raw_datapath/filename, clean_datapath)
    data.save_data()

    logger.info("Exploring clean data...")
    data_explorer = DataExploration(data.get_data())
    data_explorer.generate_report()

if __name__ == "__main__":
    diamonds_raw_data = DiamondsDataDir("raw_data")
    diamonds_clean_data = DiamondsDataDir("clean_data")
    diamonds_filename = "diamonds.csv"
    clean_data(diamonds_raw_data.path, diamonds_clean_data.path, diamonds_filename)
