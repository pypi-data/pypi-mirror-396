import pandas as pd
import matplotlib.pyplot as plt

def basic_summary(df):
    print(df.head())
    print(df.describe())
    print(df.isna().sum())

group_by = "year"
titles = ["Year", "Mean Normalized Precipitation", "Average Precipitation Across the U.S. Over Time"]
def precip_trend_figure(df, group_by,titles):
    mean_precip_by_year = df.groupby(group_by)["yearly_avg"].mean()
    plt.figure(figsize=(12,6))
    plt.plot(mean_precip_by_year)
    plt.xlabel(titles[0])
    plt.ylabel(titles[1])
    plt.title(titles[2])
    plt.tight_layout()
    plt.savefig("precip_over_time.png", dpi=300)
    plt.close()

group_by2 = "year"
titles2 = ["Year", "Mean Crop Cash Receipts", "Crop Income Trends Over Time"]
def crop_income_fig(df, group_by2, titles2):
    mean_income_by_year = df.groupby(group_by2)["Crop cash receipts"].mean()
    plt.figure(figsize=(12,6))
    plt.plot(mean_income_by_year)
    plt.xlabel(titles2[0])
    plt.ylabel(titles2[1])
    plt.title(titles2[2])
    plt.tight_layout()
    plt.savefig("crop_income_over_time.png", dpi=300)
    plt.close()

title3 = ["Normalized Precipitation", "Crop Cash Receipts", "Relationship Between Precipitation and Crop Income"]
def precip_v_income(df, title3):
    plt.figure(figsize=(12,6))
    plt.scatter(df["yearly_avg"], df["Crop cash receipts"], s=10)
    plt.xlabel(title3[0])
    plt.ylabel(title3[1])
    plt.title(title3[2])
    plt.tight_layout()
    plt.savefig("precip_vs_income_scatter.png", dpi=300)
    plt.close()

group3 = "state"
titlestate = ["Mean Normalized Precipitation", "Mean Crop Cash Receipts", "State-Level Comparison: Income vs Precipitation"]
def statcompscatt(df, group3, titlestate):
    state_summary = df.groupby(group3)[["yearly_avg", "Crop cash receipts"]].mean()
    plt.figure(figsize=(12,6))
    plt.scatter(state_summary["yearly_avg"], state_summary["Crop cash receipts"])
    plt.xlabel(titlestate[0])
    plt.ylabel(titlestate[1])
    plt.title(titlestate[2])
    plt.tight_layout()
    plt.savefig("state_level_precip_vs_income.png", dpi=300)
    plt.close()

def correl(df):
    corr = df[["yearly_avg", "Crop cash receipts"]].corr()
    print("\nCorrelation Matrix:\n", corr)

titles = "Correlation Heatmap"
def heatmap(df, title="Correlation Heatmap"):
    corr = df[["yearly_avg", "Crop cash receipts"]].corr()
    plt.figure(figsize=(6, 5))
    plt.imshow(corr, vmin=-1, vmax=1)
    plt.colorbar(label="Correlation")
    plt.xticks([0, 1], ["Precip", "Income"])
    plt.yticks([0, 1], ["Precip", "Income"])
    plt.title(title)
    plt.tight_layout()
    plt.savefig("correlation_heatmap.png", dpi=300)
    plt.close()