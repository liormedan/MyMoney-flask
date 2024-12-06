import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # הגדרות מייל
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Firebase Configuration
    FIREBASE_API_KEY = "AIzaSyACI5ah9xTqB98mmgcAFOIrCE35skvZT68"
    FIREBASE_AUTH_DOMAIN = "mymoney-react-6b771.firebaseapp.com"
    FIREBASE_PROJECT_ID = "mymoney-react-6b771"
    FIREBASE_STORAGE_BUCKET = "mymoney-react-6b771.appspot.com"
    FIREBASE_MESSAGING_SENDER_ID = "309898430150"
    FIREBASE_APP_ID = "1:309898430150:web:f933d0e0a6054974e179c7"
    
    # Firebase Admin Configuration
    FIREBASE_ADMIN_TYPE = "service_account"
    FIREBASE_ADMIN_PROJECT_ID = "mymoney-react-6b771"
    FIREBASE_ADMIN_PRIVATE_KEY_ID = os.environ.get('FIREBASE_ADMIN_PRIVATE_KEY_ID')
    FIREBASE_ADMIN_PRIVATE_KEY = os.environ.get('FIREBASE_ADMIN_PRIVATE_KEY')
    FIREBASE_ADMIN_CLIENT_EMAIL = os.environ.get('FIREBASE_ADMIN_CLIENT_EMAIL')
    FIREBASE_ADMIN_CLIENT_ID = os.environ.get('FIREBASE_ADMIN_CLIENT_ID')
    FIREBASE_ADMIN_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_ADMIN_TOKEN_URI = "https://oauth2.googleapis.com/token"
    FIREBASE_ADMIN_AUTH_PROVIDER_X509_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_ADMIN_CLIENT_X509_CERT_URL = os.environ.get('FIREBASE_ADMIN_CLIENT_X509_CERT_URL')
