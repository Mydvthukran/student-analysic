import React, { useState } from 'react';
import { AlertCircle, CheckCircle, HelpCircle, FileText, ChevronRight, User } from 'lucide-react';

const PredictionForm = ({ apiHost, onPredictionSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    study_time_weekly: 10,
    attendance_rate: 85,
    sleep_hours: 7,
    failures: 0,
    parental_support: 1, // Medium
    extracurriculars: 0,
    tutoring: 0,
    test_prep_course: 0,
    previous_grade: 75
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    let finalValue = value;
    
    if (type === 'checkbox') {
      finalValue = checked ? 1 : 0;
    } else if (type === 'number' || name === 'study_time_weekly' || name === 'attendance_rate' || name === 'sleep_hours' || name === 'previous_grade') {
      finalValue = parseFloat(value) || 0;
    } else if (name === 'failures' || name === 'parental_support' || name === 'extracurriculars' || name === 'tutoring' || name === 'test_prep_course') {
      finalValue = parseInt(value, 10);
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: finalValue
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    if (!formData.name.trim()) {
      setError("Please enter the student's name.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${apiHost}/api/predict/single`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Server error during prediction');
      }
      
      setResult(data);
      if (onPredictionSuccess) {
        onPredictionSuccess();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animated-fade row g-4">
      <div className="col-12">
        <h1 className="h2 text-gradient fw-bold mb-0">Predict Student Performance</h1>
        <p className="text-muted">Enter student metrics to predict grades and analyze academic risk.</p>
      </div>

      {/* Input Form Card */}
      <div className="col-12 col-lg-7">
        <div className="glass-card p-4">
          <h5 className="fw-bold mb-4">Student Assessment Metrics</h5>
          
          <form onSubmit={handleSubmit}>
            <div className="row g-3">
              {/* Name */}
              <div className="col-12">
                <label className="form-label text-secondary small fw-bold">Student Name</label>
                <div className="input-group">
                  <span className="input-group-text bg-dark border-secondary border-opacity-25 text-secondary">
                    <User size={18} />
                  </span>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className="form-control form-control-custom"
                    placeholder="Enter student's full name"
                    required
                  />
                </div>
              </div>

              {/* Study Time */}
              <div className="col-12 col-md-6">
                <label className="form-label text-secondary small fw-bold d-flex justify-content-between">
                  <span>Weekly Study Hours</span>
                  <span className="text-gradient fw-bold">{formData.study_time_weekly} hrs</span>
                </label>
                <input
                  type="range"
                  name="study_time_weekly"
                  min="0"
                  max="30"
                  step="0.5"
                  value={formData.study_time_weekly}
                  onChange={handleChange}
                  className="form-range"
                />
              </div>

              {/* Attendance */}
              <div className="col-12 col-md-6">
                <label className="form-label text-secondary small fw-bold d-flex justify-content-between">
                  <span>Attendance Rate</span>
                  <span className="text-gradient fw-bold">{formData.attendance_rate}%</span>
                </label>
                <input
                  type="range"
                  name="attendance_rate"
                  min="40"
                  max="100"
                  step="1"
                  value={formData.attendance_rate}
                  onChange={handleChange}
                  className="form-range"
                />
              </div>

              {/* Sleep Hours */}
              <div className="col-12 col-md-6">
                <label className="form-label text-secondary small fw-bold d-flex justify-content-between">
                  <span>Average Daily Sleep</span>
                  <span className="text-gradient fw-bold">{formData.sleep_hours} hrs</span>
                </label>
                <input
                  type="range"
                  name="sleep_hours"
                  min="4"
                  max="12"
                  step="0.5"
                  value={formData.sleep_hours}
                  onChange={handleChange}
                  className="form-range"
                />
              </div>

              {/* Previous Grade */}
              <div className="col-12 col-md-6">
                <label className="form-label text-secondary small fw-bold">Previous Term Grade (%)</label>
                <input
                  type="number"
                  name="previous_grade"
                  min="0"
                  max="100"
                  value={formData.previous_grade}
                  onChange={handleChange}
                  className="form-control form-control-custom"
                  required
                />
              </div>

              {/* Failures */}
              <div className="col-12 col-md-6">
                <label className="form-label text-secondary small fw-bold">Past Academic Failures</label>
                <select
                  name="failures"
                  value={formData.failures}
                  onChange={handleChange}
                  className="form-select form-control-custom"
                >
                  <option value={0}>0 Failures</option>
                  <option value={1}>1 Failure</option>
                  <option value={2}>2 Failures</option>
                  <option value={3}>3 Failures</option>
                  <option value={4}>4+ Failures</option>
                </select>
              </div>

              {/* Parental Support */}
              <div className="col-12 col-md-6">
                <label className="form-label text-secondary small fw-bold">Parental Support Level</label>
                <select
                  name="parental_support"
                  value={formData.parental_support}
                  onChange={handleChange}
                  className="form-select form-control-custom"
                >
                  <option value={0}>Low Support</option>
                  <option value={1}>Medium Support</option>
                  <option value={2}>High Support</option>
                </select>
              </div>

              {/* Binary Switches (Grid) */}
              <div className="col-12 mt-4">
                <h6 className="text-secondary small fw-bold mb-3">Academic Enhancements</h6>
                <div className="row g-3">
                  <div className="col-4">
                    <div className="form-check form-switch">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        name="tutoring"
                        id="tutoringSwitch"
                        checked={formData.tutoring === 1}
                        onChange={(e) => setFormData(p => ({ ...p, tutoring: e.target.checked ? 1 : 0 }))}
                      />
                      <label className="form-check-label text-secondary small" htmlFor="tutoringSwitch">
                        Tutoring
                      </label>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="form-check form-switch">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        name="test_prep_course"
                        id="testPrepSwitch"
                        checked={formData.test_prep_course === 1}
                        onChange={(e) => setFormData(p => ({ ...p, test_prep_course: e.target.checked ? 1 : 0 }))}
                      />
                      <label className="form-check-label text-secondary small" htmlFor="testPrepSwitch">
                        Test Prep
                      </label>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="form-check form-switch">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        name="extracurriculars"
                        id="extracurricularsSwitch"
                        checked={formData.extracurriculars === 1}
                        onChange={(e) => setFormData(p => ({ ...p, extracurriculars: e.target.checked ? 1 : 0 }))}
                      />
                      <label className="form-check-label text-secondary small" htmlFor="extracurricularsSwitch">
                        Activities
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              {/* Submit */}
              <div className="col-12 mt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-primary-custom w-100 py-3 d-flex align-items-center justify-content-center gap-2"
                >
                  {loading ? (
                    <div className="spinner-border spinner-border-sm text-light" role="status"></div>
                  ) : (
                    <>
                      <span>Predict Student Outcome</span>
                      <ChevronRight size={18} />
                    </>
                  )}
                </button>
              </div>

            </div>
          </form>
          {error && <div className="alert alert-danger mt-3 mb-0 py-2 small">{error}</div>}
        </div>
      </div>

      {/* Results View Card */}
      <div className="col-12 col-lg-5">
        <div className="glass-card p-4 h-100 d-flex flex-column justify-content-center">
          {!result ? (
            <div className="text-center p-5 text-muted">
              <FileText size={48} className="mb-3 text-secondary opacity-50" />
              <h5>Assessment Ready</h5>
              <p className="small">Fill the form and submit to receive deep analytics, grading predictions, and custom advisor interventions.</p>
            </div>
          ) : (
            <div className="animated-fade">
              <h5 className="fw-bold mb-4">Risk & Performance Analysis</h5>
              
              <div className="text-center mb-4">
                <p className="text-muted small mb-1">PREDICTED GRADE</p>
                <div className="display-4 fw-bold text-gradient">{result.predicted_grade}%</div>
                
                {/* Risk Level Badge */}
                <div className="mt-2">
                  <span className={`badge-risk badge-risk-${result.risk_level.toLowerCase()}`}>
                    {result.risk_level} Risk Level
                  </span>
                </div>
              </div>

              {/* Risk Gauge Bar */}
              <div className="mb-4">
                <div className="d-flex justify-content-between small text-secondary mb-1">
                  <span>Probability of Academic Struggle</span>
                  <span className="fw-bold">{result.risk_probability}%</span>
                </div>
                <div className="progress bg-dark" style={{ height: 10 }}>
                  <div 
                    className={`progress-bar rounded-pill ${
                      result.risk_level === 'High' ? 'bg-danger' : 
                      result.risk_level === 'Medium' ? 'bg-warning' : 'bg-success'
                    }`} 
                    role="progressbar" 
                    style={{ width: `${result.risk_probability}%` }}
                    aria-valuenow={result.risk_probability} 
                    aria-valuemin="0" 
                    aria-valuemax="100"
                  ></div>
                </div>
              </div>

              {/* Outcome Badge */}
              <div className="d-flex align-items-center gap-2 p-3 bg-dark rounded border border-secondary border-opacity-25 mb-4">
                {result.predicted_pass ? (
                  <>
                    <CheckCircle className="text-success" size={24} />
                    <div>
                      <strong className="text-success d-block small">PASSING OUTCOME PREDICTED</strong>
                      <span className="text-muted small">Target grade is above threshold.</span>
                    </div>
                  </>
                ) : (
                  <>
                    <AlertCircle className="text-danger" size={24} />
                    <div>
                      <strong className="text-danger d-block small">FAILING OUTCOME PREDICTED</strong>
                      <span className="text-muted small">Target grade lies below 60%.</span>
                    </div>
                  </>
                )}
              </div>

              {/* Intervention Recommendations */}
              <h6 className="fw-bold text-secondary mb-2 small">RECONSTRUCTED INTERVENTIONS</h6>
              <ul className="list-unstyled mb-0">
                {result.suggestions.map((suggestion, index) => (
                  <li key={index} className="small d-flex gap-2 mb-2 align-items-start">
                    <span className="text-gradient fw-bold">•</span>
                    <span className="text-muted">{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PredictionForm;
