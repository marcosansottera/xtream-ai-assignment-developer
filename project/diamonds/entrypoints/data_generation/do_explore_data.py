from pathlib import Path

from loguru import logger

from diamonds.data_generation.data_exploration import DataExploration
from diamonds.data_generation.data_loading import DataLoading
from diamonds.paths import DiamondsDataDir


def explore_data(raw_filepath: Path, filename: str):
    logger.info("Loading raw data...")
    data = DataLoading(raw_filepath/filename)

    logger.info("Exploring raw data...")
    data_explorer = DataExploration(data)
    data_explorer.generate_report()

if __name__ == "__main__":
    diamonds_raw_data = DiamondsDataDir("raw_data")
    diamonds_filename = "diamonds.csv"
    explore_data(diamonds_raw_data.path, diamonds_filename)
