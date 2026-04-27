import { useState, useEffect } from 'react';
import { getTripHistory, clearTripHistory } from '../services/api';

export default function TripHistory({ onError }) {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        setLoading(true);
        const data = await getTripHistory();
        setTrips(data);
      } catch (err) {
        onError('Failed to load trip history. Is the backend running?');
      } finally {
        setLoading(false);
      }
    };
    fetchTrips();
  }, [onError]);

  const handleClearHistory = async () => {
    const shouldClear = window.confirm('Clear all trip history entries? This action cannot be undone.');
    if (!shouldClear) return;

    try {
      setClearing(true);
      await clearTripHistory();
      setTrips([]);
    } catch (err) {
      onError('Failed to clear trip history. Please try again.');
    } finally {
      setClearing(false);
    }
  };

  if (loading) {
    return (
      <div className="page-view">
        <div className="page-header">
          <h1 className="page-title">Trip History</h1>
          <p className="page-subtitle">Loading your past routes…</p>
        </div>
        <div className="card-grid">
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass-card data-card">
              <div className="skeleton" style={{ height: 20, width: '60%', marginBottom: 12 }}></div>
              <div className="skeleton" style={{ height: 14, width: '80%', marginBottom: 8 }}></div>
              <div className="skeleton" style={{ height: 14, width: '40%' }}></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="page-view">
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Trip History</h1>
            <p className="page-subtitle">
              {trips.length > 0
                ? `${trips.length} trip${trips.length > 1 ? 's' : ''} recorded`
                : 'No trips yet'}
            </p>
          </div>
          {trips.length > 0 && (
            <button
              type="button"
              className="btn btn-ghost"
              onClick={handleClearHistory}
              disabled={clearing}
            >
              {clearing ? 'Clearing...' : 'Clear History'}
            </button>
          )}
        </div>
      </div>

      {trips.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">TR</div>
          <h3 className="empty-state-title">No trips recorded yet</h3>
          <p className="empty-state-text">
            Plan a route using the Route Planner to see your trip history here.
          </p>
        </div>
      ) : (
        <div className="card-grid stagger">
          {trips.map((trip) => (
            <div key={trip.id} className="glass-card data-card">
              <div className="data-card-header">
                <div>
                  <div className="data-card-title">
                    {formatCoords(trip.source)} → {formatCoords(trip.destination)}
                  </div>
                  <div className="data-card-meta">
                    {formatDate(trip.created_at)}
                  </div>
                </div>
                <span className="badge badge-accent">
                  {trip.charging_stops?.length || 0} stop{(trip.charging_stops?.length || 0) !== 1 ? 's' : ''}
                </span>
              </div>

              <div className="data-card-stats">
                <div className="data-card-stat">
                  <span className="data-card-stat-value">{trip.distance_km} km</span>
                  <span className="data-card-stat-label">Distance</span>
                </div>
                <div className="data-card-stat">
                  <span className="data-card-stat-value">{trip.battery_used_percentage}%</span>
                  <span className="data-card-stat-label">Battery Start</span>
                </div>
                <div className="data-card-stat">
                  <span className="data-card-stat-value">{trip.charging_stops?.length || 0}</span>
                  <span className="data-card-stat-label">Charging Stops</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function formatCoords(coordStr) {
  if (!coordStr) return 'Unknown';
  const parts = coordStr.split(',').map((s) => s.trim());
  if (parts.length >= 2) {
    return `${parseFloat(parts[0]).toFixed(2)}°, ${parseFloat(parts[1]).toFixed(2)}°`;
  }
  return coordStr;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
