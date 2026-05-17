from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('signup/', views.signup, name='signup'),
    
    # Auth (Login/Logout)
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('report/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('like/<int:pk>/', views.toggle_like, name='toggle_like'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/new/', views.report_create, name='report_create'),
    path('reports/<int:pk>/edit/', views.report_update, name='report_update'),
    path('reports/<int:pk>/delete/', views.report_delete, name='report_delete'),
    path('admin-delete/<int:pk>/', views.admin_delete_report, name='admin_delete'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/password/', views.change_password, name='change_password'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('service-worker.js', TemplateView.as_view(template_name="service-worker.js", content_type='application/javascript'), name='service-worker'),
    path('manifest.json', TemplateView.as_view(template_name="manifest.json", content_type='application/json'), name='manifest'),
]