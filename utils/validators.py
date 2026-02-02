from functools import wraps
from flask import request, jsonify, session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
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
