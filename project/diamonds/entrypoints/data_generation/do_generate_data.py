from diamonds.data_generation.data_generation import save_split_csv
from diamonds.paths import DiamondsDataDir

if __name__ == "__main__":
    diamonds_raw_data_new = DiamondsDataDir("raw_data_new")
    diamonds_filename = "diamonds.csv"
    save_split_csv(diamonds_raw_data_new, diamonds_filename)
