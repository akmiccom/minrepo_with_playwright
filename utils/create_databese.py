import sqlite3


def create_databese(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- テーブル作成 ---

    # 都道府県テーブル
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prefectures (
            prefecture_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        """
    )

    # ホールテーブル（prefecture_id に変更）
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS halls (
            hall_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            prefecture_id INTEGER NOT NULL,
            FOREIGN KEY (prefecture_id) REFERENCES prefectures(prefecture_id),
            UNIQUE (name, prefecture_id)
        );
        """
    )

    # 機種テーブル
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS models (
            model_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        """
    )

    # 出玉データテーブル
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS results (
        hall_id INTEGER NOT NULL,
        model_id INTEGER NOT NULL,
        unit_no INTEGER NOT NULL,
        date DATE NOT NULL,
        game INTEGER,
        BB INTEGER,
        RB INTEGER,
        medal INTEGER,
        FOREIGN KEY (hall_id) REFERENCES halls(hall_id),
        FOREIGN KEY (model_id) REFERENCES models(model_id)
        );
        """
    )

    # 出玉データのユニーク制約（ホール・台番号・日付の重複を防ぐ）
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_results_unique
        ON results (hall_id, model_id, unit_no, date);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_results_hall_date  ON results (hall_id, date);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_results_model_date ON results (model_id, date);
        """
    )

    # コミットして終了
    conn.commit()
    conn.close()

    print(f"✅ データベース {DB_PATH} を作成しました。")


if __name__ == "__main__":
    DB_PATH = "data/db/minrepo_02.db"
    create_databese(DB_PATH)
