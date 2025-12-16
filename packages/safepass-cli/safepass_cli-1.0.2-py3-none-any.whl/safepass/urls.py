"""URL Configuration for SafePass - Refactored"""

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # ========================================================================
    # TEMPLATE VIEWS (HTML Pages)
    # ========================================================================
    path('', views.login_page, name='home'),
    path('auth/login', views.login_page, name='login_page'),
    path('auth/register', views.register_page, name='register_page'),
    path('auth/logout', views.api_logout, name='logout_page'),
    
    path('dashboard', views.dashboard_page, name='dashboard'),
    path('passwords', views.passwords_page, name='passwords'),
    path('passwords/add', views.password_add_page, name='password_add'),
    path('passwords/<int:password_id>/edit', views.password_edit_page, name='password_edit'),
    path('generator', views.generator_page, name='generator'),
    path('profile', views.profile_page, name='profile'),
    path('help', views.help_page, name='help'),
    
    # ========================================================================
    # API ENDPOINTS (JSON Responses)
    # ========================================================================
    path('api/auth/register', views.api_register, name='api_register'),
    path('api/auth/login', views.api_login, name='api_login'),
    path('api/auth/logout', views.api_logout, name='api_logout'),
    path('api/auth/check', views.api_check_auth, name='api_check_auth'),
    
    path('api/passwords', views.api_passwords, name='api_passwords'),
    path('api/passwords/<int:password_id>', views.api_password_detail, name='api_password_detail'),
    path('api/passwords/<int:password_id>/delete', views.api_password_delete, name='api_password_delete'),
    
    path('api/generate-password', views.api_generate_password, name='api_generate_password'),
    path('api/dashboard/stats', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/export', views.api_export_data, name='api_export_data'),
    path('api/import', views.api_import_data, name='api_import_data'),
    path('api/profile/delete-account', views.api_delete_account, name='api_delete_account'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
