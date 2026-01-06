# email_utils.py - Email sending utilities
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import secrets

load_dotenv()

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)


def generate_verification_token() -> str:
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)


def send_verification_email(email: str, token: str, first_name: str) -> bool:
    """
    Send email verification link to user
    Returns True if email sent successfully, False otherwise
    """
    # Get frontend URL from environment or use default
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        # If email is not configured, just log it (for development)
        print(f"[EMAIL] Verification email would be sent to {email}")
        print(f"[EMAIL] Verification token: {token}")
        print(f"[EMAIL] Verification link: {FRONTEND_URL}/verify-email?token={token}")
        return True  # Return True for development
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Verify Your Email - AI Fitness App"
        msg["From"] = FROM_EMAIL
        msg["To"] = email
        
        # Create verification link
        verification_url = f"{FRONTEND_URL}/verify-email?token={token}"
        
        # Email body
        text = f"""
        Hello {first_name},
        
        Thank you for signing up for AI Fitness App!
        
        Please verify your email address by clicking the link below:
        {verification_url}
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        AI Fitness App Team
        """
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #4CAF50;">Hello {first_name}!</h2>
              <p>Thank you for signing up for AI Fitness App!</p>
              <p>Please verify your email address by clicking the button below:</p>
              <p style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email</a>
              </p>
              <p>Or copy and paste this link in your browser:</p>
              <p style="word-break: break-all; color: #666;">{verification_url}</p>
              <p style="color: #999; font-size: 12px; margin-top: 30px;">If you didn't create this account, please ignore this email.</p>
              <p style="margin-top: 20px;">Best regards,<br>AI Fitness App Team</p>
            </div>
          </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email with Gmail
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"[SUCCESS] Verification email sent to {email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] Gmail authentication failed. Check your SMTP_USERNAME and SMTP_PASSWORD in .env file")
        print(f"[ERROR] Details: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to send verification email: {e}")
        return False


def send_password_reset_email(email: str, token: str, first_name: str) -> bool:
    """
    Send password reset link to user
    Returns True if email sent successfully, False otherwise
    """
    # Get frontend URL from environment or use default
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        # If email is not configured, just log it (for development)
        print(f"[EMAIL] Password reset email would be sent to {email}")
        print(f"[EMAIL] Reset token: {token}")
        print(f"[EMAIL] Reset link: {FRONTEND_URL}/reset-password?token={token}")
        return True  # Return True for development
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Reset Your Password - AI Fitness App"
        msg["From"] = FROM_EMAIL
        msg["To"] = email
        
        # Create reset link
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        
        # Email body
        text = f"""
        Hello {first_name},
        
        You requested to reset your password for your AI Fitness App account.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email and your password will remain unchanged.
        
        Best regards,
        AI Fitness App Team
        """
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #4CAF50;">Password Reset Request</h2>
              <p>Hello {first_name},</p>
              <p>You requested to reset your password for your AI Fitness App account.</p>
              <p>Click the button below to reset your password:</p>
              <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
              </p>
              <p>Or copy and paste this link in your browser:</p>
              <p style="word-break: break-all; color: #666;">{reset_url}</p>
              <p style="color: #ff9800; font-weight: bold;">⚠️ This link will expire in 1 hour.</p>
              <p style="color: #999; font-size: 12px; margin-top: 30px;">If you didn't request this, please ignore this email and your password will remain unchanged.</p>
              <p style="margin-top: 20px;">Best regards,<br>AI Fitness App Team</p>
            </div>
          </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email with Gmail
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"[SUCCESS] Password reset email sent to {email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] Gmail authentication failed. Check your SMTP_USERNAME and SMTP_PASSWORD in .env file")
        print(f"[ERROR] Details: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to send password reset email: {e}")
        return False

