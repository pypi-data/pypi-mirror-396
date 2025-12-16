import logging

from asgiref.sync import sync_to_async
from django.http import HttpRequest, JsonResponse

from .utils import ajax_login_required
from .view_handlers import check_connection, dag, dag_run, ti_logs

logger = logging.getLogger(__name__)


@sync_to_async
@ajax_login_required
def check_connection_async(request: HttpRequest) -> JsonResponse:
    return check_connection(request)


@sync_to_async
@ajax_login_required
def dag_async(request: HttpRequest) -> JsonResponse:
    return dag(request)


@sync_to_async
@ajax_login_required
def dag_run_async(request: HttpRequest) -> JsonResponse:
    return dag_run(request)


@sync_to_async
@ajax_login_required
def ti_logs_async(request: HttpRequest) -> JsonResponse:
    return ti_logs(request)
