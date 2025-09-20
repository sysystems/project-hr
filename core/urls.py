from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('org_chart/', views.org_chart, name='org_chart'),
]
