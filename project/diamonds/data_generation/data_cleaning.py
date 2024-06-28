from pathlib import Path

from loguru import logger

from diamonds.data_generation.data_loading import DataLoading


class DataCleaning:
    def __init__(self, datafile_path: Path, clean_data_path: Path):
        self.__data = DataLoading(datafile_path)
        self.__clean_data_path = clean_data_path
        self.clean_data()
        self.__data.set_datafile_path(clean_data_path/self.__data.get_filename())

    def remove_zero_dimensional_items(self):
        try:
            df = self.__data.get_data()
            if df is None:
                logger.error("Data not loaded. Cannot remove zero dimensional items.")
                return

            original_count = len(df)
            self.__df = df[(df["x"] != 0) & (df["y"] != 0) & (df["z"] != 0)]
            removed_count = original_count - len(self.__df)
            logger.info(f"Zero dimensional items removed: {removed_count} items.")

        except Exception as e:
            logger.error(f"Error removing zero dimensional items: {e}")

    def remove_nonpositive_price_items(self):
        try:
            df = self.__df if self.__df is not None else self.__data.get_data()
            if df is None:
                logger.error("Data not loaded. Cannot remove nonpositive price items.")
                return

            original_count = len(df)
            self.__df = df[df["price"] > 0]
            removed_count = original_count - len(self.__df)
            logger.info(f"Nonpositive price items removed: {removed_count} items.")

        except Exception as e:
            logger.error(f"Error removing nonpositive price items: {e}")


    def clean_data(self):
        self.remove_zero_dimensional_items()
        self.remove_nonpositive_price_items()
        if self.__df is not None and self.__df.empty:
            logger.warning("Resulting DataFrame is empty after cleaning.")

    def save_data(self):
        try:
            if self.__df is None or self.__df.empty:
                logger.error("No data to save. Clean the data first.")
                return

            filename = self.__data.get_filename()
            clean_path = self.__clean_data_path / filename
            print(self.__clean_data_path)
            self.__df.to_csv(clean_path, index=False, encoding="utf-8")
            logger.info(f"Cleaned data saved to {clean_path}")

        except Exception as e:
            logger.error(f"Error saving cleaned data: {e}")

    def get_data(self):
        return self.__data
