# backend/routes/auth.py
# Ensure backend/ is on sys.path so imports work when running app.py from backend/
import os, sys
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Blueprint, request, jsonify, current_app
from flask_mail import Mail

# Define blueprint (must exist so app can import auth_bp)
auth_bp = Blueprint('auth', __name__)

# Now import local service modules (they expect get_db_connection etc.)
from services.user_service import (
    create_user,
    authenticate_user,
    update_user_password,
    get_user_by_email
)
from services.otp_service import (
    create_otp_request,
    verify_otp,
    clear_otps
)
from services.email_service import send_otp_email
from utils.jwt_utils import generate_token
from config import Config

def get_mail():
    """Get mail instance from current app"""
    return current_app.mail

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    user = create_user(name, email, password)
    token = generate_token(user)

    return jsonify({'message': 'User created successfully','user': user,'token': token}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = authenticate_user(email, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(user)
    return jsonify({'message': 'Login successful','user': user,'token': token}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({'message': 'If the email exists, an OTP has been sent'}), 200

    otp, expires_at = create_otp_request(email)
    mail = get_mail()
    if send_otp_email(mail, email, otp, expires_at):
        return jsonify({'message': 'OTP sent to your email'}), 200
    else:
        return jsonify({'error': 'Failed to send email'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '').strip()

    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required'}), 400
    if len(otp) != 6:
        return jsonify({'error': 'OTP must be 6 digits'}), 400

    is_valid, message = verify_otp(email, otp)
    if is_valid:
        return jsonify({'message': 'OTP verified successfully'}), 200
    else:
        return jsonify({'error': message}), 400

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '').strip()
    new_password = data.get('password', '')

    if not email or not otp or not new_password:
        return jsonify({'error': 'Email, OTP, and password are required'}), 400
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    is_valid, message = verify_otp(email, otp)
    if not is_valid:
        return jsonify({'error': message}), 400

    update_user_password(email, new_password)
    clear_otps(email)
    return jsonify({'message': 'Password reset successfully'}), 200
