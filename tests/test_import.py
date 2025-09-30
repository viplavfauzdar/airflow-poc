from airflow.models import DagBag

def test_dags_load():
    dagbag = DagBag(dag_folder='dags', include_examples=False)
    assert len(dagbag.import_errors) == 0, f"Import errors: {dagbag.import_errors}"
    assert 'crypto_prices_etl' in dagbag.dags
    assert 'crypto_aggregates' in dagbag.dags
