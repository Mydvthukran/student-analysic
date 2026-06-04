import os

class Config:
    # Secret Key for session/cookies
    SECRET_KEY = os.environ.get('SECRET_KEY', 'student-analysis-secret-key-12345')
    
    # Database configuration
    # Default to SQLite, override with DATABASE_URL for PostgreSQL/MySQL
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'student_analysis.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DEFAULT_DB_PATH}')
    
    # Fix potential Heroku/Render postgres:// URI issue
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for batch imports
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
