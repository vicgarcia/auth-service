from django.urls import path, include
from django.conf.urls import url
from core import views as core_views
from account import views as account_views
from tokens import views as tokens_views
from admin import views as admin_views


urlpatterns = [

    # status check endpoint
    path('status/', core_views.StatusView.as_view()),

    # account management routes
    path('account/signup/', account_views.SignupView.as_view()),
    path('account/manage/', account_views.ManageView.as_view()),
    path('account/verify/', account_views.VerifyView.as_view()),
    path('account/reset/', account_views.ResetView.as_view()),

    # auth token routes
    path('token/login/', tokens_views.LoginView.as_view()),
    path('token/refresh/', tokens_views.RefreshView.as_view()),
    path('token/revoke/', tokens_views.RevokeView.as_view()),
    path('token/inspect/', tokens_views.InspectView.as_view()),

    # admin management apis
    url(r'^users/', include(admin_views.user_router.urls)),
    url(r'^tokens/', include(admin_views.token_router.urls)),

]
