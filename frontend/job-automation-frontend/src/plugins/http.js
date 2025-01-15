// plugins/http.js
import axios from 'axios';

export const httpInstance = axios.create({
  baseURL: 'http://127.0.0.1:5000', 
  headers: {
    'Content-Type': 'application/json',
  },
});
