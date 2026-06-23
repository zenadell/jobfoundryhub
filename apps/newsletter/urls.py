from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('trigger-daily-automation/<str:secret_token>/', views.trigger_daily_newsletter, name='trigger_daily'),
]
