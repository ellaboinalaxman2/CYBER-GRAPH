import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:4000/api";
const ENABLE_MOCK_FALLBACK =
  import.meta.env.VITE_ENABLE_MOCK_FALLBACK === "true";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("cyber_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Authentication temporarily disabled. Do not redirect or clear session state.
    return Promise.reject(error);
  },
);

export { ENABLE_MOCK_FALLBACK };
export default apiClient;
