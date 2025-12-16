import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def remove_outliers(df, col_name, threshold, lower = True):
    if lower:
        df = df[df[col_name] > threshold]
        return df
    else:
        df = df[df[col_name] < threshold]
        return df

def center_column(df, col_name, col_group, col_stand_name):
    mean_state_col = df.groupby(col_group)[col_name].transform('mean')
    df[col_stand_name] = (df[col_name] - mean_state_col)
    return df

def corr_and_plot(df, col1, col2, plot_file,n_digits):
    correlation = round(df[col1].corr(df[col2]),n_digits)
    
    plt.figure(figsize=(8, 6))
    plt.scatter(df[col1], df[col2])
    plt.title(f'Scatter plot of {col1} vs {col2}, Correlation: {correlation}')
    plt.xlabel(col1)
    plt.ylabel(col2)
    plt.show()
    plt.savefig(plot_file)

    return correlation


def make_scatter_w_cat(df, colx, coly, colcat, plot_file):
    cat_order = sorted(df[colcat].unique())
    palette = sns.color_palette("husl", len(cat_order))

    sns.scatterplot(
    data=df,
    x=colx,
    y=coly,
    hue=colcat,
    hue_order=cat_order,
    palette=palette,
    s=30
    )

    leg = plt.legend(title=colcat, bbox_to_anchor=(1.02, 1), 
                     loc="upper left", borderaxespad=0.,
                     ncol = 2)
    for text in leg.get_texts():
        text.set_fontsize(8)  # smaller labels

    plt.show()
    plt.savefig(plot_file)
