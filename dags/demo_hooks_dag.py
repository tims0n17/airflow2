import time
import datetime

from airflow.models import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator, PostgresHook
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule


def func1():
    time.sleep(5)


def func2():
    raise 'ERROR'


def get_data(**kwargs):
    table_name = kwargs['table_name']
    print(table_name)
    sql = f"select id, description from {table_name};"
    pg_hook = PostgresHook(postgres_conn_id='dwh_postgres_local')
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(sql)
    all_rows = ''
    for row in cursor:
        all_rows += f'{row}\n'
    return all_rows

# jinja templates
# https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html
with DAG(
    dag_id="demo_postgres_dag",
    start_date=datetime.datetime(2020, 2, 2),
    schedule_interval=None,
    catchup=False,
) as dag:
    begin_task = DummyOperator(task_id='begin')
    pg_operator_task = PostgresOperator(
        task_id="pg_operator",
        postgres_conn_id='dwh_postgres_local',
        sql="""create table if not exists dbt_test.new_table_{{ ds_nodash }} (
            id serial primary key,
            description varchar);
            insert into dbt_test.new_table_{{ ds_nodash }} (description) values ('one'), ('two'), ('three');
        """,
        # parameters=
    )

    pg_hook_task = PythonOperator(task_id='pg_hook', python_callable=get_data,
                                  op_kwargs={'table_name': 'dbt_test.new_table_{{ ds_nodash }}'})

    begin_task >> pg_operator_task >> pg_hook_task
