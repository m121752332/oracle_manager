from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.index,          name='index'),
    path('api/connect/',        views.api_connect,    name='api_connect'),
    path('api/disconnect/',     views.api_disconnect, name='api_disconnect'),
    path('api/locks/',          views.api_locks,      name='api_locks'),
    path('api/kill-session/',   views.api_kill_session,  name='api_kill_session'),
    path('api/kill-process/',   views.api_kill_process,  name='api_kill_process'),
]
