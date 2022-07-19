from airflow.models import DAG   # импорт класса группы заданий
from airflow.operators.bash import BashOperator

from dwh_default_args import default_args   # импорт словаря параметров поумолчанию


class ShellOperator(BashOperator):

    def __init__(
        self, 
        command,
        *args,
        **kwargs
    ):
        super(ShellOperator, self).__init__(
            bash_command='dotnet /app/shell/Itsk.Dwh.Shell.dll ' + command,
            *args, 
            **kwargs
        )


class ShellFailByExceptionOperator(BashOperator):

    def __init__(
        self, 
        command,
        *args,
        **kwargs
    ):
        super(ShellFailByExceptionOperator, self).__init__(
            bash_command='dotnet /app/shell/Itsk.Dwh.Shell.dll ' + command + ' 2>&1 | /opt/airflow/dags/fail_by_exception.sh ',
            *args, 
            **kwargs
        )


# функция для создания групп заданий в цикле (создание единичных заданий)
def create_single_command_dag(key: str, value: str, tags: list = []):
    dag = DAG(
        key + '_single_command',
        description='Единичная команда: ' + key,
        schedule_interval=None,
        tags=['singleCommand'] + tags,
        max_active_runs=1,
        concurrency=1,
        default_args=default_args)
        
    with dag:
        ShellFailByExceptionOperator(
            task_id=key,
            command=value
        )
                
    return dag
