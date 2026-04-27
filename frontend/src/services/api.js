import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

export const optimizeRoute = async (data) => {
  const response = await API.post('/optimize-route/', data);
  return response.data;
};

export const getVehicles = async () => {
  const response = await API.get('/vehicles/');
  return response.data;
};

export const getStations = async () => {
  const response = await API.get('/stations/');
  return response.data;
};

export const getTripHistory = async () => {
  const response = await API.get('/trips/');
  return response.data;
};

export const clearTripHistory = async () => {
  const response = await API.delete('/trips/clear/');
  return response.data;
};

export const checkBackendHealth = async () => {
  const response = await API.get('/health/');
  return response.data;
};
