export default function Sidebar({ activeView, onNavigate, mobileOpen }) {
  const navItems = [
    { id: 'map', icon: '🗺️', label: 'Route Planner' },
    { id: 'history', icon: '📋', label: 'Trip History' },
    { id: 'stations', icon: '⚡', label: 'Charging Stations' },
  ];

  return (
    <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-logo">
          <div className="sidebar-brand-icon">⚡</div>
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
          <span className="status-dot"></span>
          <span>Backend Connected</span>
        </div>
      </div>
    </aside>
  );
}
