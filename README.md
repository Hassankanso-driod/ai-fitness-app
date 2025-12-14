# AI Fitness App 

A comprehensive fitness application built with React Native (Expo) and FastAPI, featuring AI-powered meal planning and workout generation.

##  Features

-  User Authentication (Signup/Login)
-  Cross-platform mobile app (Android & iOS)
-  AI-powered meal plan generation
-  AI-powered workout plan generation
-  Supplement management system
-  User profile management with BMI/BMR calculations
-  Favorites system
-  Push notifications
-  Admin dashboard for user management

##  Tech Stack

### Frontend
- **React Native** with **Expo**
- **TypeScript**
- **React Navigation**
- **React Native Paper** (UI components)
- **Firebase** (Notifications)
- **AsyncStorage** (Local storage)

### Backend
- **FastAPI** (Python web framework)
- **SQLAlchemy** (ORM)
- **MySQL** (Database)
- **Uvicorn** (ASGI server)
- **JWT** (Authentication)
- **bcrypt** (Password hashing)

##  Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.8 or higher) - [Download](https://www.python.org/)
- **MySQL** Server - [Download](https://dev.mysql.com/downloads/)
- **Expo CLI** - Install globally: `npm install -g expo-cli`
- **Git** - [Download](https://git-scm.com/)

### For Mobile Development
- **Expo Go** app on your phone (iOS/Android) - [iOS App Store](https://apps.apple.com/app/expo-go/id982107779) | [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
- OR **Android Studio** / **Xcode** for emulator/simulator

##  Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Hassankanso-driod/ai-fitness-app.git
cd ai-fitness-app

```

### 2. Backend Setup

#### Step 1: Navigate to Backend Directory

```bash
cd backend
```

#### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Configure MySQL Database

1. **Create MySQL Database:**
   ```sql
   CREATE DATABASE fitness_ai;
   ```

2. **Update Database Configuration:**
   
   Edit `backend/database.py` and update your MySQL credentials:
   ```python
   MYSQL_USER = "root"              # Your MySQL username
   MYSQL_PASSWORD = "your_password" # Your MySQL password
   MYSQL_HOST = "127.0.0.1"         # Usually localhost
   MYSQL_PORT = "3306"              # Default MySQL port
   MYSQL_DATABASE = "fitness_ai"    # Database name
   ```

3. **Create Database Tables:**
   
   The tables will be created automatically when you first run the backend. Alternatively, you can use the migration script:
   ```bash
   python migrate_db.py
   ```

#### Step 5: Create Admin User (Optional)

```bash
python create_admin.py
```

#### Step 6: Run the Backend Server

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: **http://localhost:8000**

You can view the API documentation at: **http://localhost:8000/docs**

### 3. Frontend Setup

#### Step 1: Navigate to Frontend Directory

Open a **new terminal** and navigate to the frontend directory:

```bash
cd ai-fitness-app
```

#### Step 2: Install Dependencies

```bash
npm install
```

#### Step 3: Configure Backend URL

Edit `ai-fitness-app/app/config.ts` and update the `BASE_URL`:

```typescript
export const BASE_URL = "http://YOUR_IP_ADDRESS:8000";
```

**Important:** 
- **Android Emulator:** Use `http://10.0.2.2:8000`
- **iOS Simulator:** Use `http://localhost:8000`
- **Physical Device:** Use your computer's IP address (e.g., `http://192.168.1.102:8000`)

**How to find your IP address:**
- **Windows:** Open Command Prompt → `ipconfig` → Look for "IPv4 Address"
- **Mac/Linux:** Open Terminal → `ifconfig` or `ip addr` → Look for inet address

#### Step 4: Start the Frontend

```bash
npm start
```

Or use the specific platform commands:

```bash
npm run android    # For Android
npm run ios        # For iOS
npm run web        # For Web
```

This will open the Expo developer tools in your browser. You can:
- Scan the QR code with Expo Go app (on your phone)
- Press `a` for Android emulator
- Press `i` for iOS simulator

##  Project Structure

```
Ai-Fitness-App/
├── backend/                 # FastAPI Backend
│   ├── main.py             # Main FastAPI application
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── crud.py             # Database operations
│   ├── auth.py             # Authentication utilities
│   ├── ai_meal_service.py  # AI meal plan service
│   ├── ai_workout_service.py # AI workout service
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # Uploaded images directory
│
├── ai-fitness-app/         # React Native Frontend
│   ├── app/
│   │   ├── screens/        # App screens
│   │   ├── components/     # Reusable components
│   │   ├── navigation/     # Navigation setup
│   │   ├── utils/          # Utility functions
│   │   └── config.ts       # API configuration
│   ├── android/            # Android native code
│   ├── assets/             # Images and assets
│   ├── package.json        # Node dependencies
│   └── App.tsx             # Main app component
│
└── README.md               # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /signup` - Create new user account
- `POST /login` - User login (returns JWT token)

### Supplements
- `GET /supplements` - Get all supplements
- `GET /supplements/{id}` - Get supplement by ID
- `POST /supplements` - Create new supplement (with image upload)
- `PUT /supplements/{id}` - Update supplement
- `DELETE /supplements/{id}` - Delete supplement

### Users
- `GET /user/{user_id}` - Get user profile
- `PUT /user/{user_id}` - Update user profile

### Favorites
- `POST /favorites/{user_id}/{supplement_id}` - Add to favorites
- `GET /favorites/{user_id}` - Get user favorites
- `DELETE /favorites/{user_id}/{supplement_id}` - Remove from favorites

### AI Services
- `POST /ai/meal-plan` - Generate AI meal plan
- `POST /ai/workout-plan` - Generate AI workout plan

### Admin
- `GET /admin/users` - Get all users
- `PUT /admin/user/{user_id}/status` - Toggle user status

For detailed API documentation, visit: **http://localhost:8000/docs**

##  Testing

### Test Backend Connection

```bash
curl http://localhost:8000/test
```

Expected response:
```json
{"message": "Backend is reachable ✅"}
```

### Test Login

```bash
python backend/test_login.py
```

## 📱 Running on Different Platforms

### Android Emulator
1. Start Android Studio and launch an emulator
2. Run `npm run android` in the `ai-fitness-app` directory
3. Use `http://10.0.2.2:8000` as BASE_URL in config.ts

### iOS Simulator (Mac only)
1. Run `npm run ios` in the `ai-fitness-app` directory
2. Use `http://localhost:8000` as BASE_URL in config.ts

### Physical Device
1. Ensure your phone and computer are on the same Wi-Fi network
2. Find your computer's IP address
3. Update `BASE_URL` in `config.ts` with your IP
4. Run `npm start` and scan the QR code with Expo Go app

## 🔧 Troubleshooting

### Backend Issues

**Database Connection Error:**
- Verify MySQL is running: `mysql -u root -p`
- Check credentials in `backend/database.py`
- Ensure database `fitness_ai` exists

**Port Already in Use:**
- Change port: `uvicorn main:app --port 8001`
- Or kill the process using port 8000

**Module Not Found:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**Cannot Connect to Backend:**
- Verify backend is running on port 8000
- Check `BASE_URL` in `config.ts`
- For physical device: ensure same Wi-Fi network and correct IP address

**Expo Start Fails:**
- Clear cache: `expo start -c`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

**Android Build Issues:**
- Clean build: `cd android && ./gradlew clean`
- Check Android SDK installation in Android Studio

##  Environment Variables

Create a `.env` file in the `backend` directory (optional):

```env
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=fitness_ai
```

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

##  License

This project is licensed under the MIT License.

##  Author

**Hassan Kanso**
- Email: hassankanso094@gmail.com

##  Acknowledgments

- FastAPI community
- React Native and Expo teams
- All contributors and users of this project

---



