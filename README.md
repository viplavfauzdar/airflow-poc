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
- **warehouse**: Demo Postgres **data warehouse** used by the DAGs (separate from Airflow metadata). Exposed on 
localhost:5433 (user/password: demo, db: warehouse).
- **redis**: Acts as the task queue/broker when using the Celery executor. The scheduler enqueues tasks into Redis, and workers dequeue tasks for execution. Without Redis (or another broker like RabbitMQ), the scheduler could not distribute tasks across multiple workers.
- **airflow-init**: Initializes the Airflow database and creates the admin user before other services start.

These services work together in an isolated environment to run Airflow smoothly. Logs for tasks and the scheduler are stored in the `logs/` folder. Note: This POC runs two Postgres containers: `postgres` (Airflow metadata) and `warehouse` (analytics/demo).

### Architecture Diagram

```text
          +-------------+
          | airflow-init|  (initializes DB, runs first)
          +-------------+
                 |
                 v
          +--------------+
          |   postgres   |  Airflow metadata
          +--------------+
           ^     ^     ^     ^
           |     |     |     |
+----------+  +--+--+  |  +--+--+          +-------------+
| webserver |  |scheduler|  |triggerer|    |    redis    |
+----------+  +--+--+  +--+--+          +-------------+
                 |                                   |
                 | tasks                             |
                 +---------------------------------->+
                                                     |
                                                     v
                                                  +--------+        read/write          +-----------------------------+
                                                  | worker |--------------------------->| warehouse (postgres:5433)   |
                                                  +--------+                            | user: demo / pwd: demo      |
                                                                                         | db: warehouse               |
                                                                                         +-----------------------------+
```


Turn on both DAGs: **crypto_prices_etl** and **crypto_aggregates**.

### Optional: configure coins
Admin → Variables → add Variable `coins` (e.g., `bitcoin,ethereum,solana,dogecoin`).

### Output files
- `./data/crypto_prices.parquet`
- `./data/crypto_daily_avgs.parquet`


### Demo warehouse (Postgres)
- Host: localhost, Port: 5433, User: demo, Password: demo, DB: warehouse

### Optional: Redis UI

You can explore the Redis broker that Airflow uses for the Celery executor:

- **Redis Commander** is included in this setup at [http://localhost:8081](http://localhost:8081).
- It connects to the `redis` service automatically (`REDIS_HOSTS=local:redis:6379`).
- Use it to inspect Celery queues (`celery`, `unacked`, etc.), view keys, and debug task distribution.

Alternatively, you can install **RedisInsight** (desktop GUI) and connect it to `localhost:6379` for a more advanced view.

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
