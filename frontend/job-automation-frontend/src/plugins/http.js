import axios from "axios";

export const httpInstance = axios.create({
  baseURL: "http://127.0.0.1:5000", // Update as per your API base URL
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach token to every request if it exists
httpInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
