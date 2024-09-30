from django.urls import path

from web_blog import views
from django.conf.urls import include

urlpatterns = [
    path('login/',views.login,name='login'),
]