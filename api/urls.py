"""
API URL Configuration
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    
    # Companies
    path('companies/', views.company_list, name='company-list'),
    path('companies/paginated/', views.companies_paginated, name='companies-paginated'),
    path('companies/countries/', views.companies_countries, name='companies-countries'),
    path('companies/<str:pk>/', views.company_detail, name='company-detail'),
    
    # User Profiles
    path('profiles/', views.user_profile_list, name='profile-list'),
    path('profiles/<str:pk>/', views.user_profile_detail, name='profile-detail'),
    
    # Job Applications
    path('applications/', views.job_application_list, name='application-list'),
    path('applications/<str:pk>/', views.job_application_detail, name='application-detail'),
]
