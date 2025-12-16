from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

VERSION_TAG = settings.VERSION_TAG or "NO_VERSION_TAG"

AIRFLOW_HOST = settings.AIRFLOW_HOST
AIRFLOW_PORT = settings.AIRFLOW_PORT
AIRFLOW_USER = settings.AIRFLOW_USER
AIRFLOW_PSWD = settings.AIRFLOW_PSWD
AIRFLOW_BASE_URL = settings.AIRFLOW_BASE_URL


if (
    AIRFLOW_HOST is None
    or AIRFLOW_PORT is None
    or AIRFLOW_USER is None
    or AIRFLOW_PSWD is None
    or AIRFLOW_BASE_URL is None
):
    msg = (
        "Could not find one of AIRFLOW_HOST, AIRFLOW_PORT, AIRFLOW_USER, AIRFLOW_PSWD, AIRFLOW_BASE_URL in environment"
    )
    raise ImproperlyConfigured(msg)
