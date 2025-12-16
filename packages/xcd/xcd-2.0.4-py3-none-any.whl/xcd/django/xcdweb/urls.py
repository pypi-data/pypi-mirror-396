from django.contrib import admin
from django.urls import path
from xcd.django import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('load_options/', views.load_case_and_expert_options, name='load_options'),
    path("download_xml/",views.download_xml, name="download_xml"),
]