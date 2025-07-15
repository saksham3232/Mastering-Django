from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.Index.as_view(), name='index'),
    path('contactus/', views.contactus2, name='contact'),
    path('contactusclass/', views.ContactUs.as_view(), name='contactclass'),

    # Authentication Endpoints
    path('signup/', views.RegisterView.as_view(), name='signup'),
    path('login/', views.LoginViewUser.as_view(), name='login'),
    path('logout/', views.LogoutViewUser.as_view(), name='logout')
]