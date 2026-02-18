import { useState, useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Popup,
  useMapEvents,
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { optimizeRoute } from '../services/api';

// Fix Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Charging station icon
const chargingIcon = new L.Icon({
  iconUrl: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
  iconSize: [32, 32],
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

function MapView() {
  const [source, setSource] = useState(null);
  const [destination, setDestination] = useState(null);
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (source && destination) {
      const fetchRoute = async () => {
        try {
          setLoading(true);

          const response = await optimizeRoute({
            source_lat: source[0],
            source_lon: source[1],
            destination_lat: destination[0],
            destination_lon: destination[1],
            vehicle_id: 1,
            battery_percentage: 25,
          });

          setRouteData(response);
        } catch (error) {
          console.error('Route error:', error);
        } finally {
          setLoading(false);
        }
      };

      fetchRoute();
    }
  }, [source, destination]);

  // Build polyline
  let routeCoordinates = [];

  if (routeData?.route_segments) {
    routeData.route_segments.forEach((segment) => {
      if (segment.geometry?.coordinates) {
        const coords = segment.geometry.coordinates.map(
          ([lon, lat]) => [lat, lon]
        );
        routeCoordinates = [...routeCoordinates, ...coords];
      }
    });
  }

  const resetRoute = () => {
    setSource(null);
    setDestination(null);
    setRouteData(null);
  };

  return (
    <div style={{ height: '100vh', width: '100%', position: 'relative' }}>
      <MapContainer
        center={[12.9716, 77.5946]}
        zoom={6}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <LocationSelector
          setSource={setSource}
          setDestination={setDestination}
          source={source}
          destination={destination}
        />

        {source && (
          <Marker position={source}>
            <Popup>Source</Popup>
          </Marker>
        )}

        {destination && (
          <Marker position={destination}>
            <Popup>Destination</Popup>
          </Marker>
        )}

        {routeCoordinates.length > 0 && (
          <Polyline positions={routeCoordinates} color="blue" weight={4} />
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
                ⚡ Charging Stop <br />
                {stop.node} <br />
                Battery After: {stop.battery_after_charge} km
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Loading */}
      {loading && (
        <div
          style={{
            position: 'absolute',
            top: 20,
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'white',
            padding: '8px 16px',
            borderRadius: 8,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          }}
        >
          Optimizing route...
        </div>
      )}

      {/* Floating Dashboard */}
      {routeData && (
        <div
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            width: 300,
            background: 'white',
            padding: 20,
            borderRadius: 14,
            boxShadow: '0 8px 20px rgba(0,0,0,0.2)',
          }}
        >
          <h3 style={{ marginBottom: 12 }}>EV Route Summary</h3>

          <p><strong>Total Time:</strong> {routeData.total_time_min} min</p>
          <p><strong>Initial Battery:</strong> {routeData.initial_battery_km} km</p>
          <p><strong>Charging Stops:</strong> {routeData.charging_stops?.length || 0}</p>
          <p><strong>Segments:</strong> {routeData.route_segments?.length || 0}</p>

          <button
            onClick={resetRoute}
            style={{
              marginTop: 15,
              padding: '8px 12px',
              borderRadius: 8,
              border: 'none',
              background: '#2563eb',
              color: 'white',
              cursor: 'pointer',
              width: '100%',
            }}
          >
            Reset Route
          </button>
        </div>
      )}
    </div>
  );
}

export default MapView;
