import { useState, useCallback, useEffect } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import MapView from './components/MapView';
import TripHistory from './components/TripHistory';
import StationList from './components/StationList';
import ErrorToast from './components/ErrorToast';

function App() {
  const [activeView, setActiveView] = useState('map');
  const [errors, setErrors] = useState([]);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light' || savedTheme === 'dark') {
      setTheme(savedTheme);
      return;
    }

    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(prefersDark ? 'dark' : 'light');
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const addError = useCallback((message) => {
    const id = Date.now() + Math.random();
    setErrors((prev) => [...prev, { id, message }]);
  }, []);

  const removeError = useCallback((id) => {
    setErrors((prev) => prev.filter((e) => e.id !== id));
  }, []);

  const handleNavigate = (view) => {
    setActiveView(view);
    setMobileMenuOpen(false);
  };

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  return (
    <div className="app-layout">
      {/* Mobile Header */}
      <div className="mobile-header">
        <button className="mobile-menu-btn" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
          ☰
        </button>
        <span style={{ fontWeight: 700, fontSize: 'var(--font-base)' }}>EV Route Planner</span>
      </div>

      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div className="mobile-overlay" onClick={() => setMobileMenuOpen(false)}></div>
      )}

      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        onNavigate={handleNavigate}
        mobileOpen={mobileMenuOpen}
        theme={theme}
        onThemeToggle={toggleTheme}
      />

      {/* Main Content */}
      <main className="main-content">
        {activeView === 'map' && <MapView onError={addError} theme={theme} />}
        {activeView === 'history' && <TripHistory onError={addError} />}
        {activeView === 'stations' && <StationList onError={addError} />}
      </main>

      {/* Error Toasts */}
      <ErrorToast errors={errors} removeError={removeError} />
    </div>
  );
}

export default App;
