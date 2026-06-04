import os
import joblib
import pandas as pd
import numpy as np

# Global variables to hold loaded models
_model_payload = None

def load_models():
    global _model_payload
    if _model_payload is None:
        model_path = os.path.join(os.path.dirname(__file__), "models", "model.joblib")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please train the model first.")
        _model_payload = joblib.load(model_path)
    return _model_payload

def get_intervention_suggestions(risk_level, features):
    """
    Returns custom suggestions based on risk levels and specific features.
    """
    suggestions = []
    
    if risk_level == "High":
        suggestions.append("Immediate academic counseling and mentor assignment.")
        suggestions.append("Create a mandatory structured study schedule (minimum 15 hours/week).")
    elif risk_level == "Medium":
        suggestions.append("Schedule a check-in with the subject teacher or advisor.")
        suggestions.append("Enroll in peer-led study groups.")
        
    # Check individual problem areas
    if features.get("AttendanceRate", 100) < 80:
        suggestions.append(f"Flagged Attendance: Current attendance is {features['AttendanceRate']}%. Recommend parental notification and attendance contract.")
        
    if features.get("StudyTimeWeekly", 15) < 8:
        suggestions.append(f"Low Study Time: Student reports only {features['StudyTimeWeekly']} hours of weekly study. Recommend tutoring and supervised study hall.")
        
    if features.get("SleepHours", 8) < 6.5:
        suggestions.append(f"Insufficient Sleep: Averaging {features['SleepHours']} hours of sleep. Counsel on sleep hygiene and time management.")
        
    if features.get("Failures", 0) > 0:
        suggestions.append(f"Prior Failures: Student has {features['Failures']} past failures. Prioritize remedial sessions for core topics.")
        
    if not features.get("TestPrepCourse", False):
        suggestions.append("Encourage completion of the online test preparation course.")
        
    if not features.get("Tutoring", False) and risk_level != "Low":
        suggestions.append("Recommend registering for the school's after-school tutoring program.")
        
    if len(suggestions) == 0:
        suggestions.append("Continue current study patterns. Good academic standing.")
        
    return suggestions

def predict_single(student_features):
    """
    Predicts final grade, pass status, and risk level for a single student.
    student_features: dict with keys matching FEATURE_NAMES
    """
    payload = load_models()
    reg_pipeline = payload["regressor_pipeline"]
    clf_pipeline = payload["classifier_pipeline"]
    feature_names = payload["feature_names"]
    
    # Create DataFrame with a single row
    features_dict = {k: [student_features[k]] for k in feature_names}
    df_in = pd.DataFrame(features_dict)
    
    # Run predictions
    pred_grade = reg_pipeline.predict(df_in)[0]
    pred_pass = clf_pipeline.predict(df_in)[0]
    
    # Get probabilities
    proba_pass = clf_pipeline.predict_proba(df_in)[0][1]
    proba_fail = 1.0 - proba_pass
    
    # Define risk levels
    if proba_fail >= 0.55:
        risk_level = "High"
    elif proba_fail >= 0.25:
        risk_level = "Medium"
    else:
        risk_level = "Low"
        
    suggestions = get_intervention_suggestions(risk_level, student_features)
    
    return {
        "predicted_grade": float(round(pred_grade, 1)),
        "predicted_pass": int(pred_pass),
        "risk_probability": float(proba_fail),
        "risk_level": risk_level,
        "suggestions": suggestions
    }

def predict_batch(df):
    """
    Predicts grades and risks for a DataFrame.
    Returns the DataFrame with additional prediction columns.
    """
    payload = load_models()
    reg_pipeline = payload["regressor_pipeline"]
    clf_pipeline = payload["classifier_pipeline"]
    feature_names = payload["feature_names"]
    
    # Verify features exist in input DataFrame
    missing_cols = [col for col in feature_names if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Input DataFrame is missing required features: {missing_cols}")
        
    X = df[feature_names]
    
    # Predict
    df["predicted_grade"] = np.round(reg_pipeline.predict(X), 1)
    df["predicted_pass"] = clf_pipeline.predict(X)
    
    # Probability of Fail
    proba_pass = clf_pipeline.predict_proba(X)[:, 1]
    proba_fail = 1.0 - proba_pass
    
    df["risk_probability"] = proba_fail
    
    # Map risk level
    conditions = [
        (proba_fail >= 0.55),
        (proba_fail >= 0.25) & (proba_fail < 0.55),
        (proba_fail < 0.25)
    ]
    choices = ["High", "Medium", "Low"]
    df["risk_level"] = np.select(conditions, choices, default="Low")
    
    return df
