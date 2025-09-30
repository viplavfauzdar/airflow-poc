from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import requests
from airflow.decorators import dag, task
from airflow.datasets import Dataset
from airflow.models import Variable

RAW_DATASET = Dataset("file:///opt/airflow/data/crypto_prices.parquet")

COINS_DEFAULT = ["bitcoin", "ethereum", "solana", "dogecoin"]

@dag(
    schedule="@hourly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["poc", "taskflow", "dynamic-mapping"],
)
def crypto_prices_etl():
    """
    Fetch hourly prices for a list of crypto coins from CoinGecko's public API,
    transform with pandas, write a parquet file, and load a summary into Postgres.
    Demonstrates: TaskFlow API, dynamic task mapping, datasets, and XCom-less I/O.
    """

    data_dir = Path("/opt/airflow/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    @task
    def get_coins() -> List[str]:
        raw = Variable.get("coins", default_var=",".join(COINS_DEFAULT))
        return [c.strip() for c in raw.split(",") if c.strip()]

    @task
    def fetch_price(coin: str) -> dict:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        payload = r.json()
        return {
            "coin": coin,
            "price_usd": float(payload[coin]["usd"]),
            "ts_utc": datetime.utcnow().replace(microsecond=0).isoformat(),
        }

    @task
    def combine_and_transform(rows: List[dict]) -> str:
        df = pd.DataFrame(rows)
        import numpy as np
        df["price_usd_log"] = df["price_usd"].apply(lambda x: 0 if x <= 0 else float(np.log(x)))
        out_path = data_dir / "crypto_prices.parquet"
        df.to_parquet(out_path, index=False)
        return str(out_path)

    @task(outlets=[RAW_DATASET])
    def persist_dataset(path: str) -> str:
        return path

    @task
    def load_summary_to_postgres(path: str):
        import sqlalchemy as sa
        engine = sa.create_engine("postgresql+psycopg2://demo:demo@warehouse-db:5432/warehouse")
        with engine.begin() as conn:
            conn.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS crypto_prices (
                    ts_utc TIMESTAMP NOT NULL,
                    coin TEXT NOT NULL,
                    price_usd DOUBLE PRECISION NOT NULL,
                    price_usd_log DOUBLE PRECISION
                )
                """
            )
            df = pd.read_parquet(path)
            df.to_sql("crypto_prices", conn, if_exists="append", index=False)

    coins = get_coins()
    rows = fetch_price.expand(coin=coins)
    path = combine_and_transform(rows)
    produced = persist_dataset(path)
    load_summary_to_postgres(produced)


dag = crypto_prices_etl()
