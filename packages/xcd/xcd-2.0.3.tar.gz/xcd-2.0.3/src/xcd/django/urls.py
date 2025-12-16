from django.urls import path
from . import views

app_name = 'xcd'
urlpatterns = [
    path("", views.index, name="index"),
    path("load_options/", views.load_case_and_expert_options, name="load_options"),
    path("download_xml/",views.download_xml, name="download_xml"),
    path("start_report/", views.start_report, name="start_report"),
    path("progress/<str:job_id>/", views.progress, name="progress"),
    path("download_report/<str:job_id>/", views.download_report, name="download_report"),

]