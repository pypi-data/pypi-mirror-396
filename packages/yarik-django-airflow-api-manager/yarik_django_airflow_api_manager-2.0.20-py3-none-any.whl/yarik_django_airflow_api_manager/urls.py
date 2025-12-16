from django.urls import path

from . import views

app_name = "yarik_django_airflow_api_manager"

urlpatterns = [
    path("check_connection", views.check_connection_async, name="check_connection"),
    path("dag", views.dag_async, name="dag"),
    path("dag_run", views.dag_run_async, name="dag_run"),
    path("ti_logs", views.ti_logs_async, name="ti_logs"),
]
