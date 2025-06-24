from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.auth_page, name='auth_page'),
    path('logout/', views.logout_view, name='logout'),
    path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('tutor/dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('profile/', views.profile_redirect, name='profile_redirect'),
    path('search/', views.tutor_search, name='tutor_search'),
    path('tutor/<int:id>/', views.tutor_detail, name='tutor_detail'),
    path('tutor/<int:tutor_id>/rate/', views.submit_rating, name='submit_rating'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('tutor-image/<int:tutor_id>/', views.serve_tutor_image, name='serve_tutor_image'),
  
    
]
