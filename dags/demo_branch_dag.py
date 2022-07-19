import time
import os
import pathlib
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
    'demo_branch_dag',
    description='Test import',
    schedule_interval=None,
    tags=['import'],
    max_active_runs=1,
    concurrency=1,
    default_args=default_args
)

with dag:
    task1 = airflow.operators.python.PythonOperator(task_id='sleep1', python_callable=func1)
    task2 = airflow.operators.python.PythonOperator(task_id='sleep2', python_callable=func1)
    task3 = airflow.operators.python.PythonOperator(task_id='sleep3', python_callable=func1)
    task4 = airflow.operators.python.PythonOperator(task_id='sleep4', python_callable=func1)
    task5 = airflow.operators.python.PythonOperator(task_id='sleep5', python_callable=func1)
    task6 = airflow.operators.python.PythonOperator(task_id='sleep6', python_callable=func1)
    # task7 = airflow.operators.python.PythonOperator(task_id='sleep7', python_callable=func1)
    # task8 = airflow.operators.python.PythonOperator(task_id='sleep8', python_callable=func1)

    # def choose_branch(cur_day, **kwargs):
    def choose_branch(**kwargs):
        current_day = kwargs['cur_day']
        if current_day.month == 8:
            return task2.task_id, task3.task_id
        else:
            return task4.task_id


    month_branch = airflow.operators.python.BranchPythonOperator(
        task_id='month_branch',
        python_callable=choose_branch,
        op_kwargs={
            'cur_day': datetime.now()
        }
    )

    week_day_branch = airflow.operators.weekday.BranchDayOfWeekOperator(
        task_id='week_day_branch',
        follow_task_ids_if_true=task5.task_id,
        follow_task_ids_if_false=task6.task_id,
        week_day='Saturday',
        # trigger_rule=TriggerRule.ALL_SUCCESS
    )

    # task5.trigger_rule = TriggerRule.NONE_FAILED

    task1 >> month_branch >> (task2, task3, task4)
    task4 >> week_day_branch >> (task5, task6)
    # (task2, task3) >> week_day_branch >> (task6, task7) >> task5
    # task4 >> task5
