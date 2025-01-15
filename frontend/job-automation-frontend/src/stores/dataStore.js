// stores/dataStore.js
import { defineStore } from 'pinia';
import { httpInstance } from '@/plugins/http';

export const useDataStore = defineStore('dataStore', {
  actions: {
    async getData(url) {
      try {
        const response = await httpInstance.get(url);
        return handleResponse(response);
      } catch (error) {
        return handleErrorResponse(error);
      }
    },
    async postData(url, payload = {}) {
      try {
        const response = await httpInstance.post(url, payload);
        return handleResponse(response);
      } catch (error) {
        return handleErrorResponse(error);
      }
    },
    async deleteData(url) {
      try {
        const response = await httpInstance.delete(url);
        return handleResponse(response);
      } catch (error) {
        return handleErrorResponse(error);
      }
    },
    async putData(url, payload = {}) {
      try {
        const response = await httpInstance.put(url, payload);
        return handleResponse(response);
      } catch (error) {
        return handleErrorResponse(error);
      }
    },
  },
});

function handleResponse(response) {
  return {
    data: response.data?.data ?? response.data ?? {},
    status: response.status,
    success: true,
  };
}

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
