from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services_list, name='services'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('search/', views.search, name='search'),
    path('calculator/', views.calculator, name='calculator'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('api/search/', views.api_search, name='api_search'),
]
