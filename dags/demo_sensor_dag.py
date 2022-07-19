import datetime
import time

import airflow.operators.python
import airflow.sensors.external_task
from airflow.utils.trigger_rule import TriggerRule

from dwh_default_args import default_args


def func1():
    time.sleep(5)


def func2():
    print(datetime.datetime.minute % 2)
    if datetime.datetime.minute % 2:
        raise 'ERROR'


dag = airflow.models.DAG(
    'demo_sensor_dag',
    description='Test import',
    schedule_interval=None,
    tags=['import'],
    max_active_runs=1,
    concurrency=1,
    default_args=default_args
)

with dag:
    task1 = airflow.operators.python.PythonOperator(task_id='sleep1', python_callable=func1, trigger_rule='dummy')
    task2 = airflow.operators.python.PythonOperator(task_id='sleep2', python_callable=func1, trigger_rule='dummy')
    task3 = airflow.operators.python.PythonOperator(task_id='sleep3', python_callable=func1, trigger_rule='dummy')
    # task4 = airflow.operators.python.PythonOperator(task_id='sleep4', python_callable=func1, trigger_rule='dummy')
    task5 = airflow.operators.python.PythonOperator(task_id='sleep5', python_callable=func1,
                                                    trigger_rule=TriggerRule.ALL_SUCCESS)

    task4 = airflow.sensors.external_task.ExternalTaskSensor(
        task_id='sensor123',
        external_dag_id='demo_sensor_dag',
        external_task_ids=['sleep1', 'sleep2', 'sleep3'],
        timeout=120,
        allowed_states=['success'],
        # execution_date_fn=get_last_dag_run,
        soft_fail=True,
        mode='reschedule'
    )

    (task1, task2, task3) >> task4 >> task5
