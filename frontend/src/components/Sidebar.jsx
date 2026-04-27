export default function Sidebar({
  activeView,
  onNavigate,
  mobileOpen,
  theme,
  onThemeToggle,
  backendStatus = 'checking',
}) {
  const navItems = [
    { id: 'map', icon: 'RP', label: 'Route Planner' },
    { id: 'history', icon: 'TH', label: 'Trip History' },
    { id: 'stations', icon: 'CS', label: 'Charging Stations' },
  ];

  return (
    <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-logo">
          <div className="sidebar-brand-icon">EV</div>
          <div className="sidebar-brand-text">
            <span className="sidebar-brand-title">EV Route</span>
            <span className="sidebar-brand-subtitle">Smart Planner</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <span className="sidebar-nav-label">Navigation</span>
        {navItems.map((item) => (
          <div
            key={item.id}
            className={`sidebar-nav-item ${activeView === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-footer-status">
          <span className={`status-dot ${backendStatus}`}></span>
          <span>
            {backendStatus === 'connected'
              ? 'Backend Connected'
              : backendStatus === 'disconnected'
                ? 'Backend Offline'
                : 'Checking backend...'}
          </span>
        </div>
        <button
          type="button"
          className="theme-toggle"
          onClick={onThemeToggle}
          aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          <span className="theme-toggle-label">{theme === 'light' ? 'Light' : 'Dark'} mode</span>
          <span className={`theme-toggle-track ${theme === 'dark' ? 'is-dark' : ''}`}>
            <span className="theme-toggle-thumb"></span>
          </span>
        </button>
      </div>
    </aside>
  );
}
