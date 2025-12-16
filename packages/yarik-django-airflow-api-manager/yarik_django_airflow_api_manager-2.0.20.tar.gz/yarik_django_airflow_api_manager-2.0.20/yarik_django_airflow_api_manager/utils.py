import logging
from collections.abc import Callable
from functools import wraps
from typing import Concatenate

from django.http import HttpRequest, JsonResponse, QueryDict

logger = logging.getLogger(__name__)


def ajax_login_required[**P, R](
    view_func: Callable[Concatenate[HttpRequest, P], R],
) -> Callable[Concatenate[HttpRequest, P], R | JsonResponse]:
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: P.args, **kwargs: P.kwargs) -> R | JsonResponse:
        if not request.user.is_authenticated:
            logger.warning("Попытка неавторизованного доступа: запрос отклонён.", request.user)
            return JsonResponse({"msg": "Unauthorized"}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper


def get_from_querydict(qd: QueryDict, key: str) -> str | None:
    val = qd.get(key)
    if val in ["undefined", "null"]:
        val = None
    return val
