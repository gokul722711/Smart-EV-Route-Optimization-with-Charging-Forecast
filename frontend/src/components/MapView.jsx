import { useState, useEffect, useCallback } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Popup,
  useMapEvents,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { optimizeRoute, getVehicles } from '../services/api';

// Fix Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom icons
const sourceIcon = new L.DivIcon({
  className: '',
  html: `<div style="
    width:28px;height:28px;border-radius:50%;
    background:linear-gradient(135deg,#3b82f6,#2563eb);
    border:3px solid #fff;box-shadow:0 0 12px rgba(59,130,246,0.6);
    display:flex;align-items:center;justify-content:center;
    font-size:12px;color:white;font-weight:700;
  ">A</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
});

const destIcon = new L.DivIcon({
  className: '',
  html: `<div style="
    width:28px;height:28px;border-radius:50%;
    background:linear-gradient(135deg,#ef4444,#dc2626);
    border:3px solid #fff;box-shadow:0 0 12px rgba(239,68,68,0.6);
    display:flex;align-items:center;justify-content:center;
    font-size:12px;color:white;font-weight:700;
  ">B</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
});

const chargingIcon = new L.DivIcon({
  className: '',
  html: `<div style="
    width:30px;height:30px;border-radius:50%;
    background:linear-gradient(135deg,#10b981,#059669);
    border:3px solid #fff;box-shadow:0 0 14px rgba(16,185,129,0.5);
    display:flex;align-items:center;justify-content:center;
    font-size:14px;
  ">⚡</div>`,
  iconSize: [30, 30],
  iconAnchor: [15, 15],
});

// Click selector
function LocationSelector({ setSource, setDestination, source, destination }) {
  useMapEvents({
    click(e) {
      if (!source) {
        setSource([e.latlng.lat, e.latlng.lng]);
      } else if (!destination) {
        setDestination([e.latlng.lat, e.latlng.lng]);
      } else {
        setSource([e.latlng.lat, e.latlng.lng]);
        setDestination(null);
      }
    },
  });
  return null;
}

// Auto-fit bounds when route changes
function FitBounds({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions && positions.length > 1) {
      const bounds = L.latLngBounds(positions);
      map.fitBounds(bounds, { padding: [60, 60] });
    }
  }, [positions, map]);
  return null;
}

export default function MapView({ onError }) {
  const [source, setSource] = useState(null);
  const [destination, setDestination] = useState(null);
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [vehicles, setVehicles] = useState([]);
  const [selectedVehicle, setSelectedVehicle] = useState('');
  const [battery, setBattery] = useState(80);

  // Fetch vehicles
  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const data = await getVehicles();
        setVehicles(data);
        if (data.length > 0) {
          setSelectedVehicle(String(data[0].id));
        }
      } catch (err) {
        onError('Failed to load vehicles. Is the backend running?');
      }
    };
    fetchVehicles();
  }, [onError]);

  // Fetch route when both points are set
  const fetchRoute = useCallback(async () => {
    if (!source || !destination) return;
    if (!selectedVehicle) {
      onError('Please select a vehicle first.');
      return;
    }

    try {
      setLoading(true);
      setRouteData(null);

      const response = await optimizeRoute({
        source_lat: source[0],
        source_lon: source[1],
        destination_lat: destination[0],
        destination_lon: destination[1],
        vehicle_id: parseInt(selectedVehicle),
        battery_percentage: battery,
      });

      if (response.error) {
        onError(response.error);
      } else {
        setRouteData(response);
      }
    } catch (error) {
      const msg = error.response?.data?.error || error.message || 'Route optimization failed';
      onError(msg);
    } finally {
      setLoading(false);
    }
  }, [source, destination, selectedVehicle, battery, onError]);

  useEffect(() => {
    if (source && destination) {
      fetchRoute();
    }
  }, [source, destination, fetchRoute]);

  // Build polyline
  let routeCoordinates = [];
  if (routeData?.route_segments) {
    routeData.route_segments.forEach((segment) => {
      if (segment.geometry?.coordinates) {
        const coords = segment.geometry.coordinates.map(([lon, lat]) => [lat, lon]);
        routeCoordinates = [...routeCoordinates, ...coords];
      }
    });
  }

  // Total distance
  const totalDistance = routeData?.route_segments?.reduce(
    (sum, seg) => sum + (seg.distance_km || 0), 0
  ) || 0;

  const resetRoute = () => {
    setSource(null);
    setDestination(null);
    setRouteData(null);
  };

  // Battery color
  const batteryColor =
    battery > 60 ? '#10b981' :
    battery > 30 ? '#f59e0b' : '#ef4444';

  // Instructions text
  const getInstructionText = () => {
    if (!source) return 'Click on the map to set your starting point';
    if (!destination) return 'Click on the map to set your destination';
    return 'Click anywhere to set a new route';
  };

  return (
    <div className="map-page">
      {/* Map */}
      <MapContainer
        center={[12.9716, 77.5946]}
        zoom={6}
        className="map-container"
        zoomControl={true}
      >
        <TileLayer
          attribution="&copy; CartoDB"
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        <LocationSelector
          setSource={setSource}
          setDestination={setDestination}
          source={source}
          destination={destination}
        />

        {routeCoordinates.length > 1 && <FitBounds positions={routeCoordinates} />}

        {source && (
          <Marker position={source} icon={sourceIcon}>
            <Popup>
              <strong>📍 Start Point</strong><br />
              {source[0].toFixed(4)}°, {source[1].toFixed(4)}°
            </Popup>
          </Marker>
        )}

        {destination && (
          <Marker position={destination} icon={destIcon}>
            <Popup>
              <strong>🏁 Destination</strong><br />
              {destination[0].toFixed(4)}°, {destination[1].toFixed(4)}°
            </Popup>
          </Marker>
        )}

        {routeCoordinates.length > 0 && (
          <>
            <Polyline
              positions={routeCoordinates}
              pathOptions={{
                color: '#3b82f6',
                weight: 5,
                opacity: 0.8,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
            <Polyline
              positions={routeCoordinates}
              pathOptions={{
                color: '#93c5fd',
                weight: 2,
                opacity: 0.4,
                dashArray: '8, 12',
              }}
            />
          </>
        )}

        {routeData?.charging_stops?.map((stop, index) => {
          const stationSegment = routeData.route_segments.find(
            (seg) => seg.from === stop.node
          );
          if (!stationSegment?.geometry?.coordinates?.length) return null;
          const [lon, lat] = stationSegment.geometry.coordinates[0];

          return (
            <Marker key={index} position={[lat, lon]} icon={chargingIcon}>
              <Popup>
                <strong>⚡ Charging Stop #{index + 1}</strong><br />
                Station: {stop.node}<br />
                Battery after: {stop.battery_after_charge} km range
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="glass-card loading-pill">
            <div className="loading-spinner"></div>
            Optimizing route…
          </div>
        </div>
      )}

      {/* Left Control Panel */}
      <div className="control-panel">
        {/* Vehicle & Battery Config */}
        <div className="glass-card control-card">
          <div className="control-card-title">
            <span className="icon">🚗</span> Vehicle Setup
          </div>

          <div className="control-group">
            <label className="control-label">Vehicle</label>
            <select
              className="select"
              value={selectedVehicle}
              onChange={(e) => setSelectedVehicle(e.target.value)}
            >
              {vehicles.length === 0 && <option value="">No vehicles available</option>}
              {vehicles.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} — {v.max_range_km} km range
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label className="control-label">
              Battery Level
              <span className="value" style={{ color: batteryColor }}>{battery}%</span>
            </label>
            <input
              type="range"
              min="5"
              max="100"
              step="5"
              value={battery}
              onChange={(e) => setBattery(parseInt(e.target.value))}
              style={{
                background: `linear-gradient(to right, ${batteryColor} ${battery}%, var(--bg-input) ${battery}%)`,
              }}
            />
            <div className="battery-bar-container">
              <div
                className="battery-bar-fill"
                style={{
                  width: `${battery}%`,
                  background: `linear-gradient(90deg, ${batteryColor}, ${batteryColor}88)`,
                }}
              ></div>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="click-instructions">
          <div className="pulse-dot"></div>
          <span>{getInstructionText()}</span>
        </div>

        {/* Re-route button (shown when route exists) */}
        {routeData && (
          <button className="btn btn-primary" style={{ width: '100%' }} onClick={fetchRoute}>
            🔄 Recalculate Route
          </button>
        )}
      </div>

      {/* Right Route Summary */}
      {routeData && (
        <div className="route-summary-panel">
          <div className="glass-card route-summary-content">
            <div className="route-summary-header">
              <h3 className="route-summary-title">🗺️ Route Summary</h3>
              <button className="btn btn-ghost" onClick={resetRoute} style={{ padding: '6px 12px', fontSize: 'var(--font-xs)' }}>
                ✕ Clear
              </button>
            </div>

            <div className="route-stats-grid">
              <div className="route-stat-card">
                <div className="route-stat-value">{routeData.total_time_min} min</div>
                <div className="route-stat-label">Total Time</div>
              </div>
              <div className="route-stat-card">
                <div className="route-stat-value">{totalDistance.toFixed(1)} km</div>
                <div className="route-stat-label">Total Distance</div>
              </div>
              <div className="route-stat-card">
                <div className="route-stat-value">{routeData.initial_battery_km} km</div>
                <div className="route-stat-label">Initial Range</div>
              </div>
              <div className="route-stat-card">
                <div className="route-stat-value">{routeData.charging_stops?.length || 0}</div>
                <div className="route-stat-label">Charging Stops</div>
              </div>
            </div>

            {/* Segments & Stops Timeline */}
            {(routeData.route_segments?.length > 0 || routeData.charging_stops?.length > 0) && (
              <div>
                <div className="segments-title">Route Timeline</div>
                {routeData.route_segments?.map((seg, i) => {
                  // Check if there's a charging stop at this segment's origin
                  const chargeHere = routeData.charging_stops?.find(s => s.node === seg.from);

                  return (
                    <div key={`seg-${i}`}>
                      {chargeHere && (
                        <div className="segment-item">
                          <div className="segment-dot charge"></div>
                          <div className="segment-info">
                            <strong>⚡ Charge at {chargeHere.node}</strong>
                            <div className="segment-meta">
                              Battery → {chargeHere.battery_after_charge} km
                            </div>
                          </div>
                        </div>
                      )}
                      <div className="segment-item">
                        <div className="segment-dot travel"></div>
                        <div className="segment-info">
                          <strong>{seg.from} → {seg.to}</strong>
                          <div className="segment-meta">
                            {seg.distance_km} km · {seg.duration_min} min
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
