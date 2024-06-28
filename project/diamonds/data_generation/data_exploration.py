from pathlib import Path

import matplotlib.pyplot as plt
import plotly.express as px
from loguru import logger
from mdutils.mdutils import MdUtils
from pandas.plotting import scatter_matrix

from diamonds.data_generation.data_loading import DataLoading


class DataExploration:
    def __init__(self, data: DataLoading):
        self.__data_path = data.get_data_path()
        self.__filename = data.get_filename()
        self.__filename_without_extension = data.get_datafile_path().stem
        self.df = data.get_data()

    def check_missing_values(self):
        return self.df.isna().sum()

    def basic_statistics(self):
        return self.df.describe()

    def select_zero_dimensional_items(self):
        return self.df[(self.df["x"] == 0) | (self.df["y"] == 0) | (self.df["z"] == 0)]

    def select_nonpositive_price_items(self):
        return self.df[self.df["price"] <= 0]

    def plot_scatter_matrix(self, scatter_plot_path: Path):
        numerical_features = self.df.select_dtypes(include=["number"])
        scatter_matrix(numerical_features, figsize=(14, 10))
        plt.savefig(scatter_plot_path)
        plt.close()

    def plot_histograms(self, histograms_plot_path: Path):
        self.df.hist(bins=100, figsize=(14, 10))
        plt.savefig(histograms_plot_path)
        plt.close()

    def plot_violin_price_by(self, columns_plot_paths: dict):
        for column, plot_path in columns_plot_paths.items():
            fig = px.violin(self.df, x=column, y="price", color=column, title=f"Price by {column}")
            fig.write_image(plot_path)

    def plot_scatter_price_by(self, columns_plot_paths: dict):
        for column, plot_path in columns_plot_paths.items():
            fig = px.scatter(self.df, x="carat", y="price", color=column, title=f"Price vs carat with {column}")
            fig.write_image(plot_path)

    def generate_report(self):
        """Generate a comprehensive report for the dataset."""
        logger.info("Generating report...")

        report_dir = self.__data_path / f"{self.__filename}_report"
        report_dir.mkdir()

        missing_values = self.check_missing_values()
        basic_stats = self.basic_statistics()
        zero_dimensional_items = self.select_zero_dimensional_items()
        nonpositive_price_items = self.select_nonpositive_price_items()

        scatter_plot_filename = report_dir / f"{self.__filename_without_extension}_scatter_matrix.png"
        self.plot_scatter_matrix(scatter_plot_filename)

        histograms_plot_filename = report_dir / f"{self.__filename_without_extension}_histograms.png"
        self.plot_histograms(histograms_plot_filename)

        object_dtypes = (self.df.dtypes=="object")
        object_cols = list(object_dtypes[object_dtypes].index)
        violin_dict_filenames = {
           col: report_dir / f"{self.__filename_without_extension}_violin_price_{col}.png" for col in object_cols
        }
        self.plot_violin_price_by(violin_dict_filenames)

        scatter_dict_filenames = {
            col: report_dir / f"{self.__filename_without_extension}_scatter_price_{col}.png" for col in object_cols
        }
        self.plot_scatter_price_by(scatter_dict_filenames)

        report_path = report_dir / f"{self.__filename_without_extension}_report.md"
        md_file = MdUtils(file_name=str(report_path))

        md_file.new_header(level=1, title="Data Exploration Report")

        md_file.new_header(level=2, title="Missing Values")
        md_file.new_paragraph(f"{missing_values.to_markdown()}\n")

        md_file.new_header(level=2, title="Basic Statistics")
        md_file.new_paragraph(f"{basic_stats.to_markdown()}\n")

        if not zero_dimensional_items.empty:
            md_file.new_header(level=2, title="Zero Dimensional Items (Data Errors)")
            md_file.new_paragraph(f"{zero_dimensional_items.to_markdown()}\n")

        if not nonpositive_price_items.empty:
            md_file.new_header(level=2, title="Nonpositive Price Items (Data Errors)")
            md_file.new_paragraph(f"{nonpositive_price_items.to_markdown()}\n")

        md_file.new_header(level=2, title="Scatter Matrix Plot")
        md_file.new_line(f"![scatter_matrix]({scatter_plot_filename.name})\n")

        md_file.new_header(level=2, title="Histograms")
        md_file.new_line(f"![histograms]({histograms_plot_filename.name})\n")

        md_file.new_header(level=2, title="Price-by Diamonds Plot")
        for column, plot_filename in violin_dict_filenames.items():
            md_file.new_line(f"![{column}_diamonds_plot]({plot_filename.name})\n")

        md_file.new_header(level=2, title="Price-by Scatter Diamonds Plot")
        for column, plot_filename in scatter_dict_filenames.items():
            md_file.new_line(f"![{column}_violin_plot]({plot_filename.name})\n")

        md_file.create_md_file()
        logger.info(f"Report saved as {report_path}")
