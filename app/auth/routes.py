from flask import render_template, redirect, url_for, flash, request, make_response, jsonify
from app.auth import bp
from app.models import User
from app.firebase_admin import firebase_admin
import pyrebase
from functools import wraps
from datetime import datetime, timedelta
from flask import current_app

# Initialize Pyrebase
firebase_config = {
    "apiKey": "AIzaSyACI5ah9xTqB98mmgcAFOIrCE35skvZT68",
    "authDomain": "mymoney-react-6b771.firebaseapp.com",
    "databaseURL": "https://mymoney-react-6b771-default-rtdb.firebaseio.com",
    "projectId": "mymoney-react-6b771",
    "storageBucket": "mymoney-react-6b771.appspot.com",
    "messagingSenderId": "309898430150",
    "appId": "1:309898430150:web:f933d0e0a6054974e179c7"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def set_secure_cookie(response, name, value, expires=None):
    """Set a secure HTTP-only cookie"""
    if expires is None:
        expires = datetime.utcnow() + timedelta(days=1)
    response.set_cookie(
        name,
        value,
        expires=expires,
        secure=True,  # Only send over HTTPS
        httponly=True,  # Not accessible via JavaScript
        samesite='Strict',  # Protect against CSRF
        path='/'  # Available across the entire site
    )
    return response

@bp.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        is_login = request.form.get('is_login', False)
        
        try:
            if is_login:
                # Sign in with Firebase
                user = auth.sign_in_with_email_and_password(email, password)
                
                # Create or update user in database
                user_data = User.get_by_id(user['localId'])
                if not user_data:
                    user_data = User.create(
                        uid=user['localId'],
                        email=user['email']
                    )
                
                # Create response with redirect
                response = make_response(redirect(url_for('main.index')))
                
                # Set secure cookie with Firebase ID token
                set_secure_cookie(response, 'token', user['idToken'])
                
                return response
                
            else:
                # Create user in Firebase Authentication
                user = auth.create_user_with_email_and_password(email, password)
                
                # Create user in database
                user_data = User.create(
                    uid=user['localId'],
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                
                if user_data:
                    # Sign in the user immediately after registration
                    user = auth.sign_in_with_email_and_password(email, password)
                    
                    # Create response with redirect
                    response = make_response(redirect(url_for('main.index')))
                    
                    # Set secure cookie with Firebase ID token
                    set_secure_cookie(response, 'token', user['idToken'])
                    
                    return response
                else:
                    flash('שגיאה ביצירת המשתמש')
                    return redirect(url_for('auth.auth'))
                    
        except Exception as e:
            if is_login:
                flash('כתובת אימייל או סיסמה שגויים')
            else:
                flash('שגיאה בהרשמה. ייתכן שהמייל כבר קיים במערכת.')
            return redirect(url_for('auth.auth'))
            
    return render_template('auth/auth.html', title='התחברות/הרשמה')

@bp.route('/logout')
def logout():
    response = make_response(redirect(url_for('main.index')))
    response.delete_cookie('token')
    return response

# API Routes for frontend authentication
@bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    try:
        user = auth.sign_in_with_email_and_password(
            data.get('email'),
            data.get('password')
        )
        return jsonify({
            'token': user['idToken'],
            'user': {
                'uid': user['localId'],
                'email': user['email']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    try:
        user = auth.create_user_with_email_and_password(
            data.get('email'),
            data.get('password')
        )
        
        # Create user in database
        user_data = User.create(
            uid=user['localId'],
            email=data.get('email'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        if user_data:
            return jsonify({
                'token': user['idToken'],
                'user': {
                    'uid': user['localId'],
                    'email': user['email'],
                    'first_name': data.get('first_name', ''),
                    'last_name': data.get('last_name', '')
                }
            })
        else:
            return jsonify({'error': 'Error creating user in database'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/verify-token', methods=['POST'])
def verify_token():
    try:
        token = request.json.get('token')
        if not token:
            return jsonify({'error': 'No token provided'}), 400
            
        decoded_token = auth.verify_id_token(token)
        return jsonify({'valid': True, 'uid': decoded_token['uid']})
    except Exception as e:
        return jsonify({'error': str(e)}), 401
