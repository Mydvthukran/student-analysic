import os
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report, confusion_matrix

def train_models():
    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), "../../../data/student_data.csv")
    if not os.path.exists(data_path):
        # Generate data if not exists
        print("Dataset not found. Generating dataset first...")
        from data.generate_data import generate_student_data
        df = generate_student_data(1000)
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df.to_csv(data_path, index=False)
    else:
        df = pd.read_csv(data_path)

    # Features and Targets
    feature_cols = [
        "StudyTimeWeekly", "AttendanceRate", "SleepHours", "Failures", 
        "ParentalSupport", "Extracurriculars", "Tutoring", "TestPrepCourse", "PreviousGrade"
    ]
    
    X = df[feature_cols]
    y_grade = df["FinalGrade"]
    y_pass = df["Pass"]
    
    # Train-test split
    X_train, X_test, y_train_grade, y_test_grade = train_test_split(X, y_grade, test_size=0.2, random_state=42)
    _, _, y_train_pass, y_test_pass = train_test_split(X, y_pass, test_size=0.2, random_state=42)
    
    # Preprocessing & Model pipelines
    # 1. Regressor Pipeline
    reg_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, max_depth=8))
    ])
    
    # 2. Classifier Pipeline
    clf_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8))
    ])
    
    # Train regressor
    print("Training Grade Regressor model...")
    reg_pipeline.fit(X_train, y_train_grade)
    y_pred_grade = reg_pipeline.predict(X_test)
    
    mse = mean_squared_error(y_test_grade, y_pred_grade)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test_grade, y_pred_grade)
    print(f"Regressor Results - RMSE: {rmse:.4f}, R2 Score: {r2:.4f}")
    
    # Train classifier
    print("Training Risk Classifier model...")
    clf_pipeline.fit(X_train, y_train_pass)
    y_pred_pass = clf_pipeline.predict(X_test)
    
    acc = accuracy_score(y_test_pass, y_pred_pass)
    report = classification_report(y_test_pass, y_pred_pass, output_dict=True)
    print(f"Classifier Results - Accuracy: {acc:.4f}")
    
    # Feature Importances
    reg_importances = reg_pipeline.named_steps['regressor'].feature_importances_
    clf_importances = clf_pipeline.named_steps['classifier'].feature_importances_
    
    # Save plots for backend reports
    plots_dir = os.path.join(os.path.dirname(__file__), "../static/plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # Plot 1: Feature Importance
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="darkgrid")
    indices = np.argsort(reg_importances)[::-1]
    sorted_features = [feature_cols[i] for i in indices]
    sorted_importances = reg_importances[indices]
    
    # Modern look
    colors = sns.color_palette("viridis", len(sorted_features))
    sns.barplot(x=sorted_importances, y=sorted_features, palette=colors)
    plt.title("Key Predictors of Academic Success (Feature Importance)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Importance Score", fontsize=12)
    plt.ylabel("Features", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "feature_importance.png"), dpi=300)
    plt.close()
    
    # Plot 2: Correlation Matrix
    plt.figure(figsize=(10, 8))
    corr = df[feature_cols + ["FinalGrade"]].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, square=True)
    plt.title("Correlation Analysis Matrix", fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "correlation_matrix.png"), dpi=300)
    plt.close()

    # Plot 3: Attendance vs Final Grade with regression line
    plt.figure(figsize=(8, 6))
    sns.regplot(data=df, x="AttendanceRate", y="FinalGrade", 
                scatter_kws={"alpha": 0.4, "color": "#1f77b4"}, 
                line_kws={"color": "#ff7f0e", "linewidth": 2})
    plt.title("Impact of Attendance on Final Grade", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Attendance Rate (%)")
    plt.ylabel("Final Grade (0-100)")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "attendance_vs_grade.png"), dpi=300)
    plt.close()
    
    # Save the pipeline
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_payload = {
        "regressor_pipeline": reg_pipeline,
        "classifier_pipeline": clf_pipeline,
        "feature_names": feature_cols,
        "metrics": {
            "regressor": {
                "rmse": float(rmse),
                "r2": float(r2)
            },
            "classifier": {
                "accuracy": float(acc),
                "f1_score": float(report["accuracy"]),  # Overall accuracy
                "precision": float(report["weighted avg"]["precision"]),
                "recall": float(report["weighted avg"]["recall"])
            }
        }
    }
    
    joblib.dump(model_payload, os.path.join(models_dir, "model.joblib"))
    print(f"Models and metrics successfully serialized to {os.path.join(models_dir, 'model.joblib')}")

if __name__ == "__main__":
    train_models()
