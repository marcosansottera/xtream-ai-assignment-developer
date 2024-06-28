from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from diamonds.data_processing.data_loading import DataLoading


class AbstractDataPreprocess(ABC):
    def __init__(self, datafile_path: Path):
        self._datafile_path = datafile_path
        self._train_path = datafile_path.with_name(f"{datafile_path.stem}{self._suffix}_train{datafile_path.suffix}")
        self._test_path = datafile_path.with_name(f"{datafile_path.stem}{self._suffix}_test{datafile_path.suffix}")

    def split_train_test(self, ratio: float = 0.2, random_state: int = 42):
        data = DataLoading(self._datafile_path)
        df = data.get_data()
        df = self.preprocess(df)
        x = df.drop(columns="price")
        y = df["price"]
        self._x_train, self._x_test, self._y_train, self._y_test = train_test_split(x, y, test_size=ratio, random_state=random_state)

    @abstractmethod
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def save_train_test_to_csv(self):
        train_df = pd.concat([self._x_train, self._y_train], axis=1)
        test_df = pd.concat([self._x_test, self._y_test], axis=1)
        train_df.to_csv(self._train_path, index=False)
        test_df.to_csv(self._test_path, index=False)

    def load_train_test_from_csv(self):
        train_df = pd.read_csv(self._train_path)
        test_df = pd.read_csv(self._test_path)
        train_df = self.postprocess(train_df)
        test_df = self.postprocess(test_df)
        self._x_train = train_df.drop(columns="price")
        self._y_train = train_df["price"]
        self._x_test = test_df.drop(columns="price")
        self._y_test = test_df["price"]

    @abstractmethod
    def postprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def get_train_test(self):
        return self._x_train, self._y_train, self._x_test, self._y_test

class BasicDataPreprocess(AbstractDataPreprocess):
    _suffix = "_basic"

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        object_cols = df.select_dtypes(include="object").columns.values.tolist()
        df = df.drop(columns=["depth", "table", "y", "z"])
        return pd.get_dummies(df, columns=object_cols, drop_first=True)

    def postprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def load_dataset(self):
        df = pd.read_csv(self._datafile_path)
        object_cols = df.select_dtypes(include="object").columns.values.tolist()
        df = df.drop(columns=["depth", "table", "y", "z"])
        df = pd.get_dummies(df, columns=object_cols, drop_first=True)
        return df.drop(columns="price"), df["price"]

class CategoricalDataPreprocess(AbstractDataPreprocess):
    _suffix = "_categorical"
    _category_mapping = {
        "cut": ["Fair", "Good", "Very Good", "Ideal", "Premium"],
        "color": ["D", "E", "F", "G", "H", "I", "J"],
        "clarity": ["IF", "VVS1", "VVS2", "VS1", "VS2", "SI1", "SI2", "I1"]
    }

    def _encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        for col, categories in self._category_mapping.items():
            df[col] = pd.Categorical(df[col], categories=categories, ordered=True)
        return df

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._encode_categorical(df)

    def postprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._encode_categorical(df)

    def split_train_dataset(self, ratio: float = 0.2, random_state: int = 42):
        return train_test_split(self._x_train, self._y_train, test_size=ratio, random_state=random_state)

    def load_dataset(self):
        df = pd.read_csv(self._datafile_path)
        df_features = self._encode_categorical(df.drop(columns="price"))
        df_target = df["price"]
        return df_features, df_target
