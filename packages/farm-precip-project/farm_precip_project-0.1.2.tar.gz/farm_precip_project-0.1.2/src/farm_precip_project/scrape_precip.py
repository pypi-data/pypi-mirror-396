import pandas as pd
import requests


def txt_to_csv(url, txt_name, csv_name, colspecs, cols):
    df = pd.read_fwf(txt_name, colspecs=colspecs, names=cols)
    df = df.apply(pd.to_numeric, errors='coerce')
    df.to_csv(txt_name, csv_name, colspecs, cols)


def read_url_txt(url, txt_name, csv_name, colspecs, cols):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    
    if r.status_code != 200:
        print(f"url status code is {r.status_code} not 200. Please check your url")
        return
    with open(txt_name, "wb") as f:
        f.write(r.content)
    from farm_precip_project import txt_to_csv
    txt_to_csv(txt_name, csv_name, colspecs, cols)


def normalized_data(df_to_read, new_col_name, csv_name_clean, months, groups):
    df = pd.read_csv(df_to_read)
    df[new_col_name] = df[months].mean(axis=1)
    state_precip = df.groupby(groups)[new_col_name].mean()
    state_precip.to_csv(csv_name_clean)