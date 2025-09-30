# Apache Airflow POC — ETL by Example

Learn Apache Airflow using Docker Compose, the TaskFlow API, dynamic task mapping, and Datasets.

## Quick start

```bash
cd airflow-poc
docker compose up airflow-init
docker compose up -d
# UI: http://localhost:8080  (admin / admin)
```

Turn on both DAGs: **crypto_prices_etl** and **crypto_aggregates**.

### Optional: configure coins
Admin → Variables → add Variable `coins` (e.g., `bitcoin,ethereum,solana,dogecoin`).

### Output files
- `./data/crypto_prices.parquet`
- `./data/crypto_daily_avgs.parquet`

### Demo warehouse (Postgres)
- Host: localhost, Port: 5433, User: demo, Password: demo, DB: warehouse

## Testing

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt apache-airflow==2.9.3 pytest
pytest -q
```

## Cleanup
```bash
docker compose down -v
```
