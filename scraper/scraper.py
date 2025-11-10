from playwright.sync_api import sync_playwright
from playwright.sync_api import Page, sync_playwright, TimeoutError as PWTimeout
import pandas as pd
from urllib.parse import quote, urljoin
import os
import datetime as dt
import time
import os
import yaml
import sqlite3
from dataclasses import dataclass

import config
from logger_steup import setup_logger
from utils import _norm_text
from scraping_hall_page import extract_date_url
from scraping_date_page import extract_model_url
from scraping_model_page import extract_model_data
from df_clean import df_data_clean
import df_to_db

# =========================
# 設定・ロガー
# =========================
filename, ext = os.path.splitext(os.path.basename(__file__))
logger = setup_logger(filename, log_file=config.LOG_PATH)


# =========================
# ページ操作
# =========================
def extract_result_data(hall_url: str, period: int = 1) -> pd.DataFrame:
    
    """
    ホールURLと期間を受けて、そのホールの対象日・対象機種の全データを返す
    """
    
    df_frames: list[pd.DataFrame] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            date_urls = extract_date_url(hall_url, page, period=period)
            for pref, hall, date, date_url in date_urls:
                model_urls = extract_model_url(page, hall, pref, date_url, date)
                if not model_urls:
                    continue
                df_model = extract_model_data(page, model_urls)
                if not df_model.empty:
                    df_frames.append(df_model)
                df_model.to_csv(f"data/csv/{pref}_{hall}_{date}.csv", index=False)

        finally:
            browser.close()
            df_frames = pd.concat(df_frames, ignore_index=True)
        # df_frames.to_csv(f"data/csv/{pref}_{hall}.csv", index=False)

    return df_frames


def main(test_mode=False) -> pd.DataFrame:
    start = time.perf_counter()

    # yaml  読み込み
    if not os.path.exists(config.HALLS_YAML):
        raise FileNotFoundError(f"YAMLが見つかりません: {config.HALLS_YAML}")
    with open(config.HALLS_YAML, "r", encoding="utf-8") as f:
        halls_cfg = yaml.safe_load(f).get("halls", [])

    hall_list: list[config.HallInfo] = [
        config.HallInfo(slug=h["slug"], period=int(h["period"])) for h in halls_cfg
    ]
    
    if test_mode:
        hall_list = hall_list[:2]

    frames: list[pd.DataFrame] = []
    for i, h in enumerate(hall_list, start=1):
        try:
            encoded_slug = quote(h.slug)
            hall_url = urljoin(config.MAIN_URL, encoded_slug)
            logger.info("(%d/%d) 処理中: %s", i, len(hall_list), hall_url)
            df_hall = extract_result_data(hall_url, h.period)
            logger.debug(df_hall.shape)
            if not df_hall.empty:
                frames.append(df_hall)
        except Exception as e:
            logger.exception("ホール処理でエラー: %s", e)

    df_all = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    df_all.to_csv(config.OUTPUT_CSV)

    # 列の順番を固定（下流の処理を安定化）
    cols = ["pref", "hall", "model", "date", "台番", "G数", "BB", "RB", "差枚"]
    for c in cols:
        if c not in df_all.columns:
            df_all[c] = pd.NA
    df_all = df_all[cols]

    end = time.perf_counter()
    logger.info("全体処理時間: %.2f 秒", end - start)

    return df_all


if __name__ == "__main__":
    
    df = main(test_mode=True)
    df = df_data_clean(df)
    
    # conn = sqlite3.connect(config.DB_PATH)
    # # cursor = conn.cursor()

    # # df_to_db.add_model(df, conn, cursor)
    # # df_to_db.add_prefecture_and_hall(df, conn, cursor)
    # # df_to_db.add_data_result(conn, cursor, df)
    
    # # conn.commit()
    # # conn.close()
    
