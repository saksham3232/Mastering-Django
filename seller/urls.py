from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('signupseller/', views.RegisterViewSeller.as_view(), name='signupseller'),
    path('signup/', views.RegisterView.as_view(), name='signup'),
    path('login/', views.LoginViewUser.as_view(), name='login'),
    path('logout/', views.LogoutViewUser.as_view(), name='logout')
]