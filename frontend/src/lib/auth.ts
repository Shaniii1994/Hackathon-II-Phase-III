import apiClient, { AuthResponse, LoginRequest, RegisterRequest } from './api-client';

// Decode JWT token to extract user_id
export function decodeToken(token: string | null): { sub: string; exp: number; user_id?: number } | null {
  if (!token) {
    console.error('Cannot decode null or undefined token');
    return null;
  }

  try {
    // Remove "Bearer " prefix if present
    const cleanToken = token.startsWith('Bearer ') ? token.substring(7) : token;
    
    // Check if token has the correct JWT format (header.payload.signature)
    const tokenParts = cleanToken.split('.');
    if (tokenParts.length !== 3) {
      console.error(`Invalid token format: token must have 3 parts separated by dots, got ${tokenParts.length} parts`);
      console.log('Token received:', cleanToken);
      return null;
    }

    const base64Url = tokenParts[1]; // Payload is the second part
    if (!base64Url) {
      console.error('Token payload is empty');
      return null;
    }

    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    console.log('Token that caused error:', token);
    return null;
  }
}

// Login function
export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  try {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', credentials);
    const { access_token, refresh_token, user_id } = response.data;

    // Validate that we received proper tokens
    if (!access_token || !refresh_token || !user_id) {
      console.error('Incomplete authentication response:', response.data);
      throw new Error('Incomplete authentication response from server');
    }

    // Store tokens in localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user_id', user_id.toString());

    console.log('Login successful, tokens stored in localStorage');
    return response.data;
  } catch (error: any) {
    console.error('Login error:', error);
    if (error.response) {
      console.error('Server responded with error:', error.response.data);
    } else if (error.request) {
      console.error('Network error:', error.request);
    } else {
      console.error('General error:', error.message);
    }
    throw error;
  }
}

// Register function
export async function register(credentials: RegisterRequest): Promise<AuthResponse> {
  try {
    const response = await apiClient.post<AuthResponse>('/api/auth/register', credentials);
    const { access_token, refresh_token, user_id } = response.data;

    // Validate that we received proper tokens
    if (!access_token || !refresh_token || !user_id) {
      console.error('Incomplete registration response:', response.data);
      throw new Error('Incomplete registration response from server');
    }

    // Store tokens in localStorage after successful registration
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user_id', user_id.toString());

    console.log('Registration successful, tokens stored in localStorage');
    return response.data;
  } catch (error: any) {
    console.error('Registration error:', error);
    if (error.response) {
      console.error('Server responded with error:', error.response.data);
    } else if (error.request) {
      console.error('Network error:', error.request);
    } else {
      console.error('General error:', error.message);
    }
    throw error;
  }
}

// Logout function
export function logout(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_id');
  window.location.href = '/login';
}

// Get current user ID
export function getUserId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('user_id');
}

// Check if user is authenticated
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.log('No access token found in localStorage');
    return false;
  }

  // Check if token is expired
  const decoded = decodeToken(token);
  if (!decoded) {
    console.log('Could not decode token');
    return false;
  }

  const currentTime = Date.now() / 1000;
  const isValid = decoded.exp > currentTime;
  
  if (!isValid) {
    console.log('Token is expired');
  }
  
  return isValid;
}

// Get token
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}
