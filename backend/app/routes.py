import os
import io
import pandas as pd
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from backend.app.database import db
from backend.app.models import Student
from backend.app.ml.predict import predict_single, predict_batch, load_models

api_bp = Blueprint('api', __name__)

# Allowed file extensions for batch upload
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Returns general statistics for the dashboard.
    """
    try:
        # Get counts
        total_students = Student.query.count()
        if total_students == 0:
            return jsonify({
                "total_students": 0,
                "average_predicted_grade": 0.0,
                "average_attendance": 0.0,
                "risk_counts": {"Low": 0, "Medium": 0, "High": 0},
                "pass_fail_counts": {"Pass": 0, "Fail": 0}
            })
            
        avg_grade = db.session.query(db.func.avg(Student.predicted_grade)).scalar() or 0.0
        avg_attendance = db.session.query(db.func.avg(Student.attendance_rate)).scalar() or 0.0
        
        low_risk = Student.query.filter_by(risk_level='Low').count()
        med_risk = Student.query.filter_by(risk_level='Medium').count()
        high_risk = Student.query.filter_by(risk_level='High').count()
        
        passed_students = Student.query.filter_by(predicted_pass=1).count()
        failed_students = Student.query.filter_by(predicted_pass=0).count()
        
        # Monthly/Weekly additions (last 7 additions for trend)
        recent_additions = Student.query.order_by(Student.created_at.desc()).limit(10).all()
        recent_data = [
            {"name": stu.name, "grade": stu.predicted_grade, "risk": stu.risk_level}
            for stu in reversed(recent_additions)
        ]
        
        # Get metrics of trained models
        model_payload = load_models()
        metrics = model_payload.get("metrics", {})
        
        return jsonify({
            "total_students": total_students,
            "average_predicted_grade": round(float(avg_grade), 1),
            "average_attendance": round(float(avg_attendance), 1),
            "risk_counts": {
                "Low": low_risk,
                "Medium": med_risk,
                "High": high_risk
            },
            "pass_fail_counts": {
                "Pass": passed_students,
                "Fail": failed_students
            },
            "recent_predictions": recent_data,
            "model_metrics": metrics
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/students', methods=['GET'])
def get_students():
    """
    Returns list of students with filtering and pagination.
    """
    try:
        search = request.args.get('search', '')
        risk_level = request.args.get('risk_level', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Student.query
        
        if search:
            query = query.filter((Student.name.ilike(f'%{search}%')) | (Student.student_id.ilike(f'%{search}%')))
            
        if risk_level:
            query = query.filter_by(risk_level=risk_level)
            
        # Paginate
        pagination = query.order_by(Student.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        students_list = [student.to_dict() for student in pagination.items]
        
        return jsonify({
            "students": students_list,
            "total_pages": pagination.pages,
            "total_students": pagination.total,
            "current_page": page
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    """
    Deletes a student record by ID.
    """
    try:
        student = Student.query.get_or_404(id)
        db.session.delete(student)
        db.session.commit()
        return jsonify({"success": True, "message": "Student record deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/predict/single', methods=['POST'])
def run_predict_single():
    """
    Accepts single student details, predicts outcome, saves to database, and returns results.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        # Validate required features
        required_fields = [
            "name", "study_time_weekly", "attendance_rate", "sleep_hours", 
            "failures", "parental_support", "extracurriculars", 
            "tutoring", "test_prep_course", "previous_grade"
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
                
        # Structure features for ML pipeline
        features = {
            "StudyTimeWeekly": float(data["study_time_weekly"]),
            "AttendanceRate": float(data["attendance_rate"]),
            "SleepHours": float(data["sleep_hours"]),
            "Failures": int(data["failures"]),
            "ParentalSupport": int(data["parental_support"]),
            "Extracurriculars": int(data["extracurriculars"]),
            "Tutoring": int(data["tutoring"]),
            "TestPrepCourse": int(data["test_prep_course"]),
            "PreviousGrade": float(data["previous_grade"])
        }
        
        # Run prediction
        prediction = predict_single(features)
        
        # Create student_id
        count = Student.query.count()
        student_id = f"STU{1000 + count + 1}"
        
        # Save to DB
        new_student = Student(
            student_id=student_id,
            name=data["name"],
            study_time_weekly=features["StudyTimeWeekly"],
            attendance_rate=features["AttendanceRate"],
            sleep_hours=features["SleepHours"],
            failures=features["Failures"],
            parental_support=features["ParentalSupport"],
            extracurriculars=features["Extracurriculars"],
            tutoring=features["Tutoring"],
            test_prep_course=features["TestPrepCourse"],
            previous_grade=features["PreviousGrade"],
            predicted_grade=prediction["predicted_grade"],
            predicted_pass=prediction["predicted_pass"],
            risk_probability=prediction["risk_probability"],
            risk_level=prediction["risk_level"]
        )
        
        db.session.add(new_student)
        db.session.commit()
        
        # Return prediction + saved student details
        res = new_student.to_dict()
        res["suggestions"] = prediction["suggestions"]
        return jsonify(res), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/predict/batch', methods=['POST'])
def run_predict_batch():
    """
    Accepts CSV upload of student records, predicts all, saves to DB, returns aggregations.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected for uploading"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "Allowed file types is CSV"}), 400
            
        # Parse CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        df_uploaded = pd.read_csv(stream)
        
        # Validate header columns
        expected_cols = [
            "Name", "StudyTimeWeekly", "AttendanceRate", "SleepHours", 
            "Failures", "ParentalSupport", "Extracurriculars", 
            "Tutoring", "TestPrepCourse", "PreviousGrade"
        ]
        
        missing_cols = [col for col in expected_cols if col not in df_uploaded.columns]
        if missing_cols:
            return jsonify({"error": f"CSV is missing required columns: {missing_cols}"}), 400
            
        # Add predictions using pipeline
        df_pred = predict_batch(df_uploaded.copy())
        
        saved_students = []
        count = Student.query.count()
        
        # Save records to database
        for index, row in df_pred.iterrows():
            student_id = row.get("StudentID", f"STU{1000 + count + index + 1}")
            
            # Check if student already exists to avoid unique constraint violations
            existing = Student.query.filter_by(student_id=student_id).first()
            if existing:
                # Update existing
                existing.name = row["Name"]
                existing.study_time_weekly = float(row["StudyTimeWeekly"])
                existing.attendance_rate = float(row["AttendanceRate"])
                existing.sleep_hours = float(row["SleepHours"])
                existing.failures = int(row["Failures"])
                existing.parental_support = int(row["ParentalSupport"])
                existing.extracurriculars = int(row["Extracurriculars"])
                existing.tutoring = int(row["Tutoring"])
                existing.test_prep_course = int(row["TestPrepCourse"])
                existing.previous_grade = float(row["PreviousGrade"])
                existing.predicted_grade = float(row["predicted_grade"])
                existing.predicted_pass = int(row["predicted_pass"])
                existing.risk_probability = float(row["risk_probability"])
                existing.risk_level = row["risk_level"]
                db_student = existing
            else:
                # Create new
                db_student = Student(
                    student_id=student_id,
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
                db.session.add(db_student)
                
            saved_students.append(db_student)
            
        db.session.commit()
        
        # Prepare summaries
        total = len(df_pred)
        passed = int(df_pred["predicted_pass"].sum())
        failed = total - passed
        avg_grade = float(round(df_pred["predicted_grade"].mean(), 1))
        
        risk_counts = df_pred["risk_level"].value_counts().to_dict()
        risk_counts_filled = {
            "Low": int(risk_counts.get("Low", 0)),
            "Medium": int(risk_counts.get("Medium", 0)),
            "High": int(risk_counts.get("High", 0))
        }
        
        return jsonify({
            "success": True,
            "total_records": total,
            "passed": passed,
            "failed": failed,
            "average_predicted_grade": avg_grade,
            "risk_counts": risk_counts_filled,
            "predictions": [s.to_dict() for s in saved_students[:20]]  # Return first 20 records
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/plots/<filename>', methods=['GET'])
def get_plot(filename):
    """
    Serves static Seaborn/Matplotlib generated plots.
    """
    plots_dir = os.path.join(os.path.dirname(__file__), "static", "plots")
    return send_from_directory(plots_dir, filename)
