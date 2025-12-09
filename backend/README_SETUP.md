# Backend Setup Guide

## 1. Install Required Packages

```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn[standard]
- sqlalchemy
- mysql-connector-python
- python-multipart
- passlib[bcrypt]
- python-jose[cryptography]

## 2. Configure MySQL Database

1. Import the SQL file into MySQL:
   ```bash
   mysql -u root -p fitness_ai < fitness_ai.sql
   ```

2. Update `database.py` with your MySQL credentials:
   ```python
   MYSQL_USER = "root"
   MYSQL_PASSWORD = "your_password"
   MYSQL_HOST = "127.0.0.1"
   MYSQL_PORT = "3306"
   MYSQL_DATABASE = "fitness_ai"
   ```

## 3. Create Uploads Directory

The backend will automatically create the `uploads/` directory when it starts.

## 4. Run the Backend

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 5. Test Endpoints

### Test Connection
```
GET http://localhost:8000/test
```

### Create Supplement (with image)
```
POST http://localhost:8000/supplements
Content-Type: multipart/form-data

name: "Whey Protein"
description: "High quality protein"
price: 99.99
image: [select file]
```

### View Image
```
GET http://localhost:8000/uploads/{filename}.jpg
```

## API Endpoints

### Auth
- `POST /signup` - Create new user
- `POST /login` - Login user (updates last_login)

### Supplements
- `POST /supplements` - Create supplement (multipart/form-data)
- `GET /supplements` - List all supplements
- `GET /supplements/{id}` - Get single supplement
- `PUT /supplements/{id}` - Update supplement (multipart/form-data)
- `DELETE /supplements/{id}` - Delete supplement (deletes image file too)

### Favorites
- `POST /favorites/{user_id}/{supplement_id}` - Add to favorites
- `GET /favorites/{user_id}` - Get user's favorite supplement IDs
- `DELETE /favorites/{user_id}/{supplement_id}` - Remove from favorites

### Users
- `GET /user/{user_id}` - Get user profile
- `PUT /user/{user_id}` - Update user profile (auto-calculates BMI/BMR)

### Admin
- `GET /admin/users` - List all users
- `PUT /admin/user/{user_id}/status` - Toggle user active/inactive

## Image Upload Flow

1. React Native sends FormData with image file
2. Backend receives file via `UploadFile`
3. Backend saves file as `{uuid}.jpg` in `/uploads/` directory
4. Backend stores only filename in database (`image_url` column)
5. Frontend loads images from: `http://server:8000/uploads/{filename}`

## Notes

- Images are stored as files, not base64 (much more efficient)
- File deletion is automatic when supplement is deleted
- Static file serving is enabled at `/uploads/`
- All timestamps (created_at, updated_at, last_login) are handled automatically

