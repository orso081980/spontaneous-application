# 🚀 Quick Start Guide

## Running the Application

The server is currently running! Access it at:

- **Frontend:** http://127.0.0.1:8000
- **API:** http://127.0.0.1:8000/api/
- **Admin Panel:** http://127.0.0.1:8000/admin/

## Login Credentials

**Admin Account (can CRUD companies):**

- Username: `admin`
- Password: `admin123`

**Test User Account:**

- Username: `testuser`
- Password: `test123`

## Quick Actions

### 1. Browse Companies

Visit http://127.0.0.1:8000 - no login required

### 2. Login as Admin

1. Go to http://127.0.0.1:8000/login/
2. Login with admin credentials
3. Click "Add Company" to create a new job posting

### 3. Create Your Profile

1. Register a new account or login
2. Go to "Profile" → "Create Profile"
3. Fill in your details
4. Use the rich text editor for bio and project suggestions

### 4. Test the API

**Get all companies:**

```bash
curl http://127.0.0.1:8000/api/companies/
```

**Login via API:**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Create a company (admin only):**

```bash
# First get your token from login response
curl -X POST http://127.0.0.1:8000/api/companies/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"New Company",
    "field":"Software",
    "position":"Developer",
    "website":"https://example.com",
    "contact":"hr@example.com"
  }'
```

**Or run the test script:**

```bash
./test_api.sh
```

## Project Files

- **README.md** - Full documentation
- **PROJECT_SUMMARY.md** - Complete project overview
- **requirements.txt** - Python dependencies
- **create_test_data.py** - Create sample data
- **test_api.sh** - API testing script

## Development Commands

**Start server:**

```bash
source venv/bin/activate
python manage.py runserver
```

**Create superuser:**

```bash
python manage.py createsuperuser
```

**Run migrations:**

```bash
python manage.py migrate
```

**Create test data:**

```bash
python create_test_data.py
```

## What's Working

✅ User registration and authentication  
✅ Company CRUD (admin only)  
✅ User profile management  
✅ Rich text editing with Quill  
✅ REST API with token authentication  
✅ MongoDB integration  
✅ Responsive design with Tailwind  
✅ Admin panel  
✅ Role-based permissions

## Next Steps

1. **Explore the frontend** - Browse companies, create a profile
2. **Try the admin panel** - Manage companies and users
3. **Test the API** - Use curl or Postman
4. **Integrate with Nuxt/Vue** - API is ready for frontend framework

## Notes

- MongoDB is hosted on Atlas (cloud)
- Frontend uses Django templates + Tailwind CSS
- API supports CORS for future frontend integration
- Authentication: Token-based for API, Session-based for web
- All passwords are securely hashed

## Support

Check the README.md for detailed API documentation and examples.

Enjoy building with Spontaneous Job Board! 🎉
