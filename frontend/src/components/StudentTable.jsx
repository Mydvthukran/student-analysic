import React, { useState, useEffect } from 'react';
import { Search, Trash2, ChevronLeft, ChevronRight, Filter } from 'lucide-react';

const StudentTable = ({ apiHost, refreshTrigger }) => {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [riskLevel, setRiskLevel] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalStudents, setTotalStudents] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStudents = async () => {
    setLoading(true);
    setError(null);
    try {
      const url = new URL(`${apiHost}/api/students`);
      url.searchParams.append('page', page);
      url.searchParams.append('search', search);
      url.searchParams.append('risk_level', riskLevel);
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch student directory');
      }
      
      setStudents(data.students);
      setTotalPages(data.total_pages);
      setTotalStudents(data.total_students);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [page, riskLevel, refreshTrigger]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchStudents();
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this student record?")) {
      return;
    }
    
    try {
      const response = await fetch(`${apiHost}/api/students/${id}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to delete record');
      }
      
      // Refresh
      fetchStudents();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="animated-fade">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h2 text-gradient fw-bold mb-0">Student Directory</h1>
          <p className="text-muted">Browse historical student data and model prediction results.</p>
        </div>
        <span className="badge bg-secondary px-3 py-2 fs-6">
          Total Records: {totalStudents}
        </span>
      </div>

      {/* Filters & Search Header */}
      <div className="glass-card p-3 mb-4">
        <form onSubmit={handleSearchSubmit} className="row g-2 align-items-center">
          {/* Search bar */}
          <div className="col-12 col-md-5 col-lg-6">
            <div className="input-group">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by student name or ID..."
                className="form-control form-control-custom"
              />
              <button type="submit" className="btn btn-primary-custom d-flex align-items-center gap-1">
                <Search size={16} />
                <span>Search</span>
              </button>
            </div>
          </div>

          {/* Risk Level Filter */}
          <div className="col-12 col-md-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-text bg-dark border-secondary border-opacity-25 text-secondary">
                <Filter size={16} />
              </span>
              <select
                value={riskLevel}
                onChange={(e) => {
                  setRiskLevel(e.target.value);
                  setPage(1);
                }}
                className="form-select form-control-custom"
              >
                <option value="">All Risk Profiles</option>
                <option value="Low">Low Risk Only</option>
                <option value="Medium">Medium Risk Only</option>
                <option value="High">High Risk Only</option>
              </select>
            </div>
          </div>

          {/* Reset button */}
          <div className="col-12 col-md-3 col-lg-2">
            <button
              type="button"
              onClick={() => {
                setSearch('');
                setRiskLevel('');
                setPage(1);
                // Trigger immediate reload
                setTimeout(() => fetchStudents(), 0);
              }}
              className="btn btn-outline-secondary w-100 py-2 border-opacity-25"
            >
              Reset Filters
            </button>
          </div>
        </form>
      </div>

      {/* Student Table Card */}
      <div className="glass-card p-0 overflow-hidden mb-4">
        {loading ? (
          <div className="text-center p-5 text-muted">
            <div className="spinner-border text-primary mb-2" role="status"></div>
            <div>Loading student records...</div>
          </div>
        ) : error ? (
          <div className="text-center p-5 text-danger small">
            Error loading directory: {error}
          </div>
        ) : students.length === 0 ? (
          <div className="text-center p-5 text-muted">
            No student records found matching the filters.
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table table-custom mb-0">
              <thead>
                <tr>
                  <th>StudentID</th>
                  <th>Name</th>
                  <th>Attendance</th>
                  <th>Study Time</th>
                  <th>Failures</th>
                  <th>Predicted Grade</th>
                  <th>Risk Profile</th>
                  <th className="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.map((stu) => (
                  <tr key={stu.id}>
                    <td className="font-monospace text-secondary">{stu.student_id}</td>
                    <td className="fw-bold">{stu.name}</td>
                    <td>{stu.attendance_rate}%</td>
                    <td>{stu.study_time_weekly} hrs/wk</td>
                    <td>
                      <span className={stu.failures > 0 ? "text-danger fw-bold" : "text-muted"}>
                        {stu.failures}
                      </span>
                    </td>
                    <td className="fw-bold text-gradient">{stu.predicted_grade}%</td>
                    <td>
                      <span className={`badge-risk badge-risk-${stu.risk_level.toLowerCase()}`}>
                        {stu.risk_level}
                      </span>
                    </td>
                    <td className="text-end">
                      <button
                        onClick={() => handleDelete(stu.id)}
                        className="btn btn-sm btn-outline-danger border-opacity-25 p-2 hover-bg-danger"
                        title="Delete Record"
                      >
                        <Trash2 size={15} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="d-flex justify-content-between align-items-center mb-4">
          <span className="small text-secondary">
            Page {page} of {totalPages}
          </span>
          <div className="btn-group gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="btn btn-sm btn-outline-secondary d-flex align-items-center border-opacity-25"
            >
              <ChevronLeft size={16} />
              <span>Prev</span>
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="btn btn-sm btn-outline-secondary d-flex align-items-center border-opacity-25"
            >
              <span>Next</span>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentTable;
