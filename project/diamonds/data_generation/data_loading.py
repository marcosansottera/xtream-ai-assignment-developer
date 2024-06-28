from pathlib import Path

import pandas as pd
from loguru import logger


class DataLoading:
    def __init__(self, datafile_path: Path):
        self.__datafile_path = datafile_path
        self.__df = None
        self.load_data()
        self.data_info()

    def load_data(self):
        try:
            if not self.__datafile_path.exists():
                logger.error(f"File does not exist: {self.__datafile_path}")
                return

            if self.__datafile_path.suffix != ".csv":
                logger.error(f"File is not a CSV: {self.__datafile_path}")
                return

            self.__df = pd.read_csv(self.__datafile_path, encoding="utf-8")
            logger.info(f"Data successfully loaded from {self.__datafile_path}")

        except Exception as e:
            logger.error(f"Error loading data from {self.__datafile_path}: {e}")

    def data_info(self):
        self.__df.info()

    def get_data(self):
        if self.__df is not None:
            return self.__df
        else:
            logger.warning("Data is not loaded")
            return None

    def get_data_path(self):
        return self.__datafile_path.parent

    def get_filename(self):
        return self.__datafile_path.name

    def get_datafile_path(self):
        return self.__datafile_path

    def set_datafile_path(self, datafile_path: Path):
        self.__datafile_path = datafile_path
