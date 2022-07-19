import time
from datetime import datetime
from textwrap import dedent

import airflow
from airflow.decorators import dag
from airflow.decorators import task
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.trigger_rule import TriggerRule


def func1():
    time.sleep(5)


@dag(
    dag_id="get_api_description",
    schedule_interval=None,
    start_date=datetime(2022, 1, 16),
    catchup=False,
    tags=['ORB', 'Tags'],
    description='DAG orb_description')
def get_tags():
    hook = PostgresHook('dwh_postgres_local')
    result = hook.get_records("""select distinct tagid from airflow_test.tagslive
                    where tagid not in (select tagid from airflow_test.tag_description);""")

    finish = airflow.operators.python.PythonOperator(task_id='finish', python_callable=func1, trigger_rule='dummy')

    for row in result:
        # http://10.44.140.83:4444/api/TagConfiguration/23
        extract = SimpleHttpOperator(
            task_id=f"extract_description_id_{row[0]}",
            http_conn_id="orb_tagslive_api_descriptions",
            method='GET',
            endpoint=f'/api/TagConfiguration/{row[0]}',
            # data=f'',  #endpoint?param1=value1
            headers={"Content-Type": "application/json"},
            response_filter=lambda response: response.json()['description'],
            # do_xcom_push=True
            trigger_rule=TriggerRule.ALL_SUCCESS
        )

        # extract.output
        insert = PostgresOperator(
            task_id=f"insert_id_{row[0]}",
            postgres_conn_id='dwh_postgres_local',
            sql=f"""INSERT INTO airflow_test.tag_description (tagid, description) 
                    values ( 
                        %s, 
                        '{{{{ ti.xcom_pull(key='return_value', task_ids='extract_description_id_{row[0]}') }}}}'
                    );""",
            parameters=(row[0],)
        )

        extract.doc_md = dedent(
            """\
            ### Task Documentation
            You can document your task using the attributes `doc_md` (markdown),
            `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
            rendered in the UI's Task Instance Details page.
            """
        )
        extract.doc_json = {'att1': 'value1'}

        extract >> insert >> finish


etl_dag = get_tags()

etl_dag.doc_md = __doc__  # providing that you have a docstring at the beginning of the DAG
etl_dag.doc_md = """
    ### Описание дага
    Даг выгружает из таблицы замеров отсутствующие теги и загружает их описание в справочник
    """


# v2
@dag(
    dag_id="get_api_description2",
    schedule_interval=None,
    start_date=datetime(2022, 1, 16),
    catchup=False,
    tags=['ORB', 'Tags'],
    description='DAG orb_description')
def get_tags2():
    pg_hook = PostgresHook('dwh_postgres_local')

    finish = airflow.operators.python.PythonOperator(task_id='finish',
                                                     python_callable=func1,
                                                     trigger_rule=TriggerRule.NONE_FAILED
                                                     )

    @task(
        trigger_rule=TriggerRule.DUMMY
    )
    def extract():
        rows = pg_hook.get_records("""select distinct tagid from airflow_test.tagslive
                        where tagid not in (select tagid from airflow_test.tag_description);""")

        http_hook = HttpHook(
            http_conn_id="orb_tagslive_api_descriptions",
            method='GET',
        )

        result = []
        for row in rows:
            # http://10.44.140.83:4444/api/TagConfiguration/23
            response = http_hook.run(
                endpoint=f'/api/TagConfiguration/{row[0]}',
                headers={"Content-Type": "application/json"},
            ).json()
            result.append((response['id'], response['description']))

        return ', '.join(str(_) for _ in result)

    @task(
        trigger_rule=TriggerRule.ALL_SUCCESS
    )
    def insert(**kwargs):
        value = kwargs['ti'].xcom_pull(task_ids='extract', key='return_value')
        pg_hook.run(sql=f'INSERT INTO airflow_test.tag_description (tagid, description) '
                        f'values {value} on conflict do nothing')

    def insert_branch(**kwargs):
        rt = kwargs['ti'].xcom_pull(task_ids='extract', key='return_value')
        if rt:
            return 'insert'
        return 'finish'

    direction = BranchPythonOperator(
        task_id='direction',
        python_callable=insert_branch,
        provide_context=True)

    extract() >> direction >> insert() >> finish
    direction >> finish

etl_dag2 = get_tags2()
