from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='index'),
    path('send/', views.send_message_view, name='send_message'),
]
