import pandas as pd


def color_style(x):
    if type(x) != str and x < 0:
        return "color: red"
    return ""


def table_format(df, col_format="{:,.0f}"):
    num_cols = df.select_dtypes('number').columns
    df = df.style.applymap(color_style)
    df = df.format({c: col_format for c in num_cols})
    df = df.set_table_styles(
        [
            {
                'selector': 'thead th',  # Selects the header cells
                'props': [
                    ('background-color', 'black'),
                    ('color', 'white'),
                    ('font-weight', 'bold'),
                ],
            }
        ]
    )
    return df


def table_format_total(df):
    df = table_format(df)
    df = df.applymap(
        lambda x: "background-color: silver",
        subset=slice(len(df.data) - 1, len(df.data) - 1, 1),
    )
    df = df.applymap(
        lambda x: "font-weight: bold",
        subset=slice(len(df.data) - 1, len(df.data) - 1, 1),
    )
    return df


def table_heatmap(df, cmap='RdBu'):
    max_ = abs(max(df.max(numeric_only=True, axis=1)))
    min_ = abs(min(df.min(numeric_only=True, axis=1)))
    number = max(min_, max_)
    style = table_format_total(df)
    style = style.background_gradient(
        cmap=cmap, axis=None, vmax=number, vmin=number * -1
    )  # .format(":,.0f")
    return style


def table_heatmap_col(df, col, cmap='RdBu'):
    max_ = abs(df[col].max())
    min_ = abs(df[col].min())
    number = max(min_, max_)
    style = table_format(df)
    subset = pd.IndexSlice[:, [col]]
    style = style.background_gradient(
        cmap=cmap, axis=None, vmax=number, vmin=number * -1, subset=subset
    )
    return style
