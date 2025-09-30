from __future__ import annotations
from datetime import datetime
from airflow.decorators import dag, task
from airflow.datasets import Dataset
from pathlib import Path
import pandas as pd

RAW_DATASET = Dataset("file:///opt/airflow/data/crypto_prices.parquet")

@dag(
    schedule=[RAW_DATASET],
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["poc", "datasets"],
)
def crypto_aggregates():
    @task
    def compute_daily_averages(path: str) -> str:
        df = pd.read_parquet(path)
        df["ts_utc"] = pd.to_datetime(df["ts_utc"])
        df["date"] = df["ts_utc"].dt.date
        daily = (
            df.groupby(["date", "coin"], as_index=False)["price_usd"]
            .mean()
            .rename(columns={"price_usd": "avg_price_usd"})
        )
        out_path = Path("/opt/airflow/data/crypto_daily_avgs.parquet")
        daily.to_parquet(out_path, index=False)
        return str(out_path)

    compute_daily_averages("/opt/airflow/data/crypto_prices.parquet")

dag = crypto_aggregates()
