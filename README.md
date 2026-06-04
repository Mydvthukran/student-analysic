# Predictive Student Performance Analysis System

An end-to-end Machine Learning web application designed to predict student academic performance and classify students into risk profiles (Low, Medium, High). It enables educational advisors to monitor student cohorts, run single-student predictions, perform batch prediction uploads (via CSV), and receive automated intervention recommendations.

---

## 🛠️ Technology Stack

* **Frontend**: React, Bootstrap 5, Recharts (Interactive charts), Lucide Icons, Vite
* **Backend**: Python 3.13, Flask, SQLite / PostgreSQL (via SQLAlchemy ORM), Flask-CORS
* **Machine Learning**: Scikit-Learn (Random Forests for regression and classification), Pandas, NumPy
* **Visualization**: Matplotlib, Seaborn (Static model training report plots)
* **Development**: Jupyter Notebook

---

## 📁 Directory Structure

```
student-analysis/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app creation & DB seeding
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # Student Database schema
│   │   ├── routes.py            # REST API endpoints
│   │   ├── static/              # Serves static Seaborn/Matplotlib plots
│   │   └── ml/
│   │       ├── train.py         # Trains regression and classification RF pipelines
│   │       ├── predict.py       # Inference wrapper & recommendation logic
│   │       └── models/
│   │           └── model.joblib # Serialized model pipeline
│   ├── config.py                # Server configs (DB URI, uploads)
│   ├── requirements.txt         # Python package list
│   └── run.py                   # Main backend server entry point
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DashboardStats.jsx  # Cohort KPI summary & interactive charts
│   │   │   ├── PredictionForm.jsx  # Single student prediction form
│   │   │   ├── BatchUpload.jsx     # Drag-and-drop CSV batch classifier
│   │   │   └── StudentTable.jsx    # Filterable database directory
│   │   ├── App.jsx                 # Sidebar navigation & view management
│   │   ├── index.css               # Core styling and dark glassmorphic theme
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── notebooks/
│   └── student_performance_analysis.ipynb # EDA & ML model prototyping
├── data/
│   ├── generate_data.py         # Synthetic dataset generator
│   └── student_data.csv         # Generated dataset (1000 records)
└── README.md
```

---

## 📊 Feature Variables

The system predicts performance based on **9 key variables**:
1. **StudyTimeWeekly**: Weekly study hours (0.0 to 30.0).
2. **AttendanceRate**: Attendance rate percentage (40.0% to 100.0%).
3. **SleepHours**: Average daily sleep hours (4.0 to 10.0).
4. **Failures**: Number of past academic course failures (0 to 4).
5. **ParentalSupport**: Level of parental support (0: Low, 1: Medium, 2: High).
6. **Extracurriculars**: Engagement in extracurricular activities (0: No, 1: Yes).
7. **Tutoring**: Attendance in extracurricular tutoring (0: No, 1: Yes).
8. **TestPrepCourse**: Completion of test preparation course (0: No, 1: Yes).
9. **PreviousGrade**: Previous grade percentage (0% to 100%).

### Model Outcomes:
* **Predicted Grade**: Continuous score prediction (0% to 100%).
* **Passing Projections**: Threshold-based classification (Pass: Grade ≥ 60%, Fail: Grade < 60%).
* **Risk Profile**:
  * **High Risk**: Struggle probability ≥ 55%
  * **Medium Risk**: Struggle probability between 25% and 55%
  * **Low Risk**: Struggle probability < 25%

---

## 🚀 Getting Started

### Prerequisites
* **Python** (version 3.10 to 3.13)
* **Node.js** (version 18+)
* **NPM** (version 9+)

---

### Step 1: Backend Setup
1. Open a terminal in the root directory.
2. Initialize virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   * **Windows (PowerShell)**: `venv\Scripts\Activate.ps1`
   * **Windows (CMD)**: `venv\Scripts\activate.bat`
   * **Mac/Linux**: `source venv/bin/activate`
4. Install requirements:
   ```bash
   pip install -r backend/requirements.txt
   ```
5. Run data generator & model training (this creates the database seeds and prebuilt models):
   ```bash
   python data/generate_data.py
   python backend/app/ml/train.py
   ```
6. Start the Flask server:
   ```bash
   python backend/run.py
   ```
   *The backend REST API will start on **http://localhost:5000***.

---

### Step 2: Frontend Setup
1. Open a new terminal in the `frontend/` directory.
2. Install Node packages:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   *The React App will start on **http://localhost:5173***.
