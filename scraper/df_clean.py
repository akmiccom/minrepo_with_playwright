import pandas as pd


def df_data_clean(df):
    ALIAS_MAP = {
        "SミスタージャグラーKK": "ミスタージャグラー",
        "S ミスタージャグラー KK": "ミスタージャグラー",
        "SアイムジャグラーEX": "アイムジャグラーEX-TP",
        "ファンキージャグラー2KT": "ファンキージャグラー2",
        "ジャグラーガールズSS": "ジャグラーガールズ",
        "S ネオアイムジャグラーEX KK": "ネオアイムジャグラーEX",
    }

    COULMNS_RENAME_MAP = {
        "pref": "pref",
        "prefecture": "pref",
        "h_name": "hall",
        "m_name": "model",
        "model_name": "model",
        "date": "date",
        "台番": "unit_no",
        "G数": "game",
        "BB": "bb",
        "RB": "rb",
        "差枚": "medal",
    }

    df = df.rename(columns=COULMNS_RENAME_MAP)
    df["model"] = df["model"].replace(ALIAS_MAP)
    df["game"] = df["game"].str.replace(",", "").astype(int)
    df["medal"] = df["medal"].str.replace(",", "").astype(int)


    df.to_csv("data/csv/halls_date_cleaner.csv", index=False)
    return df


if __name__ == "__main__":
    df = pd.read_csv("data/csv/halls.csv")
    df_clean = df_data_clean(df)
