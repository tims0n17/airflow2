import time
from datetime import datetime

import airflow.operators.python
import airflow.operators.weekday
from airflow.models import DAG  # импорт класса группы заданий
from airflow.utils.trigger_rule import TriggerRule

from dwh_default_args import default_args


def func1():
    time.sleep(5)


def func2():
    raise 'ERROR'


dag = DAG(
    'demo_simple_dag',
    description='Test import',
    schedule_interval=None,
    tags=['import'],
    max_active_runs=1,
    concurrency=1,
    default_args=default_args
)

with dag:
    task1 = airflow.operators.python.PythonOperator(task_id='sleep1', python_callable=func1, trigger_rule='dummy')
    task2 = airflow.operators.python.PythonOperator(task_id='sleep2', python_callable=func2, trigger_rule='dummy')
    task3 = airflow.operators.python.PythonOperator(task_id='sleep3', python_callable=func1, trigger_rule='dummy')
    task4 = airflow.operators.python.PythonOperator(task_id='sleep4', python_callable=func1, trigger_rule='dummy')
    task5 = airflow.operators.python.PythonOperator(task_id='sleep5', python_callable=func1, trigger_rule='dummy')
    task6 = airflow.operators.python.PythonOperator(task_id='sleep6', python_callable=func1, trigger_rule='dummy')
    task7 = airflow.operators.python.PythonOperator(task_id='sleep7', python_callable=func1, trigger_rule='dummy')
    task8 = airflow.operators.python.PythonOperator(task_id='sleep8', python_callable=func1, trigger_rule='dummy')

    task5.trigger_rule = TriggerRule.NONE_FAILED
    task7.trigger_rule = TriggerRule.ALL_SUCCESS
    # task5.trigger_rule = TriggerRule.

    task1 >> (task2, task3, task4)
    (task2, task3) >> task7 >> task5
    task4 >> task5
