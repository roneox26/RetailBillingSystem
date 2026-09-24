from functools import wraps
from flask import request, jsonify, session, redirect, url_for
import re

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_json(*expected_args):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            missing = [arg for arg in expected_args if arg not in data]
            if missing:
                return jsonify({'status': 'error', 'message': f'Missing fields: {", ".join(missing)}'}), 400
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_positive_number(value, field_name):
    try:
        num = float(value)
        if num <= 0:
            raise ValueError(f'{field_name} must be positive')
        return num
    except (ValueError, TypeError):
        raise ValueError(f'Invalid {field_name}')

def validate_password(password):
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters')
    if not re.search(r'[A-Za-z]', password):
        raise ValueError('Password must contain at least one letter')
    if not re.search(r'[0-9]', password):
        raise ValueError('Password must contain at least one number')
    return True
