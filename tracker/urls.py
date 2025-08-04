from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Main dashboard
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),

    # Food logging routes
    path('food-log/', views.foodlog_view, name='food_log'),

    # Weight logging route
    path('weight-log/', views.weight_log_view, name='weight_log'),

    # ✅ Calorie Estimator
    path('calorie-estimator/', views.calorie_estimator_view, name='calorie_estimator'),
    path('', views.home_view, name='home'),

]
