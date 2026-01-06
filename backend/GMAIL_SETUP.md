# Gmail Email Setup Guide

## Overview
The application now supports email verification and password reset via Gmail SMTP.

## Gmail Configuration Steps

### 1. Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification**
3. Enable 2-Step Verification if not already enabled

### 2. Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **App**: Choose "Mail"
3. Select **Device**: Choose "Other (Custom name)" and enter "AI Fitness App"
4. Click **Generate**
5. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)

### 3. Configure Environment Variables
Create or update `.env` file in the `backend` directory:

```env
# Gmail SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=your-email@gmail.com

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:8000
```

**Important Notes:**
- Use your **full Gmail address** for `SMTP_USERNAME` and `FROM_EMAIL`
- Use the **16-character app password** (remove spaces) for `SMTP_PASSWORD`
- Do NOT use your regular Gmail password

### 4. Test Email Sending
After configuration, test by:
1. Sign up a new user with an email
2. Check your email inbox for verification email
3. Check backend console for any errors

## Features Enabled

### Email Verification
- Users receive verification email after signup
- Email contains verification link
- Users can verify email to activate account

### Password Reset
- Users can request password reset from login screen
- Reset link sent via email
- Link expires after 1 hour
- Secure token-based reset process

## Troubleshooting

### "SMTPAuthenticationError"
- Verify app password is correct (16 characters, no spaces)
- Ensure 2-Factor Authentication is enabled
- Check that SMTP_USERNAME is your full email address

### "Connection refused"
- Check internet connection
- Verify SMTP_SERVER is `smtp.gmail.com`
- Verify SMTP_PORT is `587`

### Emails not received
- Check spam/junk folder
- Verify email address is correct
- Check backend console for error messages
- Ensure Gmail account is not locked

## Development Mode
If email is not configured, the system will:
- Log verification/reset tokens to console
- Print email links for testing
- Still function normally (for development)

## Production Setup
For production:
1. Use a dedicated email service (SendGrid, Mailgun, etc.)
2. Update SMTP settings accordingly
3. Set FRONTEND_URL to your production domain
4. Use environment variables securely (never commit .env file)











