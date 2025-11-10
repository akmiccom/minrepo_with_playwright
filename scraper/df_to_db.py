import pandas as pd
import sqlite3


def add_model(df, conn, cursor):
    """--- モデルの登録 ---"""
    new_model_count = 0
    models = df["model"].dropna().unique().tolist()
    for model in models:
        cursor.execute("INSERT OR IGNORE INTO models (name) VALUES (?)", (model,))
        if cursor.rowcount > 0:
            new_model_count += 1

    if new_model_count == 0:
        print("モデルの新規登録はありません。")
    else:
        print(f"新規モデル: {new_model_count} 件")


def add_prefecture_and_hall(df, conn, cursor):
    """--- 都道府県とホール登録 ---"""
    new_pref_count, new_hall_count = 0, 0
    prefectures = df["pref"].dropna().unique().tolist()
    for pref in prefectures:
        # 都道府県を登録（重複無視）
        cursor.execute("INSERT OR IGNORE INTO prefectures (name) VALUES (?)", (pref,))
        if cursor.rowcount > 0:
            new_pref_count += 1

        # 都道府県IDの取得
        cursor.execute("SELECT prefecture_id FROM prefectures WHERE name = ?", (pref,))
        result = cursor.fetchone()
        if not result:
            print(f"⚠ 都道府県IDの取得に失敗しました: {pref}")
            continue
        prefecture_id = result[0]

        # 該当都道府県のホールを登録
        halls = df.loc[df["pref"] == pref, "hall"].dropna().unique().tolist()
        for hall in halls:
            cursor.execute(
                "INSERT OR IGNORE INTO halls (name, prefecture_id) VALUES (?, ?)",
                (hall, prefecture_id),
            )
            if cursor.rowcount > 0:
                new_hall_count += 1

    if new_pref_count == new_hall_count == 0:
        print("都道府県、ホールの新規登録はありません。")
    else:
        # --- 結果メッセージ ---
        print(f"・新規都道府県: {new_pref_count} 件")
        print(f"・新規ホール: {new_hall_count} 件")


def add_data_result(conn, cursor, df):
    """--- データ登録 ---"""
    new_result_count = 0

    prefectures = df["pref"].dropna().unique().tolist()
    for pref in prefectures:
        # 都道府県追加とIDの取得
        cursor.execute("INSERT OR IGNORE INTO prefectures (name) VALUES (?)", (pref,))
        cursor.execute("SELECT prefecture_id FROM prefectures WHERE name = ?", (pref,))
        prefecture_id = cursor.fetchone()[0]

        # ホールの登録
        halls = df.loc[df["pref"] == pref, "hall"].dropna().unique().tolist()
        for hall in halls:
            cursor.execute(
                "INSERT OR IGNORE INTO halls (name, prefecture_id) VALUES (?, ?)",
                (hall, prefecture_id),
            )

        df_pref = df[df["pref"] == pref]
        for _, row in df_pref.iterrows():
            h_name = row["hall"]
            m_name = row["model"]
            unit_no = int(row["unit_no"])
            date = row["date"]
            game = int(row["game"])
            bb = int(row["bb"])
            rb = int(row["rb"])
            medal = int(row["medal"])

            # 3-1) hall_id 取得
            cursor.execute(
                "SELECT hall_id FROM halls WHERE name = ? AND prefecture_id = ?",
                (h_name, prefecture_id),
            )
            hall_row = cursor.fetchone()
            if not hall_row:
                # 念のため（通常は上の INSERT OR IGNORE で存在する想定）
                cursor.execute(
                    "INSERT OR IGNORE INTO halls (name, prefecture_id) VALUES (?, ?)",
                    (h_name, prefecture_id),
                )
                cursor.execute(
                    "SELECT hall_id FROM halls WHERE name = ? AND prefecture_id = ?",
                    (h_name, prefecture_id),
                )
                hall_row = cursor.fetchone()
            hall_id = hall_row[0]

            # 3-2) model_id 取得（なければ作成）
            cursor.execute("INSERT OR IGNORE INTO models (name) VALUES (?)", (m_name,))
            cursor.execute("SELECT model_id FROM models WHERE name = ?", (m_name,))
            model_id = cursor.fetchone()[0]

            # 3-3) results へ登録（重複は無視）
            cursor.execute(
                """
            INSERT OR IGNORE INTO results
            (hall_id, model_id, unit_no, date, game, bb, rb, medal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (hall_id, model_id, unit_no, date, game, bb, rb, medal),
            )
            if cursor.rowcount > 0:
                new_result_count += 1

    if new_result_count == 0:
        print("データの新規登録はありません。")
    else:
        print(f"データ登録数: {new_result_count} 件")


if __name__ == "__main__":

    DB_PATH = "data/db/minrepo_02.db"
    CSV_PATH = "data/csv/halls_date_cleaner.csv"

    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    add_model(df, conn, cursor)
    add_prefecture_and_hall(df, conn, cursor)
    add_data_result(conn, cursor, df)
    
    conn.commit()
    conn.close()

