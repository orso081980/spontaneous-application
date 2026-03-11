"""
Frontend URL Configuration
"""
from django.urls import path, register_converter
from . import views

class ObjectIdConverter:
    """Custom converter for MongoDB ObjectId strings"""
    regex = '[a-f0-9]{24}'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return str(value)

# Register the custom converter
register_converter(ObjectIdConverter, 'objectid')

app_name = 'frontend'

urlpatterns = [
    path('', views.home, name='home'),
    path('companies/', views.companies_vue_view, name='company_list'),
    path('companies/page/<int:page>/', views.company_list_view, name='company_list_page'),
    path('companies/map/', views.company_map_view, name='company_map'),
    path('companies/create/', views.company_create_view, name='company_create'),
    path('companies/<objectid:pk>/', views.company_detail_view, name='company_detail'),
    path('companies/<objectid:pk>/edit/', views.company_edit_view, name='company_edit'),
    path('companies/<objectid:pk>/delete/', views.company_delete_view, name='company_delete'),
    path('companies/<objectid:pk>/apply/', views.company_apply_view, name='company_apply'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_create_edit_view, name='profile_edit'),
    path('applications/', views.my_applications_view, name='my_applications'),
    path('applications/<objectid:pk>/edit/', views.application_edit_view, name='application_edit'),
    path('applications/<objectid:pk>/delete/', views.application_delete_view, name='application_delete'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
