from datetime import datetime
from backend.app.database import db

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    
    # ML Features
    study_time_weekly = db.Column(db.Float, nullable=False)
    attendance_rate = db.Column(db.Float, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    failures = db.Column(db.Integer, nullable=False, default=0)
    parental_support = db.Column(db.Integer, nullable=False, default=1)  # 0: Low, 1: Medium, 2: High
    extracurriculars = db.Column(db.Integer, nullable=False, default=0)    # 0: No, 1: Yes
    tutoring = db.Column(db.Integer, nullable=False, default=0)            # 0: No, 1: Yes
    test_prep_course = db.Column(db.Integer, nullable=False, default=0)    # 0: No, 1: Yes
    previous_grade = db.Column(db.Float, nullable=False)
    
    # Model Predictions
    predicted_grade = db.Column(db.Float, nullable=True)
    predicted_pass = db.Column(db.Integer, nullable=True)        # 0: Fail, 1: Pass
    risk_probability = db.Column(db.Float, nullable=True)        # Probability of Failure (1 - P(Pass))
    risk_level = db.Column(db.String(20), nullable=True)         # 'Low', 'Medium', 'High'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "name": self.name,
            "study_time_weekly": self.study_time_weekly,
            "attendance_rate": self.attendance_rate,
            "sleep_hours": self.sleep_hours,
            "failures": self.failures,
            "parental_support": self.parental_support,
            "extracurriculars": bool(self.extracurriculars),
            "tutoring": bool(self.tutoring),
            "test_prep_course": bool(self.test_prep_course),
            "previous_grade": self.previous_grade,
            "predicted_grade": round(self.predicted_grade, 1) if self.predicted_grade is not None else None,
            "predicted_pass": bool(self.predicted_pass) if self.predicted_pass is not None else None,
            "risk_probability": round(self.risk_probability * 100, 1) if self.risk_probability is not None else None,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat()
        }
