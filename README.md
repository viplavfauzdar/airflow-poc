# Apache Airflow POC — ETL by Example

Learn Apache Airflow using Docker Compose, the TaskFlow API, dynamic task mapping, and Datasets.

## Quick start

```bash
cd airflow-poc
docker compose up airflow-init
docker compose up -d
# UI: http://localhost:8080  (admin / admin)
```

## Airflow Setup

The Docker Compose setup spins up several containers to provide a complete Airflow environment:

- **webserver**: Airflow UI for monitoring DAGs, triggering runs, and viewing logs.
- **scheduler**: Responsible for scheduling and triggering DAG tasks.
- **worker**: Executes tasks (used with Celery or Kubernetes executors).
- **triggerer**: Manages deferrable operators and asynchronous events.
- **postgres**: Airflow metadata database.
- **redis**: Broker for Celery executor (if enabled).
- **airflow-init**: Initializes the Airflow database and creates the admin user before other services start.

These services work together in an isolated environment to run Airflow smoothly. Logs for tasks and the scheduler are stored in the `logs/` folder.

### Architecture Diagram

```text
          +-------------+
          | airflow-init|  (initializes DB, runs first)
          +-------------+
                 |
                 v
          +--------------+
          |   postgres   |<--------------------------------+
          +--------------+                                 |
           ^     ^     ^     ^                             |
           |     |     |     |                             |
+----------+  +--+--+  |  +--+--+          +-------------+ |
| webserver |  |scheduler|  |triggerer|   |    redis    | |
+----------+  +--+--+  +--+--+          +-------------+ |
                 |                                   |    |
                 | tasks                             |    |
                 +---------------------------------->+    |
                                                     |    |
                                                     v    |
                                                  +--------+
                                                  | worker |
                                                  +--------+
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
