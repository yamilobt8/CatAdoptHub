from django.urls import path

from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('add_cat', views.add_cat, name='add_cat'),
    path('profile/', views.profile, name='profile'),
    path('cat/<int:cat_id>/', views.cat_details, name='cat_detail'),
    path('cat/<int:cat_id>/approve', views.approve_adoption, name='approve_adoption_request'),
]