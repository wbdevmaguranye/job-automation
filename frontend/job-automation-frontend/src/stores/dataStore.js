// stores/dataStore.js
import { defineStore } from 'pinia';
import { httpInstance } from '@/plugins/http';

export const useDataStore = defineStore('dataStore', {
  actions: {
    // Generic GET request
    async getData(url, options = {}) {
      try {
        const response = await httpInstance.get(url, addAuthHeader(options));
        return handleResponse(response);
      } catch (error) {
        return handleErrorResponse(error);
      }
    },

    // Generic POST request
    async postData(url, payload = {}, options = {}) {
      try {
        const response = await httpInstance.post(url, payload, addAuthHeader(options));
        return handleResponse(response);
      } catch (error) {
        return handleErrorResponse(error);
      }
    },

    // Generic DELETE request
    async deleteData(url, options = {}) {
      try {
        const response = await httpInstance.delete(url, addAuthHeader(options));
        return handleResponse(response);
      } catch (error) {
        return handleErrorResponse(error);
      }
    },

    // Generic PUT request
    async putData(url, payload = {}, options = {}) {
      try {
        const response = await httpInstance.put(url, payload, addAuthHeader(options));
        return handleResponse(response);
      } catch (error) {
        return handleErrorResponse(error);
      }
    },
  },
});

// Utility: Add Authorization Header
function addAuthHeader(headers) {
  const token = localStorage.getItem('token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log("Authorization Header Set: ", headers); // Debugging log
  } else {
    console.warn("No token found for Authorization header.");
  }
  return headers;
}

// Utility: Handle API Response
function handleResponse(response) {
  return {
    data: response.data?.data ?? response.data ?? {},
    status: response.status,
    success: true,
  };
}

// Utility: Handle API Errors
function handleErrorResponse(error) {
  console.error('API Error:', error);
  return {
    data:
      error?.response?.data?.data ??
      error?.response?.data ??
      { message: 'An error occurred while processing your request' },
    status: error?.response?.status ?? 500,
    success: false,
  };
}
