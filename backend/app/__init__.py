import os
import pandas as pd
from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.app.database import db, init_db

def create_app(config_class=Config):
    # Initialize Flask app
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize Database
    init_db(app)
    
    # Register blueprints
    from backend.app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Seed database if empty
    with app.app_context():
        seed_database()
        
    return app

def seed_database():
    from backend.app.models import Student
    
    # Check if we already have records
    if Student.query.count() > 0:
        print("Database already contains data. Skipping seeding.")
        return
        
    csv_path = os.path.join(os.path.dirname(__file__), "../../data/student_data.csv")
    if not os.path.exists(csv_path):
        print(f"Seeding dataset not found at {csv_path}. Skipping seeding.")
        return
        
    print("Seeding database with initial student data...")
    try:
        df = pd.read_csv(csv_path)
        
        # We need to run predictions to fill the predicted fields
        from backend.app.ml.predict import predict_batch
        df_pred = predict_batch(df)
        
        students_to_add = []
        for index, row in df_pred.iterrows():
            student = Student(
                student_id=row["StudentID"],
                name=row["Name"],
                study_time_weekly=float(row["StudyTimeWeekly"]),
                attendance_rate=float(row["AttendanceRate"]),
                sleep_hours=float(row["SleepHours"]),
                failures=int(row["Failures"]),
                parental_support=int(row["ParentalSupport"]),
                extracurriculars=int(row["Extracurriculars"]),
                tutoring=int(row["Tutoring"]),
                test_prep_course=int(row["TestPrepCourse"]),
                previous_grade=float(row["PreviousGrade"]),
                predicted_grade=float(row["predicted_grade"]),
                predicted_pass=int(row["predicted_pass"]),
                risk_probability=float(row["risk_probability"]),
                risk_level=row["risk_level"]
            )
            students_to_add.append(student)
            
        # Bulk save
        db.session.bulk_save_objects(students_to_add)
        db.session.commit()
        print(f"Successfully seeded database with {len(students_to_add)} student records!")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to seed database: {str(e)}")
