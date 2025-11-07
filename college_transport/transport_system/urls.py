from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register-route/', views.register_route, name='register_route'),
    path('notifications/', views.notifications, name='notifications'),
    path('bus-tracking/', views.bus_tracking, name='bus_tracking'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("make-payment/", views.make_payment, name="make_payment"),
    path("download-receipt/", views.download_receipt, name="download_receipt"),
    
]
