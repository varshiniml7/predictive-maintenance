from flask_mail import Message
from flask import current_app
from config import Config

def send_otp_email(mail, email, otp, expires_at):
    """Send OTP email to user"""
    try:
        subject = "Your Password Reset OTP"
        body = f"""
        Your password reset OTP is: {otp}
        
        This OTP will expire in {Config.OTP_EXPIRATION_MINUTES} minutes.
        
        If you didn't request this, please ignore this email.
        """
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Password Reset OTP</h2>
            <p>Your password reset OTP is: <strong style="font-size: 24px; color: #007bff;">{otp}</strong></p>
            <p>This OTP will expire in {Config.OTP_EXPIRATION_MINUTES} minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[email],
            body=body,
            html=html,
            sender=Config.MAIL_DEFAULT_SENDER
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
