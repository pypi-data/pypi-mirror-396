from .scrape_precip import txt_to_csv, read_url_txt, normalized_data
from .scrape_farm import row_by_label, extract_state_rows, scrape_farm_data
from .eda_work import basic_summary, precip_trend_figure, crop_income_fig, precip_v_income, statcompscatt, correl, heatmap
from .analysis import remove_outliers, center_column, corr_and_plot, make_scatter_w_cat
from .merge_csvs import merge_csvs
# import from all .py coding
# all code should be in this folder
# uv pip install -e .
# uv run quarto preview

__all__ = [
    "txt_to_csv", "read_url_txt", "normalized_data",
    "row_by_label", "extract_state_rows", "scrape_farm_data",
    "basic_summary", "precip_trend_figure", "crop_income_fig", "precip_v_income",
    "statcompscatt", "correl", "heatmap",
    "remove_outliers", "center_column", "corr_and_plot", "make_scatter_w_cat",
    "merge_csvs",
]

__version__ = "0.1.2"