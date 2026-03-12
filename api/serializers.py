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


class ObjectIdPrimaryKeyField(serializers.PrimaryKeyRelatedField):
    """PrimaryKeyRelatedField that serializes the pk (ObjectId) as a string."""

    def to_representation(self, value):
        return str(value.pk)


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    id = ObjectIdField(read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'field', 'website', 'contact', 'contact_form_url',
            'phone', 'address', 'city', 'country', 'vat_number', 'description',
            'potential_improvement', 'logo_url', 'plus_code', 'latitude',
            'longitude', 'technologies', 'linkedin_url', 'facebook_url',
            'twitter_url', 'instagram_url', 'youtube_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'city', 'country', 'created_at', 'updated_at']

    def validate_address(self, value: str) -> str:
        """Require exactly three comma-separated parts: Street, City PostalCode, Country"""
        if not value:
            return value
        parts = [p.strip() for p in value.split(',')]
        if len(parts) != 3 or not all(parts):
            raise serializers.ValidationError(
                "Address must have exactly three comma-separated parts: "
                "Street, City PostalCode, Country — "
                "e.g. \"Kerkstraat 106, 9050 Gent, Belgium\""
            )
        return value

    def create(self, validated_data: dict) -> Company:
        self._parse_address(validated_data)
        return super().create(validated_data)

    def update(self, instance: Company, validated_data: dict) -> Company:
        if 'address' in validated_data:
            self._parse_address(validated_data)
        return super().update(instance, validated_data)

    @staticmethod
    def _parse_address(data: dict) -> None:
        """Populate city and country from a validated three-part address."""
        address = data.get('address', '')
        if address:
            parts = [p.strip() for p in address.split(',')]
            if len(parts) == 3:
                data['city'] = parts[1]
                data['country'] = parts[2]


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
    user_profile_id = ObjectIdPrimaryKeyField(
        source='user_profile',
        queryset=UserProfile.objects.all(),
        required=False  # View always provides this via serializer.save(user_profile=...)
    )
    company_id = ObjectIdPrimaryKeyField(
        source='company',
        queryset=Company.objects.all()
    )
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_country = serializers.CharField(source='company.country', read_only=True, default='')

    class Meta:
        model = JobApplication
        fields = [
            'id', 'user_profile_id', 'company_id', 'company_name', 'company_country',
            'position', 'project_to_suggest', 'link_to_project', 'message', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'company_name', 'company_country']
