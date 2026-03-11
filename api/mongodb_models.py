"""
MongoDB Database Utilities
"""
import os
from datetime import datetime
from pymongo import MongoClient
from django.conf import settings
from bson import ObjectId


class MongoDBManager:
    """MongoDB Connection Manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        if not self.client:
            mongodb_uri = getattr(settings, 'MONGODB_URI', os.getenv('MONGODB_URI'))
            mongodb_name = getattr(settings, 'MONGODB_NAME', 'spontaneous')
            
            self.client = MongoClient(mongodb_uri)
            self.db = self.client[mongodb_name]
    
    def get_collection(self, name):
        """Get MongoDB collection"""
        return self.db[name]


# Global MongoDB manager instance
mongodb_manager = MongoDBManager()


class MongoModel:
    """Base MongoDB model class"""
    
    collection_name = None
    
    def __init__(self, **kwargs):
        self.data = kwargs
        if '_id' in kwargs:
            self.data['id'] = str(kwargs['_id'])
    
    @classmethod
    def get_collection(cls):
        """Get the MongoDB collection for this model"""
        return mongodb_manager.get_collection(cls.collection_name)
    
    @classmethod
    def create(cls, **data):
        """Create a new document"""
        data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        result = cls.get_collection().insert_one(data)
        return str(result.inserted_id)
    
    @classmethod
    def find_by_id(cls, doc_id):
        """Find document by ID"""
        try:
            obj_id = ObjectId(doc_id) if isinstance(doc_id, str) else doc_id
            doc = cls.get_collection().find_one({'_id': obj_id})
            return cls(**doc) if doc else None
        except:
            return None
    
    @classmethod
    def find_all(cls, **filters):
        """Find all documents matching filters"""
        docs = cls.get_collection().find(filters).sort('created_at', -1)
        return [cls(**doc) for doc in docs]
    
    @classmethod
    def update(cls, doc_id, **data):
        """Update a document"""
        try:
            obj_id = ObjectId(doc_id) if isinstance(doc_id, str) else doc_id
            data['updated_at'] = datetime.utcnow()
            cls.get_collection().update_one(
                {'_id': obj_id},
                {'$set': data}
            )
            return True
        except:
            return False
    
    @classmethod
    def delete(cls, doc_id):
        """Delete a document"""
        try:
            obj_id = ObjectId(doc_id) if isinstance(doc_id, str) else doc_id
            result = cls.get_collection().delete_one({'_id': obj_id})
            return result.deleted_count > 0
        except:
            return False
    
    def to_dict(self):
        """Convert to dictionary"""
        data = self.data.copy()
        if '_id' in data:
            data['id'] = str(data.pop('_id'))
        return data
    
    def __getattr__(self, name):
        return self.data.get(name)


class Company(MongoModel):
    """Company MongoDB Model"""
    collection_name = 'companies'


class UserProfile(MongoModel):
    """UserProfile MongoDB Model"""
    collection_name = 'user_profiles'
    
    @classmethod
    def find_by_user_id(cls, user_id):
        """Find profile by Django user ID"""
        doc = cls.get_collection().find_one({'user_id': user_id})
        return cls(**doc) if doc else None


class JobApplication(MongoModel):
    """JobApplication MongoDB Model"""
    collection_name = 'job_applications'
    
    @classmethod
    def find_by_user_profile(cls, user_profile_id):
        """Find applications by user profile"""
        docs = cls.get_collection().find({'user_profile_id': user_profile_id}).sort('created_at', -1)
        return [cls(**doc) for doc in docs]
    
    @classmethod
    def find_by_company(cls, company_id):
        """Find applications by company"""
        docs = cls.get_collection().find({'company_id': company_id}).sort('created_at', -1)
        return [cls(**doc) for doc in docs]