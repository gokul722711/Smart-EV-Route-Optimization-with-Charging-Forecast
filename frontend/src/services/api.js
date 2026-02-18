import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

export const optimizeRoute = async (data) => {
  const response = await API.post('/optimize-route/', data);
  return response.data;
};
