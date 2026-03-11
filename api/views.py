"""
API Views for the Spontaneous Job Board - Django ORM with MongoDB
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Company, UserProfile, JobApplication
from .serializers import CompanySerializer, UserProfileSerializer, JobApplicationSerializer


# ==================== Authentication Views ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not username or not email or not password:
        return Response(
            {'error': 'Please provide username, email and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    # Create token for the user
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_staff or user.is_superuser
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user by deleting token"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==================== Company Views ====================

@api_view(['GET', 'POST'])
def company_list(request):
    """
    GET: List all companies
    POST: Create a new company (admin only)
    """
    if request.method == 'GET':
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Only admin can create companies
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'Only administrators can create companies'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def companies_paginated(request):
    """
    GET: List companies with pagination, search, and filtering
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 9)
    - search: Search by company name
    - country: Filter by country
    - status: Filter by application status for authenticated users
    """
    # Get query parameters
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 9))
    search_query = request.GET.get('search', '').strip()
    country_filter = request.GET.get('country', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    # Start with all companies
    companies = Company.objects.all()
    
    # Apply search filter
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) | 
            Q(field__icontains=search_query)
        )
    
    # Apply country filter
    if country_filter:
        # Filter by exact country match (last word of address)
        companies = companies.filter(address__iregex=r'\b' + country_filter + r'\b')
    
    # Get all companies for initial filtering (before pagination)
    all_companies = list(companies.values('id', 'address'))
    
    # Set up pagination
    paginator = Paginator(companies, page_size)
    
    try:
        companies_page = paginator.page(page)
    except PageNotAnInteger:
        companies_page = paginator.page(1)
    except EmptyPage:
        companies_page = paginator.page(paginator.num_pages)
    
    # Serialize company data
    serializer = CompanySerializer(companies_page.object_list, many=True)
    company_data = serializer.data
    
    # Add user application status if authenticated
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            applications = JobApplication.objects.filter(user_profile=profile).select_related('company')
            user_applications = {str(app.company.id): app.status for app in applications}
            
            # Add application status to each company
            for company in company_data:
                company_id = company['id']
                company['application_status'] = user_applications.get(company_id, None)
        except UserProfile.DoesNotExist:
            # Add null status for all companies
            for company in company_data:
                company['application_status'] = None
    else:
        # Add null status for all companies
        for company in company_data:
            company['application_status'] = None
    
    # Apply status filter AFTER adding application status - filter the queryset results
    if status_filter and request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            applications = JobApplication.objects.filter(user_profile=profile).select_related('company')
            user_applications = {str(app.company.id): app.status for app in applications}
            
            if status_filter == 'not-applied':
                # Get companies without applications
                applied_company_ids = [str(app.company.id) for app in applications]
                companies = companies.exclude(id__in=applied_company_ids)
            else:
                # Get companies with specific status
                filtered_company_ids = [str(app.company.id) for app in applications if app.status == status_filter]
                companies = companies.filter(id__in=filtered_company_ids)
            
            # Re-paginate with filtered results
            paginator = Paginator(companies, page_size)
            try:
                companies_page = paginator.page(page)
            except PageNotAnInteger:
                companies_page = paginator.page(1)
            except EmptyPage:
                companies_page = paginator.page(paginator.num_pages)
            
            # Re-serialize with filtered data
            serializer = CompanySerializer(companies_page.object_list, many=True)
            company_data = serializer.data
            
            # Re-add application status to filtered data
            for company in company_data:
                company_id = company['id']
                company['application_status'] = user_applications.get(company_id, None)
                
        except UserProfile.DoesNotExist:
            pass
    
    # Build response
    response_data = {
        'results': company_data,
        'pagination': {
            'current_page': companies_page.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': companies_page.has_next(),
            'has_previous': companies_page.has_previous(),
        }
    }
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def companies_countries(request):
    """
    GET: List all unique countries from company addresses
    """
    # Import here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from frontend.templatetags.company_filters import COUNTRY_FLAGS
    except ImportError:
        # Fallback country flags if import fails
        COUNTRY_FLAGS = {
            'luxembourg': '🇱🇺', 'belgium': '🇧🇪', 'france': '🇫🇷', 'germany': '🇩🇪',
            'netherlands': '🇳🇱', 'uk': '🇬🇧', 'usa': '🇺🇸', 'canada': '🇨🇦'
        }
    
    companies = Company.objects.exclude(address__isnull=True).exclude(address='')
    countries = set()
    
    for company in companies:
        if company.address:
            parts = company.address.split()
            if parts:
                country = parts[-1].strip()
                if country:
                    countries.add(country)
    
    # Create country list with flags
    country_list = []
    for country in sorted(countries):
        flag = COUNTRY_FLAGS.get(country.lower(), '🌍')
        country_list.append({
            'name': country,
            'flag': flag
        })
    
    return Response(country_list)


@api_view(['GET', 'PUT', 'DELETE'])
def company_detail(request, pk):
    """
    GET: Retrieve a company
    PUT: Update a company (admin only)
    DELETE: Delete a company (admin only)
    """
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'GET':
        serializer = CompanySerializer(company)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Only admin can update companies
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'Only administrators can update companies'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Only admin can delete companies
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'Only administrators can delete companies'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== User Profile Views ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_profile_list(request):
    """
    GET: Get current user's profile
    POST: Create profile for current user
    """
    if request.method == 'GET':
        # Get profile for current user
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        # Check if user already has a profile
        if UserProfile.objects.filter(user=request.user).exists():
            return Response(
                {'error': 'Profile already exists for this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_profile_detail(request, pk):
    """
    GET: Retrieve a user profile
    PUT: Update a user profile (own profile only)
    DELETE: Delete a user profile (own profile only)
    """
    profile = get_object_or_404(UserProfile, pk=pk)
    
    # Check if this is the user's own profile (or if user is admin)
    is_own_profile = profile.user == request.user
    is_admin = request.user.is_staff or request.user.is_superuser
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not (is_own_profile or is_admin):
            return Response(
                {'error': 'You can only update your own profile'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not (is_own_profile or is_admin):
            return Response(
                {'error': 'You can only delete your own profile'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== Job Application Views ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def job_application_list(request):
    """
    GET: List all applications for current user
    POST: Create a new job application
    """
    # Get user profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'You need to create a profile first'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if request.method == 'GET':
        applications = JobApplication.objects.filter(user_profile=user_profile).select_related('company')
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = JobApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_profile=user_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def job_application_detail(request, pk):
    """
    GET: Retrieve a job application
    PUT: Update a job application (own application only)
    DELETE: Delete a job application (own application only)
    """
    application = get_object_or_404(JobApplication, pk=pk)
    
    # Check ownership
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        is_own_application = application.user_profile == user_profile
    except UserProfile.DoesNotExist:
        is_own_application = False
    
    is_admin = request.user.is_staff or request.user.is_superuser
    
    if request.method == 'GET':
        if not (is_own_application or is_admin):
            return Response(
                {'error': 'You can only view your own applications'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not (is_own_application or is_admin):
            return Response(
                {'error': 'You can only update your own applications'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = JobApplicationSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not (is_own_application or is_admin):
            return Response(
                {'error': 'You can only delete your own applications'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== Company Applications (for admin) ====================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def company_applications(request, company_id):
    """Get all applications for a specific company (admin only)"""
    company = get_object_or_404(Company, pk=company_id)
    applications = JobApplication.objects.filter(company=company).select_related('user_profile', 'company')
    serializer = JobApplicationSerializer(applications, many=True)
    return Response(serializer.data)
