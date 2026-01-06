# Email Verification Setup

## Overview
The application now supports email verification for user signup and login with username or email.

## Database Migration
Run the migration script to add the new email fields:
```bash
python backend/migrate_db.py
```

This will add:
- `email` (VARCHAR(255)) - User's email address
- `email_verified` (BOOLEAN) - Whether email is verified
- `email_verification_token` (VARCHAR(255)) - Token for email verification

## Email Configuration

### For Development (No Email Setup Required)
If you don't configure email settings, the system will:
- Log verification tokens to the console
- Print verification links for testing
- Still create users successfully

### For Production (Email Setup Required)
Add these environment variables to your `.env` file in the `backend` directory:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

### Gmail Setup
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the generated app password as `SMTP_PASSWORD`

### Other Email Providers
- **Outlook/Hotmail**: `smtp-mail.outlook.com`, port `587`
- **Yahoo**: `smtp.mail.yahoo.com`, port `587`
- **Custom SMTP**: Use your provider's SMTP settings

## API Endpoints

### POST /register
Now requires `email` field:
```json
{
  "first_name": "John",
  "email": "john@example.com",
  "password": "password123",
  "age": 25,
  "height_cm": 175,
  "weight_kg": 70,
  "sex": "male",
  "goal": "maintain"
}
```

### POST /login
Now accepts `username_or_email` (can be either username or email):
```json
{
  "username_or_email": "john@example.com",  // or "John"
  "password": "password123"
}
```

### POST /verify-email
Verify email with token:
```json
{
  "token": "verification-token-from-email"
}
```

## Frontend Changes

### Signup Screen
- Added email input field with validation
- Shows error message for invalid email format
- Displays success message prompting user to check email

### Login Screen
- Changed label from "Username" to "Username or Email"
- Accepts either username or email address
- Updated placeholder text

## Testing
1. Sign up with a new account (email will be sent or logged)
2. Check console/email for verification link
3. Login using either username or email
4. Verify email using the token from the email











