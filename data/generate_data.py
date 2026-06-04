import os
import numpy as np
import pandas as pd

def generate_student_data(num_students=1000, random_seed=42):
    np.random.seed(random_seed)
    
    # Generate random features
    student_ids = [f"STU{1000 + i}" for i in range(num_students)]
    
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
                   "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                   "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
                   "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
                  "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris"]
    
    names = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(num_students)]
    
    study_time = np.random.uniform(2.0, 25.0, num_students)  # hours per week
    attendance = np.random.beta(a=8, b=1.5, size=num_students) * 100  # skewed towards high attendance (70-100)
    # Clip attendance between 40 and 100
    attendance = np.clip(attendance, 40, 100)
    
    sleep_hours = np.random.normal(7.0, 1.2, num_students)
    sleep_hours = np.clip(sleep_hours, 4, 10)
    
    # Failures: higher probability of 0, lower probability of 1, 2, 3, 4
    failures = np.random.choice([0, 1, 2, 3, 4], size=num_students, p=[0.75, 0.15, 0.06, 0.03, 0.01])
    
    # Support levels: 0 (Low), 1 (Medium), 2 (High)
    parental_support = np.random.choice([0, 1, 2], size=num_students, p=[0.2, 0.5, 0.3])
    
    # Binary variables
    extracurriculars = np.random.choice([0, 1], size=num_students, p=[0.4, 0.6])
    tutoring = np.random.choice([0, 1], size=num_students, p=[0.7, 0.3])
    test_prep = np.random.choice([0, 1], size=num_students, p=[0.65, 0.35])
    
    # Previous grade: base previous grade (mean 72, std 12)
    previous_grade = np.random.normal(70, 12, num_students)
    # Correlate previous grade with study time and attendance a bit
    previous_grade += (study_time - 12) * 0.8 + (attendance - 85) * 0.15
    previous_grade = np.clip(previous_grade, 45, 98)
    
    # Generate final grade based on a linear combination + noise
    # Base grade
    final_grade = 45.0
    # Coefficients
    final_grade += (previous_grade - 50) * 0.45
    final_grade += (study_time - 10) * 0.8
    final_grade += (attendance - 80) * 0.25
    final_grade += (sleep_hours - 7) * 1.2
    final_grade += (parental_support - 1) * 2.5
    final_grade += tutoring * 3.5
    final_grade += test_prep * 4.0
    final_grade -= failures * 6.5
    final_grade += (extracurriculars - 0.5) * 1.0
    
    # Add random noise
    final_grade += np.random.normal(0, 4.0, num_students)
    
    # Clip final grade to be between 0 and 100
    final_grade = np.round(np.clip(final_grade, 0, 100), 1)
    
    # Pass status: final grade >= 60
    pass_status = (final_grade >= 60).astype(int)
    
    # Create DataFrame
    df = pd.DataFrame({
        "StudentID": student_ids,
        "Name": names,
        "StudyTimeWeekly": np.round(study_time, 1),
        "AttendanceRate": np.round(attendance, 1),
        "SleepHours": np.round(sleep_hours, 1),
        "Failures": failures,
        "ParentalSupport": parental_support,
        "Extracurriculars": extracurriculars,
        "Tutoring": tutoring,
        "TestPrepCourse": test_prep,
        "PreviousGrade": np.round(previous_grade, 1),
        "FinalGrade": final_grade,
        "Pass": pass_status
    })
    
    return df

if __name__ == "__main__":
    df = generate_student_data(1000)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/student_data.csv", index=False)
    print(f"Generated synthetic student performance dataset with {len(df)} records at data/student_data.csv")
    print(df.head())
