import pandas as pd

def merge_csvs(new_csv_name, csvs, group_on):
    df1 = pd.read_csv(csvs[0])
    df2 = pd.read_csv(csvs[1])
    merged_df = pd.merge(df1, df2, on=group_on)
    merged_df.to_csv(new_csv_name, index=False)