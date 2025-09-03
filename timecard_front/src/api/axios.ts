import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const authStore = useAuthStore();

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = authStore.refreshToken;
        if (!refreshToken) {
          authStore.logout();
          return Promise.reject(error);
        }

        const { data } = await axios.post('/api/refresh', {}, {
          headers: {
            'Authorization': `Bearer ${refreshToken}`
          }
        });

        authStore.setNewAccessToken(data.access_token);
        originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`;

        return api(originalRequest);
      } catch (refreshError) {
        console.error("Unable to refresh token:", refreshError);
        authStore.logout();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
)

export default api;
