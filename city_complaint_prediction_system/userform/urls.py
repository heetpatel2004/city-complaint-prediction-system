# userform/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views

app_name = "userform"

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('complaint/', views.submit_complaint, name='submit_complaint'),
    path('track/', views.track_complaint, name='track_complaint'),
    path('logout/', views.user_logout, name='logout'),
    path('about/', views.about_us, name='about_us'),
    # admin section
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='userform/password_reset_form.html',        # ← slash not colon
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('userform:password_reset_done'),
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='userform/password_reset_done.html',   # ← slash not colon
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='userform/password_reset_confirm.html', # ← slash not colon
            success_url=reverse_lazy('userform:password_reset_complete'),
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='userform/password_reset_complete.html', 
        ),
        name='password_reset_complete'
    ),
]