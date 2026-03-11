"""
Frontend Views for the Spontaneous Job Board
"""
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.models import Company, UserProfile, JobApplication


def get_available_icons():
    """Get list of available technology icons"""
    icons_dir = os.path.join(settings.BASE_DIR, 'static', 'icons')
    if not os.path.exists(icons_dir):
        return []
    
    available_icons = []
    for filename in os.listdir(icons_dir):
        if filename.endswith(('.svg', '.png', '.jpg', '.jpeg')) and not filename.startswith('.'):
            available_icons.append(filename)
    
    return sorted(available_icons)


def home(request):
    """Home page showing all companies with user's application status"""
    companies = Company.objects.all()
    available_icons = get_available_icons()
    
    # Get user's applications if authenticated
    user_applications = {}
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            applications = JobApplication.objects.filter(user_profile=profile).select_related('company')
            user_applications = {app.company.id: app for app in applications}
        except UserProfile.DoesNotExist:
            pass
    
    return render(request, 'frontend/home.html', {
        'companies': companies,
        'user_applications': user_applications,
        'available_icons': available_icons
    })


def company_list_view(request, page=1):
    """List all companies with pagination"""
    companies = Company.objects.all()
    
    # Get user's applications if authenticated
    user_applications = {}
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            applications = JobApplication.objects.filter(user_profile=profile).select_related('company')
            user_applications = {app.company.id: app for app in applications}
        except UserProfile.DoesNotExist:
            pass
    
    paginator = Paginator(companies, 9)  # 9 companies per page
    
    try:
        companies_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        companies_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        companies_page = paginator.page(paginator.num_pages)
    
    return render(request, 'frontend/company_list.html', {
        'companies': companies_page,
        'page_obj': companies_page,
        'user_applications': user_applications
    })


def company_detail_view(request, pk):
    """Company detail page"""
    import json
    company = get_object_or_404(Company, pk=pk)
    available_icons = get_available_icons()
    
    # Check if user has already applied
    user_application = None
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            user_application = JobApplication.objects.filter(
                user_profile=profile,
                company=company
            ).first()
        except UserProfile.DoesNotExist:
            pass
    
    return render(request, 'frontend/company_detail.html', {
        'company': company,
        'user_application': user_application,
        'available_icons': available_icons
    })


@login_required
def company_create_view(request):
    """Create a new company (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Only administrators can create companies')
        return redirect('frontend:home')
    
    if request.method == 'POST':
        # Helper function to convert empty strings to None for optional fields
        def get_optional(field_name):
            value = request.POST.get(field_name)
            return value if value and value.strip() else None
        
        # Check for duplicates based on name and website
        name = request.POST.get('name')
        website = request.POST.get('website')
        if Company.objects.filter(name=name, website=website).exists():
            messages.error(request, f'A company with the name "{name}" and website "{website}" already exists.')
            return render(request, 'frontend/company_form.html', {
                'form_data': request.POST
            })
        
        company = Company.objects.create(
            name=name,
            field=request.POST.get('field'),
            website=website,
            contact=get_optional('contact'),
            contact_form_url=get_optional('contact_form_url'),
            phone=get_optional('phone'),
            address=request.POST.get('address'),
            vat_number=get_optional('vat_number'),
            description=get_optional('description'),
            potential_improvement=get_optional('potential_improvement'),
            logo_url=request.POST.get('logo_url'),
            plus_code=get_optional('plus_code'),
            latitude=get_optional('latitude'),
            longitude=get_optional('longitude'),
            technologies=get_optional('technologies'),
            linkedin_url=get_optional('linkedin_url'),
            facebook_url=get_optional('facebook_url'),
            twitter_url=get_optional('twitter_url'),
            instagram_url=get_optional('instagram_url'),
            youtube_url=get_optional('youtube_url')
        )
        messages.success(request, 'Company created successfully')
        return redirect('frontend:company_detail', pk=company.id)
    
    return render(request, 'frontend/company_form.html')


@login_required
def company_edit_view(request, pk):
    """Edit a company (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Only administrators can edit companies')
        return redirect('frontend:home')
    
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        # Helper function to convert empty strings to None for optional fields
        def get_optional(field_name):
            value = request.POST.get(field_name)
            return value if value and value.strip() else None
        
        # Check for duplicates (excluding current company)
        name = request.POST.get('name')
        website = request.POST.get('website')
        if Company.objects.filter(name=name, website=website).exclude(pk=pk).exists():
            messages.error(request, f'Another company with the name "{name}" and website "{website}" already exists.')
            return render(request, 'frontend/company_form.html', {'company': company})
        
        company.name = name
        company.field = request.POST.get('field')
        company.website = website
        company.contact = get_optional('contact')
        company.contact_form_url = get_optional('contact_form_url')
        company.phone = get_optional('phone')
        company.address = request.POST.get('address')
        company.vat_number = get_optional('vat_number')
        company.description = get_optional('description')
        company.potential_improvement = get_optional('potential_improvement')
        company.logo_url = request.POST.get('logo_url')
        company.plus_code = get_optional('plus_code')
        company.latitude = get_optional('latitude')
        company.longitude = get_optional('longitude')
        company.technologies = get_optional('technologies')
        company.linkedin_url = get_optional('linkedin_url')
        company.facebook_url = get_optional('facebook_url')
        company.twitter_url = get_optional('twitter_url')
        company.instagram_url = get_optional('instagram_url')
        company.youtube_url = get_optional('youtube_url')
        company.save()
        
        messages.success(request, 'Company updated successfully')
        return redirect('frontend:company_detail', pk=pk)
    
    return render(request, 'frontend/company_form.html', {'company': company})


@login_required
def company_delete_view(request, pk):
    """Delete a company (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Only administrators can delete companies')
        return redirect('frontend:home')
    
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        company_name = company.name
        company.delete()
        messages.success(request, f'Company "{company_name}" has been deleted successfully')
        return redirect('frontend:company_list')
    
    return render(request, 'frontend/company_delete.html', {'company': company})


@login_required
def profile_view(request):
    """View user profile"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    
    return render(request, 'frontend/profile.html', {'profile': profile})


@login_required
def profile_create_edit_view(request):
    """Create or edit user profile"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        job_position = request.POST.get('job_position', '').strip()
        email = request.POST.get('email', '').strip()
        bio = request.POST.get('bio', '').strip()
        phone = request.POST.get('phone', '').strip()
        linkedin = request.POST.get('linkedin', '').strip()
        
        # Validate required fields
        if not name or not job_position or not email:
            messages.error(request, 'Name, job position, and email are required')
            return render(request, 'frontend/profile_form.html', {'profile': profile})
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messages.error(request, 'Please enter a valid email address')
            return render(request, 'frontend/profile_form.html', {'profile': profile})
        
        # Validate LinkedIn URL format if provided
        if linkedin and not linkedin.startswith('http'):
            linkedin = 'https://' + linkedin
        
        # Check if email is already taken by another user (but allow current user to keep their email)
        try:
            existing_profile = UserProfile.objects.filter(email=email).exclude(user=request.user).first()
            if existing_profile:
                messages.error(request, 'This email is already taken by another user')
                return render(request, 'frontend/profile_form.html', {'profile': profile})
        except Exception as db_error:
            print(f"Database error during email check: {db_error}")
            messages.error(request, 'Database error occurred while checking email availability')
            return render(request, 'frontend/profile_form.html', {'profile': profile})
        
        try:
            if profile:
                # Update existing profile
                profile.name = name
                profile.job_position = job_position
                profile.email = email
                profile.bio = bio
                profile.phone = phone
                profile.linkedin = linkedin
                profile.save()
                messages.success(request, 'Profile updated successfully')
            else:
                # Create new profile
                profile = UserProfile.objects.create(
                    user=request.user,
                    name=name,
                    job_position=job_position,
                    email=email,
                    bio=bio,
                    phone=phone,
                    linkedin=linkedin
                )
                messages.success(request, 'Profile created successfully')
            
            return redirect('frontend:profile')
        except Exception as e:
            print(f"Error saving profile: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error saving profile: {str(e)}')
            return render(request, 'frontend/profile_form.html', {'profile': profile})
    
    return render(request, 'frontend/profile_form.html', {'profile': profile})


def register_view(request):
    """User registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'frontend/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'frontend/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Registration successful')
        return redirect('frontend:home')
    
    return render(request, 'frontend/register.html')


def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('frontend:home')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'frontend/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('frontend:home')


@login_required
def company_apply_view(request, pk):
    """Apply to a company with project suggestion"""
    company = get_object_or_404(Company, pk=pk)
    
    # Check if user has a profile
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please create your profile first')
        return redirect('frontend:profile_edit')
    
    # Check if user has already applied
    existing_application = JobApplication.objects.filter(
        user_profile=profile,
        company=company
    ).first()
    
    if existing_application:
        messages.info(request, f'You have already applied to {company.name}')
        return redirect('frontend:company_detail', pk=pk)
    
    if request.method == 'POST':
        # Helper function to convert empty strings to None for optional fields
        def get_optional(field_name):
            value = request.POST.get(field_name)
            return value if value and value.strip() else None
        
        application = JobApplication.objects.create(
            user_profile=profile,
            company=company,
            position=get_optional('position'),
            project_to_suggest=request.POST.get('project_to_suggest'),
            link_to_project=get_optional('link_to_project'),
            message=get_optional('message'),
            status='created'
        )
        messages.success(request, f'Application submitted to {company.name}')
        return redirect('frontend:my_applications')
    
    return render(request, 'frontend/application_form.html', {'company': company, 'profile': profile})


@login_required
def application_edit_view(request, pk):
    """Edit a job application"""
    application = get_object_or_404(JobApplication, pk=pk)
    
    # Check if user owns this application
    try:
        profile = UserProfile.objects.get(user=request.user)
        if application.user_profile != profile and not request.user.is_staff:
            messages.error(request, 'You can only edit your own applications')
            return redirect('frontend:my_applications')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('frontend:home')
    
    if request.method == 'POST':
        # Helper function to convert empty strings to None for optional fields
        def get_optional(field_name):
            value = request.POST.get(field_name)
            return value if value and value.strip() else None
        
        application.position = get_optional('position')
        application.project_to_suggest = request.POST.get('project_to_suggest')
        application.link_to_project = get_optional('link_to_project')
        application.message = get_optional('message')
        application.status = request.POST.get('status', 'created')
        application.save()
        
        messages.success(request, 'Application updated successfully')
        return redirect('frontend:my_applications')
    
    return render(request, 'frontend/application_form.html', {
        'company': application.company,
        'profile': application.user_profile,
        'application': application,
        'edit_mode': True
    })


@login_required
def application_delete_view(request, pk):
    """Delete a job application"""
    application = get_object_or_404(JobApplication, pk=pk)
    
    # Check if user owns this application
    try:
        profile = UserProfile.objects.get(user=request.user)
        if application.user_profile != profile and not request.user.is_staff:
            messages.error(request, 'You can only delete your own applications')
            return redirect('frontend:my_applications')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('frontend:home')
    
    if request.method == 'POST':
        company_name = application.company.name
        application.delete()
        messages.success(request, f'Application to {company_name} deleted successfully')
        return redirect('frontend:my_applications')
    
    # Show confirmation page
    return render(request, 'frontend/my_applications.html', {
        'confirm_delete': application
    })


@login_required
def my_applications_view(request):
    """View user's applications"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please create your profile first')
        return redirect('frontend:profile_edit')
    
    applications = JobApplication.objects.filter(user_profile=profile).select_related('company').order_by('-created_at')
    
    return render(request, 'frontend/my_applications.html', {
        'applications': applications,
        'profile': profile
    })


def company_map_view(request):
    """View companies on a map"""
    # Get all companies that have location data
    companies = Company.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).exclude(latitude='').exclude(longitude='')
    
    # Filter by user if authenticated (show all companies but can be extended)
    if request.user.is_authenticated:
        # You can add additional filtering here if needed
        pass
    
    from django.conf import settings
    return render(request, 'frontend/company_map.html', {
        'companies': companies,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    })


def companies_vue_view(request):
    """Vue.js powered companies view with API integration"""
    from django.conf import settings
    import json
    
    # Get country flags for Vue.js
    from .templatetags.company_filters import COUNTRY_FLAGS
    available_icons = get_available_icons()
    
    return render(request, 'frontend/companies.html', {
        'country_flags_json': json.dumps(COUNTRY_FLAGS),
        'available_icons': available_icons
    })
