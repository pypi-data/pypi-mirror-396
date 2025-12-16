import base64
import codecs
import logging
from collections import deque
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime
from functools import wraps
from socket import timeout
from typing import Any, Concatenate, Literal
from urllib import request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlunparse

import requests
import urllib3
from pydantic import BaseModel
from pydantic.alias_generators import to_camel

from yarik_django_airflow_api_manager.conf.settings import (
    AIRFLOW_BASE_URL,
    AIRFLOW_HOST,
    AIRFLOW_PORT,
    AIRFLOW_PSWD,
    AIRFLOW_USER,
)

logger = logging.getLogger(__name__)

AIRFLOW_AUTH = (AIRFLOW_USER, AIRFLOW_PSWD)

URL_SCHEME = "http"
URL_NETLOC = f"{AIRFLOW_HOST}:{AIRFLOW_PORT}"
URL_PATH = f"{AIRFLOW_BASE_URL}/api/v1/"


HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
CONN_TIMEOUT = 10

COMMON_REQUEST_PARAMS: dict[str, Any] = {
    "headers": HEADERS,
    "auth": AIRFLOW_AUTH,
    "timeout": CONN_TIMEOUT,
}


class Components(BaseModel):
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str

    @property
    def components(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            self.query,
            self.fragment,
        )


type RunType = Literal["backfill", "manual", "scheduled", "dataset_triggered"]
type DagState = Literal["queued", "running", "success", "failed"]
type TaskState = Literal[
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
type TriggerRule = Literal[
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
        alias_generator = to_camel
        populate_by_name = True


class SLAMiss(BaseModel):
    task_id: str
    dag_id: str
    execution_date: datetime
    email_sent: bool
    timestamp: datetime
    description: str | None = None
    notification_sent: bool


class Trigger(BaseModel):
    id: int
    classpath: str
    kwargs: str
    created_date: datetime
    trigger_id: int | None = None


class Job(BaseModel):
    id: int
    dag_id: str | None = None
    state: str | None = None
    job_type: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    latest_heartbeat: datetime | None = None
    executor_class: str | None = None
    hostname: str | None = None
    unixname: str | None = None


class Tag(BaseModel):
    name: str


class Dag(ModelWithAliasGenerator):
    dag_id: str
    root_dag_id: str | None = None
    is_paused: bool | None = None
    is_active: bool | None = None
    is_subdag: bool
    last_parsed_time: datetime | None = None
    last_pickled: datetime | None = None
    last_expired: datetime | None = None
    scheduler_lock: bool | None = None
    pickle_id: str | None = None
    default_view: str | None = None
    fileloc: str
    file_token: str
    owners: list[str]
    description: str | None = None
    schedule_interval: Any | None = None
    timetable_description: str | None = None
    tags: list[Tag] | None = None
    max_active_tasks: int | None = None
    max_active_runs: int | None = None
    has_task_concurrency_limits: bool | None = None
    has_import_errors: bool | None = None
    next_dagrun: datetime | None = None
    next_dagrun_data_interval_start: datetime | None = None
    next_dagrun_data_interval_end: datetime | None = None
    next_dagrun_create_after: datetime | None = None
    max_consecutive_failed_dag_runs: int | None = None


class Dags(ModelWithAliasGenerator):
    dags: list[Dag]
    total_entries: int


class DagRun(ModelWithAliasGenerator):
    dag_id: str
    dag_run_id: str | None = None
    logical_date: datetime | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    data_interval_start: datetime | None = None
    data_interval_end: datetime | None = None
    last_scheduling_decision: datetime | None = None
    run_type: RunType
    state: DagState
    external_trigger: bool
    conf: dict[str, Any]
    note: str | None = None


class DagRuns(ModelWithAliasGenerator):
    dag_runs: list[DagRun]
    total_entries: int


class Task(ModelWithAliasGenerator):
    class_ref: Any
    task_id: str
    owner: str
    start_date: datetime
    end_date: datetime | None = None
    trigger_rule: TriggerRule
    extra_links: list[Any]
    depends_on_past: bool
    is_mapped: bool
    wait_for_downstream: bool
    retries: int
    queue: str | None = None
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
    sub_dag: Dag | None = None
    downstream_task_ids: list[str]


class Tasks(ModelWithAliasGenerator):
    tasks: list[Task]


class TaskInstance(ModelWithAliasGenerator):
    task_id: str
    dag_id: str
    dag_run_id: str
    execution_date: datetime
    start_date: datetime | None = None
    end_date: datetime | None = None
    duration: float | None = None
    state: TaskState | None = None
    try_number: int
    map_index: int
    max_tries: int
    hostname: str
    unixname: str
    pool: str
    pool_slots: int
    queue: str | None
    priority_weight: int | None = None
    operator: str | None = None
    queued_when: str | None = None
    pid: int | None = None
    executor_config: str
    sla_miss: SLAMiss | None = None
    rendered_fields: dict[str, Any]
    trigger: Trigger | None = None
    triggerer_job: Job | None = None
    note: str | None = None


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
    detail: str | None = None
    instance: str | None = None


def catch_airflow_errors[**P, R](
    func: Callable[Concatenate[P], tuple[R | None, int]],
) -> Callable[Concatenate[P], tuple[R | None, int]]:
    """Декоратор перехватывает все исключения при работе с Airflow и логирует причину ошибки.

    Returns:
        out: `Any | None`
            Возвращаемое значение оборачиваемой функции или None в случае ошибки.

    """  # noqa: RUF002

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[R | None, int]:
        try:
            return func(*args, **kwargs)
        except ConnectionError:
            logger.exception("Ошибка соединения с Airflow")  # noqa: RUF001
            return (None, 503)
        except URLError as e:
            if isinstance(e.reason, timeout):
                logger.exception("Превышено время ожидания ответа от Airflow %s", e.reason)
            else:
                logger.exception("Не удаётся разрешить URL Airflow {e.reason}")  # noqa: RUF001
            logger.debug(e)
            return (None, 503)
        except requests.Timeout:
            logger.exception("Ошибка при выполнении запроса к Airflow: превышено время ожидания запроса")
            return (None, 503)
        except urllib3.exceptions.MaxRetryError as e:
            logger.exception(
                "Ошибка при выполнении запроса к Airflow, достигнуто максимальное число попыток: %s", e.args
            )
            return (None, 503)
        except requests.RequestException as e:
            status = 503
            if isinstance(e.args[0], ErrorResponce):
                logger.exception(
                    "Ошибка при выполнении запроса к Airflow, причина: %d %s. %s",
                    e.args[0].status,
                    e.args[0].title,
                    e.args[0].type,
                )
                status = e.args[0].status
            else:
                logger.exception("Ошибка при выполнении запроса к Airflow: %s", e.args)
            return (None, status)
        except Exception as e:
            logger.exception("Неизвестная ошибка при работе менеджера соединений Airflow API %s", e.args)
            logger.debug(e)
            return (None, 500)

    return wrapper


def get_request(url: str) -> requests.Response:
    responce = requests.get(url, **COMMON_REQUEST_PARAMS)  # noqa: S113  - таймаут задаётся при распаковке COMMON_REQUEST_PARAMS

    if responce.status_code == requests.codes["ok"]:
        return responce
    raise requests.RequestException(ErrorResponce(**responce.json()))


def post_request(url: str, payload: Any | None = None) -> requests.Response:  # noqa: ANN401
    responce = requests.post(url, json=payload, **COMMON_REQUEST_PARAMS)  # noqa: S113 - таймаут задаётся при распаковке COMMON_REQUEST_PARAMS

    if responce.status_code == requests.codes["ok"]:
        return responce
    raise requests.RequestException(ErrorResponce(**responce.json()))


def patch_request(url: str, payload: Any | None = None) -> requests.Response:  # noqa: ANN401
    responce = requests.patch(url, json=payload, **COMMON_REQUEST_PARAMS)  # noqa: S113  - таймаут задаётся при распаковке COMMON_REQUEST_PARAMS

    if responce.status_code == requests.codes["ok"]:
        return responce
    raise requests.RequestException(ErrorResponce(**responce.json()))


class AirflowManager:
    """Интерфейс для работы с Airflow."""  # noqa: RUF002

    def __init__(self, dag_id: str | None = None, dag_run_id: str | None = None) -> None:
        """Инициализация экземпляра интерфейса для работы с Airflow.

        Args:
            dag_id (Optional[str], optional): идентификатор дага. По умолчанию None.
            dag_run_id (Optional[str], optional): идентификатор запуска дага. По умолчанию None.

        """  # noqa: RUF002
        self.url = Components(
            scheme=URL_SCHEME,
            netloc=URL_NETLOC,
            path=AIRFLOW_BASE_URL,
            params="",
            query="",
            fragment="",
        )
        self.url.path = URL_PATH
        self.dag_id = dag_id
        self.dag_run_id = dag_run_id

    def _check_connection(self) -> None:
        url = Components(
            scheme=URL_SCHEME,
            netloc=URL_NETLOC,
            path=AIRFLOW_BASE_URL,
            params="",
            query="",
            fragment="",
        )
        # Проверка соединения
        logger.debug(urlunparse(url.components))
        url = urlunparse(url.components)
        if not url.lower().startswith(("http", "https")):
            msg = "URL должен начинаться с 'http:' or 'https:'"  # noqa: RUF001
            raise ValueError(msg)
        with request.urlopen(url, timeout=CONN_TIMEOUT):  # noqa: S310 - обработано выше
            pass

    def _check_creds(self) -> None:
        url = deepcopy(self.url)
        url.path += "dags?limit=0"
        url_str = urlunparse(url.components)
        if not url_str.lower().startswith(("http", "https")):
            msg = "URL должен начинаться с 'http:' or 'https:'"  # noqa: RUF001
            raise ValueError(msg)
        req = request.Request(url_str)  # noqa: S310  - обработано выше
        base64string = base64.b64encode(bytes("{}:{}".format(*AIRFLOW_AUTH), "ascii"))
        req.add_header("Authorization", "Basic {}".format(base64string.decode("utf-8")))
        with request.urlopen(req, timeout=CONN_TIMEOUT):  # noqa: S310  - обработано выше
            pass

    def conn_good(self) -> bool:
        """Проверяет соединение с Airflow.

        Возвращает:
            bool: доступность Airflow
        """  # noqa: RUF002
        try:
            self._check_connection()
        except ConnectionError:
            logger.exception("Ошибка соединения с Airflow")  # noqa: RUF001
            return False
        except URLError as e:
            if isinstance(e.reason, timeout):
                logger.exception("Превышено время ожидания ответа от Airflow %s", e.reason)
            else:
                logger.exception("Не удаётся разрешить URL Airflow %s", e.reason)  # noqa: RUF001
            logger.debug(e)
            return False
        except TimeoutError:
            logger.exception("Превышено время ожидания ответа от Airflow")
            return False
        except Exception as e:
            logger.exception("Неизвестная ошибка при проверке соединения с Airflow %s", e.args)  # noqa: RUF001
            logger.debug(e)
            return False
        return True

    def creds_is_valid(self) -> bool:
        """Проверяет корректность учетных данных пользователя API.

        Returns:
            bool: корректность учетных данных

        """
        try:
            self._check_creds()
        except HTTPError:
            logger.exception("Учётные данные пользователя Airflow API некорректны")
            return False
        except URLError as e:
            if isinstance(e.reason, timeout):
                logger.exception("Превышено время ожидания ответа от Airflow %s", e.reason)
            else:
                logger.exception("Не удаётся разрешить URL Airflow %s", e.reason)  # noqa: RUF001
            logger.debug(e)
            return False
        except Exception as e:
            logger.exception("Не удалось проверить учетные данные пользователя Airflow API %s", e.args)  # noqa: RUF001
            logger.debug(e)
            return False
        return True

    @catch_airflow_errors
    def get_dag(self) -> tuple[Dag | None, int]:
        """Получить даг.

        Возвращает:
            Dag | None: объект дага или None в случае ошибки
        """
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}"

        return (Dag(**(get_request(urlunparse(url.components)).json())), 200)

    @catch_airflow_errors
    def get_dags_dict(
        self,
        tags: list[str] | None = None,
        dag_id_pattern: str = "",
        only_active: bool = True,
        limit: int = 100,
        offset: int = 0,
        fields: list[str] | None = None,
    ) -> tuple[dict[str, Any] | None, int]:
        """Получить даги в формате словаря.

        Возвращает:
            dict | None: словарь дага или None в случае ошибки
        """
        if tags is None:
            tags = []
        url = deepcopy(self.url)
        query_dict: dict[str, Any] = {
            "tags": ",".join(tags) if len(tags) > 0 else None,
            "dag_id_pattern": dag_id_pattern if len(dag_id_pattern) > 0 else "",
            "only_active": only_active,
            "limit": limit,
            "offset": offset,
        }
        if fields:
            query_dict["fields"] = fields
        url.query = urlencode(query_dict)

        url.path += "dags"
        return (get_request(urlunparse(url.components)).json(), 200)

    @catch_airflow_errors
    def get_dags(
        self,
        tags: list[str] | None = None,
        dag_id_pattern: str = "",
        only_active: bool = True,
        limit: int = 100,
        offset: int = 0,
        fields: list[str] | None = None,
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
        if tags is None:
            tags = []
        dct, status = self.get_dags_dict(tags, dag_id_pattern, only_active, limit, offset, fields)
        if not dct:
            return (None, status)
        return (Dags(**dct), 200)

    @catch_airflow_errors
    def get_dags_count(
        self,
        tags: list[str] | None = None,
        dag_id_pattern: str = "",
        only_active: bool = True,
    ) -> tuple[int, int]:
        """Получить количество дагов.

        Аргументы:
            tags (list[str], optional): список тегов дага. По умолчанию [].
            dag_id_pattern (str, optional): паттерн идентификатора дага. По умолчанию "".
            only_active (bool, optional): учитывать только активные даги. По умолчанию True.

        Возвращает:
            int: количество дагов
        """
        if tags is None:
            tags = []
        dct, status = self.get_dags_dict(tags, dag_id_pattern, only_active, 1, 0)
        if not dct:
            return (0, status)
        dags = Dags(**dct)
        return (dags.total_entries if dags else 0, status)

    @catch_airflow_errors
    def get_dag_runs(self, states: list[DagState] | None = None) -> tuple[list[DagRun] | None, int]:
        """Получить список запусков дага.

        Аргументы:
            state (List[DagState] | None, optional): список кодов состояния запусков дага. По умолчанию None.

        Возвращает:
            List[DagRun] | None: список запусков дага или None в случае ошибки
        """
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns"
        query: dict[str, Any] = {"limit": 100, "order_by": "-execution_date"}
        if states and len(states) > 0:
            query["state"] = ",".join(states)

        url.query = urlencode(query)

        dag_runs = DagRuns(**(get_request(urlunparse(url.components)).json()))

        return (dag_runs.dag_runs, 200)

    @catch_airflow_errors
    def get_dag_runs_batch(
        self,
        dag_ids: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[DagRuns | None, int]:
        """Получить список запусков дага по нескольким dag_id.

        Аргументы:
            dag_ids (List[str] | None, optional): список идентификаторов дагов. По умолчанию None.

        Возвращает:
            DagRuns | None: список запусков дага или None в случае ошибки
        """
        url = deepcopy(self.url)
        url.path += "dags/~/dagRuns/list"
        payload: dict[str, Any] = {
            "dag_ids": dag_ids,
            "limit": limit,
            "offset": offset,
        }

        return (DagRuns(**(post_request(urlunparse(url.components), payload=payload).json())), 200)

    @catch_airflow_errors
    def get_last_dag_run(self, username: str | None = None) -> tuple[DagRun | None, int]:
        """Получить список запусков дага.

        Аргументы:
            username (Optional[str], optional): Имя пользователя системы, для которого нужно получить последний \
            запуск дага. По умолчанию None.

        Возвращает:
            List[DagRun] | None: список запусков дага или None в случае ошибки
        """
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns"

        dag_run = None
        if username:
            url.query = urlencode({"limit": 10, "order_by": "-execution_date"})
            dag_runs = DagRuns(**(get_request(urlunparse(url.components)).json()))

            dag_run = next(
                (d for d in dag_runs.dag_runs if "run_username" in d.conf and d.conf["run_username"] == username),
                None,
            )
            if not dag_run:
                for offset in range(10, dag_runs.total_entries, 10):
                    url.query = urlencode({"limit": 10, "offset": offset, "order_by": "-execution_date"})
                    dag_runs = DagRuns(**(get_request(urlunparse(url.components)).json())).dag_runs
                    dag_run = next(
                        (d for d in dag_runs if "run_username" in d.conf and d.conf["run_username"] == username),
                        None,
                    )
                    if dag_run:
                        break

        else:
            url.query = urlencode({"limit": 1, "order_by": "-execution_date"})
            dag_runs = DagRuns(**(get_request(urlunparse(url.components)).json())).dag_runs
            if len(dag_runs) > 0:
                dag_run = dag_runs[0]

        if dag_run:
            self.dag_run_id = dag_run.dag_run_id

        return (dag_run, 200 if dag_run else 404)

    @catch_airflow_errors
    def get_current_dag_run(self) -> tuple[DagRun | None, int]:
        """Получить текущий запуск дага.

        Возвращает:
            DagRun | None: объект текущего запуска дага или None в случае ошибки
        """
        if self.dag_run_id is None:
            return (None, 404)

        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}"

        return (DagRun(**(get_request(urlunparse(url.components)).json())), 200)

    @catch_airflow_errors
    def trigger(self, conf: dict[str, Any] | None = None) -> tuple[DagRun | None, int]:
        """Запустить даг.

        Аргументы:
            conf (dict[str, Any], {}): параметры запуска дага. По умолчанию {}.

        Возвращает:
            DagRun | None: объект нового запуска дага или None в случае ошибки
        """
        if conf is None:
            conf = {}
        payload = {
            "conf": conf,
        }
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns"

        dag_run = DagRun(**(post_request(urlunparse(url.components), payload=payload).json()))

        self.dag_run_id = dag_run.dag_run_id

        return (dag_run, 200)

    @catch_airflow_errors
    def stop(self) -> tuple[DagRun | None, int]:
        """Остановить выполнение запущенного дага.

        Возвращает:
            DagRun | None: объект остановленного дага или None в случае ошибки
        """
        payload = {
            "state": "failed",
        }
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}"

        return (DagRun(**(patch_request(urlunparse(url.components), payload=payload).json())), 200)

    @catch_airflow_errors
    def clear(self) -> tuple[DagRun | None, int]:
        """Очистить все экземпляры задач текущего запуска дага.

        Возвращает:
            DagRun | None: объект очищенного запуска дага или None в случае ошибки
        """
        payload = {
            "dry_run": False,
        }
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}/clear"

        return (DagRun(**(post_request(urlunparse(url.components), payload=payload).json())), 200)

    @catch_airflow_errors
    def get_task_instances(self) -> tuple[TaskInstances | None, int]:
        """Получить все экземпляры задач текущего запуска дага.

        Возвращает:
            TaskInstances | None: список экземпляров задач текущего запуска дага или None в случае ошибки
        """
        if self.dag_run_id is None:
            return (None, 404)

        # Упорядочить задачи, топологическая сортировка Кана
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/tasks"

        dag_tasks = Tasks(**(get_request(urlunparse(url.components)).json())).tasks

        graph: dict[str, list[str]] = {}
        indegree: dict[str, int] = {}

        for task in dag_tasks:
            task_id = task.task_id
            graph[task_id] = task.downstream_task_ids
            indegree[task_id] = 0

        for downstreams in graph.values():
            for down in downstreams:
                indegree[down] += 1

        queue = deque([task_id for task_id in indegree if indegree[task_id] == 0])
        topological_order: list[str] = []

        while queue:
            task_id = queue.popleft()
            topological_order.append(task_id)
            for down in graph[task_id]:
                indegree[down] -= 1
                if indegree[down] == 0:
                    queue.append(down)

        # Получить экземпляры задач
        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}/taskInstances"

        task_instances = TaskInstances(**(get_request(urlunparse(url.components)).json()))

        task_instances.task_instances.sort(key=lambda ti: topological_order.index(ti.task_id))

        return (task_instances, 200)

    @catch_airflow_errors
    def get_task_instance(self, task_id: str) -> tuple[TaskInstance | None, int]:
        """Получить все экземпляры задач текущего запуска дага.

        Аргументы:
            task_id (str): идентификатор задачи дага

        Возвращает:
            TaskInstance | None: экземпляр задачи текущего запуска дага или None в случае ошибки
        """
        if self.dag_run_id is None:
            return (None, 404)

        url = deepcopy(self.url)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}/taskInstances/{task_id}"

        return (TaskInstance(**(get_request(urlunparse(url.components)).json())), 200)

    @catch_airflow_errors
    def get_logs(self, task_id: str, try_num: int, continuation_token: str | None = None) -> tuple[Logs | None, int]:
        """Получить логи экземпляра задачи текущего запуска дага.

        Аргументы:
            task_id (str): идентификатор задачи дага
            try_num (int): номер попытки выполнения задачи
            continuation_token (str | None, optional): токен для слежения за логами. По умолчанию None.

        Returns:
            Logs | None: логи экземпляра задачи текущего запуска дага или None в случае ошибки

        """
        if self.dag_run_id is None:
            return (None, 404)

        url = deepcopy(self.url)
        query: dict[str, Any] = {"full_content": continuation_token is None}
        if continuation_token is not None:
            query["token"] = continuation_token
        url.query = urlencode(query)
        url.path += f"dags/{self.dag_id}/dagRuns/{self.dag_run_id}/taskInstances/{task_id}/logs/{try_num}"

        logs = Logs(**(get_request(urlunparse(url.components)).json()))

        escape_decoded = codecs.escape_decode(bytes(logs.content, "utf-8"))[0]
        if not isinstance(escape_decoded, bytes):
            return (None, 404)

        logs.content = escape_decoded.decode("utf-8")

        ws_index = logs.content.find(" ")
        first_quot_pos = ws_index + 1
        second_quot_pos = logs.content.rfind("'") if logs.content[first_quot_pos] == "'" else logs.content.rfind('"')

        logs.content = logs.content[first_quot_pos + 1 : second_quot_pos]

        return (logs, 200)
