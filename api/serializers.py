"""
Django REST Framework Serializers for MongoDB models
"""
from rest_framework import serializers
from .models import Company, UserProfile, JobApplication
from bson import ObjectId


class ObjectIdField(serializers.Field):
    """Custom field to serialize ObjectId as string"""
    
    def to_representation(self, value):
        return str(value)
    
    def to_internal_value(self, data):
        try:
            return ObjectId(data)
        except Exception:
            raise serializers.ValidationError("Invalid ObjectId")


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    id = ObjectIdField(read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'field', 'website', 'contact', 'contact_form_url',
            'phone', 'address', 'vat_number', 'description', 'potential_improvement',
            'logo_url', 'plus_code', 'latitude', 'longitude', 'technologies',
            'linkedin_url', 'facebook_url', 'twitter_url', 'instagram_url',
            'youtube_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    id = ObjectIdField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_id', 'username', 'name', 'job_position', 'email',
            'bio', 'phone', 'linkedin', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'username', 'created_at', 'updated_at']


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for JobApplication model"""
    id = ObjectIdField(read_only=True)
    user_profile_id = serializers.PrimaryKeyRelatedField(
        source='user_profile',
        queryset=UserProfile.objects.all()
    )
    company_id = serializers.PrimaryKeyRelatedField(
        source='company',
        queryset=Company.objects.all()
    )
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'user_profile_id', 'company_id', 'company_name', 'position',
            'project_to_suggest', 'link_to_project', 'message', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'company_name']
