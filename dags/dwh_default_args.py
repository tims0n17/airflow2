from datetime import timedelta

import airflow
from airflow.utils.dates import days_ago

default_args = {
	'owner': 'airflow',
	'depends_on_past': False,
	'start_date':  airflow.utils.dates.days_ago(1),
	'email': ['sagitov.ara@gazprom-neft.ru', 'Smirnov.AVikt@gazprom-neft.ru', 'Ismagilov.TF@gazprom-neft.ru', 'Savelev.SP@gazprom-neft.ru', 'Migranov.NN@gazprom-neft.ru', 'Vatolin.AA@gazprom-neft.ru', 'Kamaltdinov.RRi@gazprom-neft.ru', 'Akhmadullin.DG@gazprom-neft.ru'],
	'email_on_failure': True,
	'email_on_retry': False,
	'retries': 2,
	'retry_delay': timedelta(minutes=5),
	'retry_exponential_backoff': True,
	'catchup': False,
	'max_active_runs': 1,
	'execution_timeout': timedelta(hours=10)
}