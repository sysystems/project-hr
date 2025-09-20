from django.urls import path
from . import views

urlpatterns = [
    # 기존 URL들...
    path('api/org/action/<str:action>/', views.org_action_api, name='org_action_api'),
]