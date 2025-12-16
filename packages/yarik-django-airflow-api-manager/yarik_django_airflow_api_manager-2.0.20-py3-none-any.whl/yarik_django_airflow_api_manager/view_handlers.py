import json
import logging

from django.contrib.auth.models import User
from django.http import HttpRequest, JsonResponse

from .airflow_api_manager import AirflowManager
from .utils import get_from_querydict

logger = logging.getLogger(__name__)


def check_connection(_: HttpRequest) -> JsonResponse:
    am = AirflowManager()
    if not am.conn_good():
        return JsonResponse({"title": "Не удалось установить соединение с Airflow"}, status=503)  # noqa: RUF001

    if not am.creds_is_valid():
        return JsonResponse({"title": "Ошибка авторизации Airflow API"}, status=401)

    return JsonResponse({}, status=200)


def dag(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        return JsonResponse({"msg": "Метод не разрешён"}, status=405)

    dag_id = get_from_querydict(request.GET, "dag_id")
    if dag_id is None:
        return JsonResponse({"msg": "dag_id не предоставлен"}, status=400)

    dag, status = AirflowManager(dag_id=dag_id).get_dag()

    if not dag:
        return JsonResponse({"msg": "Даг не найден"}, status=status)

    return JsonResponse({"dag": dag.model_dump(by_alias=True)}, status=status)


def dag_run(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        return _dag_run_post(request)

    by_user = request.GET.get("by_user", "false") == "true"

    dag_id = get_from_querydict(request.GET, "dag_id")
    if dag_id is None:
        return JsonResponse({}, status=400)

    dag_run_id = get_from_querydict(request.GET, "dag_run_id")

    airflow_manager = AirflowManager(dag_id=dag_id)

    dag_run = None
    if dag_run_id is None:
        username = None
        if by_user and isinstance(request.user, User):
            username = request.user.username
        dag_run, status = airflow_manager.get_last_dag_run(username=username)
    else:
        airflow_manager.dag_run_id = dag_run_id
        dag_run, status = airflow_manager.get_current_dag_run()

    logger.debug("dag_run=%s", dag_run)
    if not dag_run:
        return JsonResponse({"msg": "Запуск дага не найден"}, status=status)

    task_instances, status = airflow_manager.get_task_instances()

    if not task_instances:
        return JsonResponse({"msg": "Экземпляры задач не найдены"}, status=status)

    return JsonResponse(
        {
            "dagRun": (dag_run.model_dump(by_alias=True)),
            "taskInstances": (task_instances.model_dump(by_alias=True)),
        },
        status=status,
    )


def _dag_run_post(request: HttpRequest) -> JsonResponse:
    action = json.loads(request.body.decode("utf-8")).get("action")
    if action not in ["start", "restart", "stop"]:
        JsonResponse({"msg": f"Действие {action} не реализовано, доступные действия: start, restart, stop"}, status=400)

    dag_id = json.loads(request.body.decode("utf-8")).get("dag_id")
    if dag_id is None:
        return JsonResponse({"msg": "dag_id не предоставлен"}, status=400)

    dag_run_id = json.loads(request.body.decode("utf-8")).get("dag_run_id")
    if action != "start" and dag_run_id is None:
        return JsonResponse({"msg": "dag_run_id не предоставлен"}, status=400)

    dag_run = None
    task_instances = None
    airflow_manager = AirflowManager(dag_id=dag_id)

    if action == "start":
        conf = json.loads(request.body.decode("utf-8")).get("conf")
        if conf is not None and "run_username" not in conf:
            conf["run_username"] = request.user.username
        dag_run, status = airflow_manager.trigger(conf=conf)
    elif action == "restart":
        airflow_manager.dag_run_id = dag_run_id
        dag_run, status = airflow_manager.clear()
    else:
        airflow_manager.dag_run_id = dag_run_id
        dag_run, status = airflow_manager.stop()

    if not dag_run:
        logger.error("Не удалось выполнить действие %s с дагом %s", action, dag_id)  # noqa: RUF001
        return JsonResponse({"title": "Ошибка при выполнении операции с дагом"}, status=status)  # noqa: RUF001

    task_instances, status = airflow_manager.get_task_instances()
    if not task_instances:
        logger.warning(
            "Не удалось получить список экземпляров задач дага %s для запуска %s",  # noqa: RUF001
            dag_id,
            dag_run.dag_run_id,
        )

    return JsonResponse(
        {
            "dagRun": dag_run.model_dump(by_alias=True) if dag_run else None,
            "taskInstances": (task_instances.model_dump(by_alias=True) if task_instances else None),
        },
        status=status,
    )


def ti_logs(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        return JsonResponse({"msg": "Метод не разрешён"}, status=405)

    dag_id = get_from_querydict(request.GET, "dag_id")
    if dag_id is None:
        return JsonResponse({"msg": "dag_id не предоставлен"}, status=400)

    dag_run_id = get_from_querydict(request.GET, "dag_run_id")
    if dag_run_id is None:
        return JsonResponse({"msg": "dag_run_id не предоставлен"}, status=400)

    task_id = get_from_querydict(request.GET, "task_id")
    if task_id is None:
        return JsonResponse({"msg": "task_id не предоставлен"}, status=400)

    try_num = get_from_querydict(request.GET, "try_num")
    if try_num is None or not try_num.isdigit():
        try_num = "1"
    try_num = int(try_num)

    continuation_token = get_from_querydict(request.GET, "continuation_token")

    airflow_manager = AirflowManager(dag_id=dag_id, dag_run_id=dag_run_id)

    logs, status = airflow_manager.get_logs(task_id=task_id, try_num=try_num, continuation_token=continuation_token)

    if not logs:
        logger.error("Не удалось получить логи для дага %s и запуска %s", dag_id, dag_run_id)  # noqa: RUF001
        return JsonResponse({"title": "Ошибка при получении логов"}, status=status)

    return JsonResponse({"logs": logs.model_dump(by_alias=True)}, status=status)
