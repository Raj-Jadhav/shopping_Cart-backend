# Backend Environment Setup Guide

## Quick Start

### 1. Copy the environment template
```bash
cp .env.example .env
```

### 2. Edit `.env` with your configuration
```bash
# Critical settings
SECRET_KEY=your-super-secret-key-here
DATABASE_PASSWORD=your-secure-password

# Frontend URL (where your Next.js app is running)
FRONTEND_URL=http://localhost:3000
FRONTEND_PORT=3000

# Server port
SERVER_PORT=8000
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Start the server
```bash
python manage.py runserver 0.0.0.0:8000
```

## Environment Variables Reference

### Django Core Settings
- `SECRET_KEY` - Django secret key (change in production!)
- `DEBUG` - Set to 'False' in production
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

### Server Configuration
- `SERVER_PORT` - Port to run Django server on (default: 8000)

### Frontend Integration
- `FRONTEND_URL` - URL of your Next.js frontend (for CORS)
- `FRONTEND_PORT` - Port your Next.js app runs on

### Database Configuration
- `DATABASE_ENGINE` - Default: `django.db.backends.postgresql`
- `DATABASE_NAME` - Database name
- `DATABASE_USER` - Database user
- `DATABASE_PASSWORD` - Database password
- `DATABASE_HOST` - Database host
- `DATABASE_PORT` - Database port

### CORS Configuration
- `CORS_ALLOWED_ORIGINS` - Comma-separated URLs (e.g., `http://localhost:3000,http://localhost:3001`)
- `CORS_ALLOW_ALL_ORIGINS` - Set to 'True' for development only!

### JWT Settings
- `JWT_ACCESS_TOKEN_LIFETIME` - Minutes until access token expires (default: 15)
- `JWT_REFRESH_TOKEN_LIFETIME` - Days until refresh token expires (default: 1)
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)

### Caching
- `CACHE_BACKEND` - Cache backend class (default: locmem)
- `CACHE_MAX_ENTRIES` - Maximum cache entries

### Logging
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)

### Optional: AWS S3 (for media files)
- `USE_S3` - Set to 'True' to use S3 instead of local storage
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_REGION_NAME`

## Important Notes

⚠️ **Never commit `.env` file** - It's already in `.gitignore`

✅ **Always use `.env.example`** - This serves as documentation for required variables

🔒 **Production checklist:**
- Set `DEBUG=False`
- Use a strong `SECRET_KEY`
- Set proper `ALLOWED_HOSTS`
- Update `CORS_ALLOWED_ORIGINS` to your production frontend URL
- Use a production database (PostgreSQL recommended)
- Set `CORS_ALLOW_ALL_ORIGINS=False`
