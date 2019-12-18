from django.urls import path, include
from django.conf.urls import url
from core import views as core_views


urlpatterns = [

    # status check endpoint
    path('status/', core_views.StatusView.as_view()),

]
