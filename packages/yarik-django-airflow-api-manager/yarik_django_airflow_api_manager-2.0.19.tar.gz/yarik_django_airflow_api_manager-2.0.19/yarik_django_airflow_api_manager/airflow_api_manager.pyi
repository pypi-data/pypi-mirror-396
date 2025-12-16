"""Определения типов и классов менеджера Airflow."""

from collections.abc import Callable
from datetime import datetime
from typing import Any, Concatenate, Literal

import requests
from pydantic import BaseModel

RunType = Literal["backfill", "manual", "scheduled", "dataset_triggered"]
DagState = Literal["queued", "running", "success", "failed"]
TaskState = Literal[
    "success",
    "running",
    "failed",
    "upstream_failed",
    "skipped",
    "up_for_retry",
    "up_for_reschedule",
    "queued",
    "none",
    "scheduled",
    "deferred",
    "removed",
    "restarting",
]
TriggerRule = Literal[
    "all_success",
    "all_failed",
    "all_done",
    "one_success",
    "one_failed",
    "none_failed",
    "none_skipped",
    "none_failed_or_skipped",
    "none_failed_min_one_success",
    "dummy",
]

class ModelWithAliasGenerator(BaseModel):
    class Config:
        alias_generator = ...
        populate_by_name = ...

class SLAMiss(BaseModel):
    task_id: str
    dag_id: str
    execution_date: datetime
    email_sent: bool
    timestamp: datetime
    description: str | None = ...
    notification_sent: bool

class Trigger(BaseModel):
    id: int
    classpath: str
    kwargs: str
    created_date: datetime
    trigger_id: int | None = ...

class Job(BaseModel):
    id: int
    dag_id: str | None = ...
    state: str | None = ...
    job_type: str | None = ...
    start_date: datetime | None = ...
    end_date: datetime | None = ...
    latest_heartbeat: datetime | None = ...
    executor_class: str | None = ...
    hostname: str | None = ...
    unixname: str | None = ...

class Tag(BaseModel):
    name: str

class Dag(ModelWithAliasGenerator):
    dag_id: str
    root_dag_id: str | None = ...
    is_paused: bool | None = ...
    is_active: bool | None = ...
    is_subdag: bool
    last_parsed_time: datetime | None = ...
    last_pickled: datetime | None = ...
    last_expired: datetime | None = ...
    scheduler_lock: bool | None = ...
    pickle_id: str | None = ...
    default_view: str | None = ...
    fileloc: str
    file_token: str
    owners: list[str]
    description: str | None = ...
    schedule_interval: Any | None = ...
    timetable_description: str | None = ...
    tags: list[Tag] | None = ...
    max_active_tasks: int | None = ...
    max_active_runs: int | None = ...
    has_task_concurrency_limits: bool | None = ...
    has_import_errors: bool | None = ...
    next_dagrun: datetime | None = ...
    next_dagrun_data_interval_start: datetime | None = ...
    next_dagrun_data_interval_end: datetime | None = ...
    next_dagrun_create_after: datetime | None = ...
    max_consecutive_failed_dag_runs: int | None = ...

class Dags(ModelWithAliasGenerator):
    dags: list[Dag]
    total_entries: int

class DagRun(ModelWithAliasGenerator):
    dag_id: str
    dag_run_id: str | None = ...
    logical_date: datetime | None = ...
    start_date: datetime | None = ...
    end_date: datetime | None = ...
    data_interval_start: datetime | None = ...
    data_interval_end: datetime | None = ...
    last_scheduling_decision: datetime | None = ...
    run_type: RunType
    state: DagState
    external_trigger: bool
    conf: dict[str, Any]
    note: str | None = ...

class DagRuns(ModelWithAliasGenerator):
    dag_runs: list[DagRun]
    total_entries: int

class Task(ModelWithAliasGenerator):
    class_ref: Any
    task_id: str
    owner: str
    start_date: datetime
    end_date: datetime | None = ...
    trigger_rule: TriggerRule
    extra_links: list[Any]
    depends_on_past: bool
    is_mapped: bool
    wait_for_downstream: bool
    retries: int
    queue: str | None = ...
    pool: str
    pool_slots: int
    execution_timeout: Any
    retry_delay: Any
    retry_exponential_backoff: bool
    priority_weight: int
    weight_rule: Literal["downstream", "upstream", "absolute"]
    ui_color: str
    ui_fgcolor: str
    template_fields: list[str]
    sub_dag: Dag | None = ...
    downstream_task_ids: list[str]

class Tasks(ModelWithAliasGenerator):
    tasks: list[Task]

class TaskInstance(ModelWithAliasGenerator):
    task_id: str
    dag_id: str
    dag_run_id: str
    execution_date: datetime
    start_date: datetime | None = ...
    end_date: datetime | None = ...
    duration: float | None = ...
    state: TaskState | None = ...
    try_number: int
    map_index: int
    max_tries: int
    hostname: str
    unixname: str
    pool: str
    pool_slots: int
    queue: str | None
    priority_weight: int | None = ...
    operator: str | None = ...
    queued_when: str | None = ...
    pid: int | None = ...
    executor_config: str
    sla_miss: SLAMiss | None = ...
    rendered_fields: dict[str, Any]
    trigger: Trigger | None = ...
    triggerer_job: Job | None = ...
    note: str | None = ...

class TaskInstances(ModelWithAliasGenerator):
    task_instances: list[TaskInstance]
    total_entries: int

class Logs(ModelWithAliasGenerator):
    continuation_token: str
    content: str

class ErrorResponce(ModelWithAliasGenerator):
    type: str
    title: str | None
    status: int
    detail: str | None = ...
    instance: str | None = ...

def catch_airflow_errors[**P, R](
    func: Callable[Concatenate[P], tuple[R | None, int]],
) -> Callable[Concatenate[P], tuple[R | None, int]]:
    """Декоратор перехватывает все исключения при работе с Airflow и логирует причину ошибки.

    Returns:
        out: `Any | None`
            Возвращаемое значение оборачиваемой функции или None в случае ошибки.

    """  # noqa: RUF002

def get_request(url: str) -> requests.Response: ...
def post_request(url: str, payload: Any | None = ...) -> requests.Response: ...  # noqa: ANN401
def patch_request(url: str, payload: Any | None = ...) -> requests.Response: ...  # noqa: ANN401

class AirflowManager:
    """Интерфейс для работы с Airflow."""  # noqa: RUF002

    dag_id: str | None = ...
    dag_run_id: str | None = ...

    def __init__(self, dag_id: str | None = ..., dag_run_id: str | None = ...) -> None:
        """Инициализация экземпляра интерфейса для работы с Airflow.

        Args:
            dag_id (Optional[str], optional): идентификатор дага. По умолчанию None.
            dag_run_id (Optional[str], optional): идентификатор запуска дага. По умолчанию None.

        """  # noqa: RUF002

    def conn_good(self) -> bool:
        """Проверяет соединение с Airflow.

        Возвращает:
            bool: доступность Airflow
        """  # noqa: RUF002

    def creds_is_valid(self) -> bool:
        """Проверяет корректность учетных данных пользователя API.

        Returns:
            bool: корректность учетных данных

        """

    @catch_airflow_errors
    def get_dag(self) -> tuple[Dag | None, int]:
        """Получить даг.

        Возвращает:
            Dag | None: объект дага или None в случае ошибки
        """

    @catch_airflow_errors
    def get_dags_dict(
        self,
        tags: list[str] | None = ...,
        dag_id_pattern: str = ...,
        only_active: bool = ...,
        limit: int = ...,
        offset: int = ...,
        fields: list[str] | None = ...,
    ) -> tuple[dict[str, Any] | None, int]:
        """Получить даги в формате словаря.

        Возвращает:
            dict | None: словарь дага или None в случае ошибки
        """

    @catch_airflow_errors
    def get_dags(
        self,
        tags: list[str] | None = ...,
        dag_id_pattern: str = ...,
        only_active: bool = ...,
        limit: int = ...,
        offset: int = ...,
        fields: list[str] | None = ...,
    ) -> tuple[Dags | None, int]:
        """Получить даги.

        Аргументы:
            tags (list[str], optional): список тегов дага. По умолчанию [].
            dag_id_pattern (str, optional): паттерн идентификатора дага. По умолчанию "".
            only_active (bool, optional): учитывать только активные даги. По умолчанию True.
            limit (int, optional): лимит количества получаемых дагов. Defaults to 100.
            offset (int, optional): позиция, с которой нужно вернуть даги. Defaults to 0.
            fields (list[str] | None, optional): список запрашиваемых полей дага. Defaults to None.

        Возвращает:
            Dags: объект списка дагов или None в случае ошибки
        """  # noqa: RUF002

    @catch_airflow_errors
    def get_dags_count(
        self, tags: list[str] | None = ..., dag_id_pattern: str = ..., only_active: bool = ...
    ) -> tuple[int, int]:
        """Получить количество дагов.

        Аргументы:
            tags (list[str], optional): список тегов дага. По умолчанию [].
            dag_id_pattern (str, optional): паттерн идентификатора дага. По умолчанию "".
            only_active (bool, optional): учитывать только активные даги. По умолчанию True.

        Возвращает:
            int: количество дагов
        """

    @catch_airflow_errors
    def get_dag_runs(self, states: list[DagState] | None = ...) -> tuple[list[DagRun] | None, int]:
        """Получить список запусков дага.

        Аргументы:
            state (List[DagState] | None, optional): список кодов состояния запусков дага. По умолчанию None.

        Возвращает:
            List[DagRun] | None: список запусков дага или None в случае ошибки
        """

    @catch_airflow_errors
    def get_dag_runs_batch(
        self, dag_ids: list[str] | None = ..., limit: int = ..., offset: int = ...
    ) -> tuple[DagRuns | None, int]:
        """Получить список запусков дага по нескольким dag_id.

        Аргументы:
            dag_ids (List[str] | None, optional): список идентификаторов дагов. По умолчанию None.

        Возвращает:
            DagRuns | None: список запусков дага или None в случае ошибки
        """

    @catch_airflow_errors
    def get_last_dag_run(self, username: str | None = ...) -> tuple[DagRun | None, int]:
        """Получить список запусков дага.

        Аргументы:
            username (Optional[str], optional): Имя пользователя системы, для которого нужно получить последний \
            запуск дага. По умолчанию None.

        Возвращает:
            List[DagRun] | None: список запусков дага или None в случае ошибки
        """

    @catch_airflow_errors
    def get_current_dag_run(self) -> tuple[DagRun | None, int]:
        """Получить текущий запуск дага.

        Возвращает:
            DagRun | None: объект текущего запуска дага или None в случае ошибки
        """

    @catch_airflow_errors
    def trigger(self, conf: dict[str, Any] | None = ...) -> tuple[DagRun | None, int]:
        """Запустить даг.

        Аргументы:
            conf (dict[str, Any], {}): параметры запуска дага. По умолчанию {}.

        Возвращает:
            DagRun | None: объект нового запуска дага или None в случае ошибки
        """

    @catch_airflow_errors
    def stop(self) -> tuple[DagRun | None, int]:
        """Остановить выполнение запущенного дага.

        Возвращает:
            DagRun | None: объект остановленного дага или None в случае ошибки
        """

    @catch_airflow_errors
    def clear(self) -> tuple[DagRun | None, int]:
        """Очистить все экземпляры задач текущего запуска дага.

        Возвращает:
            DagRun | None: объект очищенного запуска дага или None в случае ошибки
        """

    @catch_airflow_errors
    def get_task_instances(self) -> tuple[TaskInstances | None, int]:
        """Получить все экземпляры задач текущего запуска дага.

        Возвращает:
            TaskInstances | None: список экземпляров задач текущего запуска дага или None в случае ошибки
        """

    @catch_airflow_errors
    def get_task_instance(self, task_id: str) -> tuple[TaskInstance | None, int]:
        """Получить все экземпляры задач текущего запуска дага.

        Аргументы:
            task_id (str): идентификатор задачи дага

        Возвращает:
            TaskInstance | None: экземпляр задачи текущего запуска дага или None в случае ошибки
        """

    @catch_airflow_errors
    def get_logs(self, task_id: str, try_num: int, continuation_token: str | None = ...) -> tuple[Logs | None, int]:
        """Получить логи экземпляра задачи текущего запуска дага.

        Аргументы:
            task_id (str): идентификатор задачи дага
            try_num (int): номер попытки выполнения задачи
            continuation_token (str | None, optional): токен для слежения за логами. По умолчанию None.

        Returns:
            Logs | None: логи экземпляра задачи текущего запуска дага или None в случае ошибки

        """
