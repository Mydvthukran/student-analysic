import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, BarChart, FileSpreadsheet, Download } from 'lucide-react';

const BatchUpload = ({ apiHost, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'text/csv' && !selectedFile.name.endsWith('.csv')) {
        setError('Please select a valid CSV file.');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiHost}/api/predict/batch`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Server error during batch prediction');
      }

      setResults(data);
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper to trigger dummy download of the CSV template
  const downloadTemplate = () => {
    const csvContent = 
      "Name,StudyTimeWeekly,AttendanceRate,SleepHours,Failures,ParentalSupport,Extracurriculars,Tutoring,TestPrepCourse,PreviousGrade\n" +
      "John Doe,15.5,92,7.5,0,2,1,0,1,84.5\n" +
      "Jane Smith,8.2,74.5,6,1,0,0,1,0,58.0\n" +
      "Alex Johnson,19.0,88,8,0,1,1,1,0,72.3\n";
      
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "student_template.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="animated-fade row g-4">
      <div className="col-12">
        <h1 className="h2 text-gradient fw-bold mb-0">Batch Predictions</h1>
        <p className="text-muted">Upload student cohort datasets in CSV format for automated mass-risk classification.</p>
      </div>

      {/* Upload Zone Card */}
      <div className="col-12 col-lg-5">
        <div className="glass-card p-4 h-100 d-flex flex-column justify-content-between">
          <div>
            <h5 className="fw-bold mb-3">Upload Cohort Dataset</h5>
            <p className="text-secondary small">
              Upload a `.csv` spreadsheet containing your student records. The file must match the required columns structure.
            </p>

            <form onSubmit={handleUpload} className="my-4">
              <div className="border border-dashed border-secondary border-opacity-50 rounded-3 p-4 text-center bg-dark bg-opacity-25 hover-border">
                <input 
                  type="file" 
                  id="csvFileInput" 
                  accept=".csv" 
                  onChange={handleFileChange} 
                  className="d-none" 
                />
                <label htmlFor="csvFileInput" style={{ cursor: 'pointer' }} className="w-100 mb-0">
                  <Upload size={36} className="text-gradient mb-3" />
                  <p className="mb-1 fw-bold small">
                    {file ? file.name : "Click to select CSV File"}
                  </p>
                  <p className="text-secondary small mb-0">Max size: 16 MB</p>
                </label>
              </div>

              {file && (
                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-primary-custom w-100 mt-3 py-2 d-flex align-items-center justify-content-center gap-2"
                >
                  {loading ? (
                    <div className="spinner-border spinner-border-sm text-light" role="status"></div>
                  ) : (
                    <>
                      <BarChart size={18} />
                      <span>Run Batch Analysis</span>
                    </>
                  )}
                </button>
              )}
            </form>

            {error && <div className="alert alert-danger py-2 small">{error}</div>}
          </div>

          {/* Template Download Option */}
          <div className="border border-secondary border-opacity-25 rounded p-3 bg-dark bg-opacity-10 mt-3">
            <div className="d-flex align-items-center justify-content-between">
              <div className="d-flex align-items-center gap-2">
                <FileSpreadsheet className="text-success" size={24} />
                <div>
                  <strong className="small d-block">CSV Template</strong>
                  <span className="text-muted small">Required format details</span>
                </div>
              </div>
              <button 
                type="button" 
                onClick={downloadTemplate}
                className="btn btn-sm btn-outline-light d-flex align-items-center gap-1"
              >
                <Download size={14} />
                <span className="small">Get Template</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Batch Results View Card */}
      <div className="col-12 col-lg-7">
        <div className="glass-card p-4 h-100">
          {!results ? (
            <div className="text-center p-5 text-muted d-flex flex-column align-items-center justify-content-center h-100">
              <FileText size={48} className="mb-3 text-secondary opacity-50" />
              <h5>Batch Results Preview</h5>
              <p className="small max-w-400">
                After uploading your student CSV file, key cohort performance indicators, passing projections, and individual risk reports will display here.
              </p>
            </div>
          ) : (
            <div className="animated-fade">
              <h5 className="fw-bold mb-3 d-flex align-items-center gap-2">
                <CheckCircle className="text-success" size={20} />
                <span>Analysis Complete</span>
              </h5>
              
              {/* Stats Summary Grid */}
              <div className="row g-3 mb-4 text-center">
                <div className="col-4">
                  <div className="bg-dark bg-opacity-50 p-3 rounded border border-secondary border-opacity-25">
                    <span className="text-muted small d-block mb-1">PROCESSED</span>
                    <strong className="fs-5">{results.total_records}</strong>
                  </div>
                </div>
                <div className="col-4">
                  <div className="bg-dark bg-opacity-50 p-3 rounded border border-secondary border-opacity-25">
                    <span className="text-muted small d-block mb-1">PASS RATE</span>
                    <strong className="fs-5 text-success">
                      {((results.passed / results.total_records) * 100).toFixed(0)}%
                    </strong>
                  </div>
                </div>
                <div className="col-4">
                  <div className="bg-dark bg-opacity-50 p-3 rounded border border-secondary border-opacity-25">
                    <span className="text-muted small d-block mb-1">AVG GRADE</span>
                    <strong className="fs-5 text-gradient">{results.average_predicted_grade}%</strong>
                  </div>
                </div>
              </div>

              {/* Risk Summary Cards */}
              <div className="row g-3 mb-4">
                <div className="col-4">
                  <div className="p-2 text-center rounded border border-success border-opacity-25 bg-success bg-opacity-10">
                    <span className="text-success small d-block fw-bold">LOW RISK</span>
                    <strong className="text-success fs-5">{results.risk_counts.Low}</strong>
                  </div>
                </div>
                <div className="col-4">
                  <div className="p-2 text-center rounded border border-warning border-opacity-25 bg-warning bg-opacity-10">
                    <span className="text-warning small d-block fw-bold">MEDIUM RISK</span>
                    <strong className="text-warning fs-5">{results.risk_counts.Medium}</strong>
                  </div>
                </div>
                <div className="col-4">
                  <div className="p-2 text-center rounded border border-danger border-opacity-25 bg-danger bg-opacity-10">
                    <span className="text-danger small d-block fw-bold">HIGH RISK</span>
                    <strong className="text-danger fs-5">{results.risk_counts.High}</strong>
                  </div>
                </div>
              </div>

              {/* Cohort Table Preview */}
              <h6 className="fw-bold text-secondary mb-2 small">PREDICTED COHORT PREVIEW (FIRST 5)</h6>
              <div className="table-responsive">
                <table className="table table-custom mb-0 small">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Predicted Grade</th>
                      <th>Risk Level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.predictions.slice(0, 5).map((stu, i) => (
                      <tr key={i}>
                        <td className="font-monospace text-secondary">{stu.student_id}</td>
                        <td className="fw-bold">{stu.name}</td>
                        <td>{stu.predicted_grade}%</td>
                        <td>
                          <span className={`badge-risk badge-risk-${stu.risk_level.toLowerCase()}`}>
                            {stu.risk_level}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BatchUpload;
