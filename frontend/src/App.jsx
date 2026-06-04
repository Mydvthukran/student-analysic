import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, FileText, Upload, Database, 
  GraduationCap
} from 'lucide-react';
import DashboardStats from './components/DashboardStats';
import PredictionForm from './components/PredictionForm';
import BatchUpload from './components/BatchUpload';
import StudentTable from './components/StudentTable';

const API_HOST = 'http://localhost:5000';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_HOST}/api/dashboard/stats`);
      const data = await response.json();
      if (response.ok) {
        setStats(data);
      }
    } catch (err) {
      console.error("Error fetching dashboard statistics:", err);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [refreshTrigger]);

  const triggerRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="container-fluid p-0 d-flex flex-column flex-md-row min-vh-100">
      
      {/* Sidebar Navigation */}
      <aside className="col-12 col-md-3 col-xl-2 sidebar p-3 d-flex flex-column justify-content-between">
        <div>
          {/* Logo Brand */}
          <div className="d-flex align-items-center gap-2 mb-4 px-2 py-3 border-bottom border-secondary border-opacity-25">
            <div className="bg-primary bg-opacity-10 p-2 rounded text-primary">
              <GraduationCap size={28} className="text-gradient" />
            </div>
            <div>
              <h5 className="fw-bold mb-0 text-white leading-tight">Antigravity</h5>
              <span className="text-secondary small fw-bold text-uppercase tracking-wider" style={{ fontSize: '0.65rem' }}>
                Academic ML Predict
              </span>
            </div>
          </div>

          {/* Nav Menu */}
          <nav className="nav flex-column">
            <a 
              href="#dashboard" 
              onClick={() => setActiveTab('dashboard')}
              className={`nav-link-custom ${activeTab === 'dashboard' ? 'active' : ''}`}
            >
              <LayoutDashboard size={20} />
              <span>Dashboard</span>
            </a>
            <a 
              href="#predict" 
              onClick={() => setActiveTab('predict')}
              className={`nav-link-custom ${activeTab === 'predict' ? 'active' : ''}`}
            >
              <FileText size={20} />
              <span>Single Predict</span>
            </a>
            <a 
              href="#batch" 
              onClick={() => setActiveTab('batch')}
              className={`nav-link-custom ${activeTab === 'batch' ? 'active' : ''}`}
            >
              <Upload size={20} />
              <span>Batch Predict</span>
            </a>
            <a 
              href="#students" 
              onClick={() => setActiveTab('students')}
              className={`nav-link-custom ${activeTab === 'students' ? 'active' : ''}`}
            >
              <Database size={20} />
              <span>Directory</span>
            </a>
          </nav>
        </div>

        {/* Footer info in sidebar */}
        <div className="px-2 pt-3 border-top border-secondary border-opacity-25">
          <div className="d-flex justify-content-between align-items-center mb-1">
            <span className="small text-secondary fw-semibold">Backend Port</span>
            <span className="badge bg-success bg-opacity-15 text-success small font-monospace">5000</span>
          </div>
          <div className="d-flex justify-content-between align-items-center">
            <span className="small text-secondary fw-semibold">App Status</span>
            <span className="badge bg-primary bg-opacity-15 text-primary small">Active</span>
          </div>
          <div className="text-center mt-3 text-secondary" style={{ fontSize: '0.75rem' }}>
            © 2026 Academic Predictor
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="col-12 col-md-9 col-xl-10 p-4 p-md-5 overflow-auto" style={{ maxHeight: '100vh' }}>
        
        {/* Render Active View */}
        {activeTab === 'dashboard' && (
          <DashboardStats stats={stats} apiHost={API_HOST} />
        )}
        
        {activeTab === 'predict' && (
          <PredictionForm apiHost={API_HOST} onPredictionSuccess={triggerRefresh} />
        )}
        
        {activeTab === 'batch' && (
          <BatchUpload apiHost={API_HOST} onUploadSuccess={triggerRefresh} />
        )}
        
        {activeTab === 'students' && (
          <StudentTable apiHost={API_HOST} refreshTrigger={refreshTrigger} />
        )}

      </main>
    </div>
  );
}

export default App;
