from django.urls import path, include
from django.conf.urls import url
from core import views as core_views
from tokens import views as tokens_views


urlpatterns = [

    # status check endpoint
    path('status/', core_views.StatusView.as_view()),

    # auth token routes
    path('token/login/', tokens_views.LoginView.as_view()),
    path('token/refresh/', tokens_views.RefreshView.as_view()),
    path('token/revoke/', tokens_views.RevokeView.as_view()),
    path('token/inspect/', tokens_views.InspectView.as_view()),

]
