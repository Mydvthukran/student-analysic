from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    from backend.app.models import Student  # Import here to register models before create_all
    with app.app_context():
        db.create_all()

