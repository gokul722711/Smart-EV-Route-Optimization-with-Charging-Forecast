import { useState, useEffect } from 'react';
import { getStations } from '../services/api';

export default function StationList({ onError }) {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStations = async () => {
      try {
        setLoading(true);
        const data = await getStations();
        setStations(data);
      } catch (err) {
        onError('Failed to load charging stations. Is the backend running?');
      } finally {
        setLoading(false);
      }
    };
    fetchStations();
  }, [onError]);

  if (loading) {
    return (
      <div className="page-view">
        <div className="page-header">
          <h1 className="page-title">Charging Stations</h1>
          <p className="page-subtitle">Loading station data…</p>
        </div>
        <div className="card-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="glass-card data-card">
              <div className="skeleton" style={{ height: 20, width: '50%', marginBottom: 12 }}></div>
              <div className="skeleton" style={{ height: 14, width: '70%', marginBottom: 8 }}></div>
              <div className="skeleton" style={{ height: 14, width: '35%' }}></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="page-view">
      <div className="page-header">
        <h1 className="page-title">Charging Stations</h1>
        <p className="page-subtitle">
          {stations.length > 0
            ? `${stations.length} station${stations.length > 1 ? 's' : ''} available in the network`
            : 'No stations registered'}
        </p>
      </div>

      {stations.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🔌</div>
          <h3 className="empty-state-title">No charging stations</h3>
          <p className="empty-state-text">
            Charging stations can be added through the Django admin panel.
          </p>
        </div>
      ) : (
        <div className="card-grid stagger">
          {stations.map((station) => (
            <div key={station.id} className="glass-card data-card">
              <div className="data-card-header">
                <div>
                  <div className="data-card-title">
                    {station.fast_charger ? '⚡' : '🔌'} {station.name}
                  </div>
                  <div className="data-card-meta">
                    {station.latitude.toFixed(4)}°N, {station.longitude.toFixed(4)}°E
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {station.fast_charger && (
                    <span className="badge badge-warning">Fast Charger</span>
                  )}
                  <span className="badge badge-success">{station.power_kw} kW</span>
                </div>
              </div>

              <div className="data-card-stats">
                <div className="data-card-stat">
                  <span className="data-card-stat-value">{station.power_kw} kW</span>
                  <span className="data-card-stat-label">Power Output</span>
                </div>
                <div className="data-card-stat">
                  <span className="data-card-stat-value">{station.total_slots}</span>
                  <span className="data-card-stat-label">Total Slots</span>
                </div>
                <div className="data-card-stat">
                  <span className="data-card-stat-value">{station.fast_charger ? 'Yes' : 'No'}</span>
                  <span className="data-card-stat-label">Fast Charging</span>
                </div>
              </div>

              <div className="station-slots" title={`${station.total_slots} charging slots`}>
                {Array.from({ length: Math.min(station.total_slots, 12) }).map((_, i) => (
                  <div key={i} className="slot-dot"></div>
                ))}
                {station.total_slots > 12 && (
                  <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)', marginLeft: 4 }}>
                    +{station.total_slots - 12}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
