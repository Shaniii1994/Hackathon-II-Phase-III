import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// API Response Types
export interface User {
  id: number;
  email: string;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  due_date: string | null;
  is_complete: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface CreateTaskRequest {
  title: string;
  description: string;
  due_date: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  due_date?: string;
  completed?: boolean;
}

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      // Ensure we're sending the correct format
      const cleanToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
      config.headers.Authorization = cleanToken;
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors and refresh tokens
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          // Attempt to refresh the access token
          const refreshResponse = await axios.post<AuthResponse>(
            `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/refresh`,
            { refresh_token: refreshToken }
          );

          // Store new access token
          localStorage.setItem('access_token', refreshResponse.data.access_token);

          // Update authorization header with new token
          const newToken = refreshResponse.data.access_token.startsWith('Bearer ') 
            ? refreshResponse.data.access_token 
            : `Bearer ${refreshResponse.data.access_token}`;
          originalRequest.headers!.Authorization = newToken;

          // Retry the original request with new token
          return apiClient(originalRequest);
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          
          // Refresh token failed or expired, logout user
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user_id');

          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }

          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available, logout user
        console.log('No refresh token available, logging out user');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');

        if (typeof window !== 'undefined') {
          window.location.href = '/login';
          window.location.reload(); // Force redirect
        }
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
