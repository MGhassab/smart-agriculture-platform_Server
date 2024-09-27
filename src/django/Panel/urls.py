from django.urls import path, include
from . import views
from rest_framework import routers


urlpatterns = [
    path('', views.IndexPageView.as_view(), name='panel'),
    # path('', view.PanelView.as_view(), name='Panel'),

    path('log-in/', views.LogInView.as_view(), name='log_in'),
    path('503_blank/', views.BlankView.as_view(), name='503_blank'),
    path('log-out/', views.LogOutView.as_view(), name='log_out'),
    path('sensorconditions/', views.SensorsLastValuesView.as_view(), name='sensorconditions'),
    # path('log-out/', LogOutView.as_view(), name='log_out'),

    # path('sign-up/', SignUpView.as_view(), name='sign_up'),

    # path('activate/<code>/', ActivateView.as_view(), name='activate'),
    # path('resend/activation-code/', ResendActivationCodeView.as_view(), name='resend_activation_code'),

    # path('restore/password/', RestorePasswordView.as_view(), name='restore_password'),
    # path('restore/password/done/', RestorePasswordDoneView.as_view(), name='restore_password_done'),
    # path('restore/<uidb64>/<token>/', RestorePasswordConfirmView.as_view(), name='restore_password_confirm'),

    # path('remind/username/', RemindUsernameView.as_view(), name='remind_username'),

    # path('change/profile/', ChangeProfileView.as_view(), name='change_profile'),
    # path('change/password/', ChangePasswordView.as_view(), name='change_password'),
    # path('change/email/', ChangeEmailView.as_view(), name='change_email'),
    # path('change/email/<code>/', ChangeEmailActivateView.as_view(), name='change_email_activation'),

]