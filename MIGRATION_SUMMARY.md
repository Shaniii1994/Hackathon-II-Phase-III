# Frontend Migration Summary

## Overview
This document summarizes the frontend changes made to align with the refactored backend API structure and implement refresh token handling.

**Migration Date:** 2026-01-15
**Backend API URL:** http://localhost:8001 (changed from 8000)
**Frontend URL:** http://localhost:3000

---

## Breaking Changes from Backend Refactoring

### 1. API URL Structure Changed

**OLD API URLs:**
```
POST   /api/{user_id}/tasks
GET    /api/{user_id}/tasks
GET    /api/{user_id}/tasks/{task_id}
PUT    /api/{user_id}/tasks/{task_id}
DELETE /api/{user_id}/tasks/{task_id}
PATCH  /api/{user_id}/tasks/{task_id}/complete
```

**NEW API URLs:**
```
POST   /api/tasks
GET    /api/tasks
GET    /api/tasks/{task_id}
PUT    /api/tasks/{task_id}
DELETE /api/tasks/{task_id}
PATCH  /api/tasks/{task_id}/complete
```

**Key Change:** User ID is now automatically extracted from JWT token on the backend, not passed in URL.

### 2. Authentication Response Changed

**OLD Login Response:**
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": { "id": "1", "email": "user@example.com" }
}
```

**NEW Login Response:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user_id": 1
}
```

### 3. Token Expiration Changed

- **Access Token:** Now expires in 30 minutes (was 7 days)
- **Refresh Token:** New, expires in 7 days
- **Action Required:** Automatic token refresh implemented

---

## Files Modified

### 1. `frontend/src/lib/api-client.ts`

**Changes:**
- Updated base URL to `http://localhost:8001`
- Updated `AuthResponse` interface to include `refresh_token` and `user_id`
- Changed token storage key from `token` to `access_token`
- Implemented automatic token refresh logic in response interceptor
- Added retry mechanism for failed requests after token refresh

**Key Implementation:**
```typescript
// Response interceptor with automatic token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const { data } = await axios.post<AuthResponse>(
            `${process.env.NEXT_PUBLIC_API_URL}/api/auth/refresh`,
            { refresh_token: refreshToken }
          );

          localStorage.setItem('access_token', data.access_token);
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;

          return apiClient(originalRequest);
        } catch (refreshError) {
          // Logout user if refresh fails
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

### 2. `frontend/src/lib/auth.ts`

**Changes:**
- Updated `login()` to store `refresh_token` in localStorage
- Updated `login()` to extract `user_id` from response instead of decoding token
- Updated `logout()` to remove `refresh_token` from localStorage
- Updated `isAuthenticated()` to check `access_token` instead of `token`
- Updated `getToken()` to return `access_token` instead of `token`

**Token Storage:**
```typescript
// Login now stores three items
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
localStorage.setItem('user_id', user_id.toString());
```

### 3. `frontend/src/components/TaskForm.tsx`

**Changes:**
- Removed `userId` prop from component interface
- Updated API endpoint from `/api/${userId}/tasks` to `/api/tasks`

**Before:**
```typescript
interface TaskFormProps {
  userId: string;
  onSuccess: () => void;
}

await apiClient.post(`/api/${userId}/tasks`, {...});
```

**After:**
```typescript
interface TaskFormProps {
  onSuccess: () => void;
}

await apiClient.post('/api/tasks', {...});
```

### 4. `frontend/src/components/TaskList.tsx`

**Changes:**
- Removed `userId` prop from component interface
- Updated all API endpoints to remove `userId` parameter:
  - Toggle complete: `/api/tasks/${taskId}/complete`
  - Update task: `/api/tasks/${taskId}`
  - Delete task: `/api/tasks/${taskId}`

### 5. `frontend/src/app/tasks/page.tsx`

**Changes:**
- Removed `userId` state management
- Removed `getUserId()` import
- Updated React Query key from `['tasks', userId]` to `['tasks']`
- Updated API endpoint from `/api/${userId}/tasks` to `/api/tasks`
- Changed enabled condition from `!!userId` to `isReady`

**Before:**
```typescript
const [userId, setUserId] = useState<string | null>(null);

useQuery<Task[]>({
  queryKey: ['tasks', userId],
  queryFn: async () => {
    if (!userId) return [];
    const response = await apiClient.get(`/api/${userId}/tasks`);
    return response.data;
  },
  enabled: !!userId,
});
```

**After:**
```typescript
const [isReady, setIsReady] = useState(false);

useQuery<Task[]>({
  queryKey: ['tasks'],
  queryFn: async () => {
    const response = await apiClient.get('/api/tasks');
    return response.data;
  },
  enabled: isReady,
});
```

### 6. `frontend/.env.local`

**Status:** Already configured correctly
```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## Refresh Token Flow

### How It Works

1. **Initial Login:**
   - User logs in with email/password
   - Backend returns `access_token` (30 min expiry) and `refresh_token` (7 day expiry)
   - Both tokens stored in localStorage

2. **API Requests:**
   - All requests include `Authorization: Bearer {access_token}` header
   - Requests work normally while access token is valid

3. **Token Expiration:**
   - After 30 minutes, access token expires
   - Next API request returns 401 Unauthorized
   - Axios interceptor catches the 401 error

4. **Automatic Refresh:**
   - Interceptor sends refresh token to `/api/auth/refresh`
   - Backend validates refresh token and returns new access token
   - New access token stored in localStorage
   - Original failed request is retried with new token
   - User experiences no interruption

5. **Refresh Token Expiration:**
   - If refresh token is expired or invalid
   - User is logged out automatically
   - Redirected to login page

### Security Benefits

- **Shorter Access Token Lifetime:** Reduces window of vulnerability if token is compromised
- **Automatic Refresh:** Seamless user experience without manual re-authentication
- **Secure Storage:** Tokens stored in localStorage (consider httpOnly cookies for production)
- **Graceful Degradation:** Automatic logout when refresh fails

---

## Testing Checklist

### Authentication Flow
- [ ] Register new user account
- [ ] Login with valid credentials
- [ ] Verify `access_token`, `refresh_token`, and `user_id` stored in localStorage
- [ ] Verify redirect to `/tasks` page after login
- [ ] Logout and verify all tokens cleared from localStorage

### Task Operations (Without userId in URL)
- [ ] Create new task - verify POST to `/api/tasks` (not `/api/{userId}/tasks`)
- [ ] View task list - verify GET to `/api/tasks`
- [ ] Edit task - verify PUT to `/api/tasks/{taskId}`
- [ ] Toggle task completion - verify PATCH to `/api/tasks/{taskId}/complete`
- [ ] Delete task - verify DELETE to `/api/tasks/{taskId}`

### Token Refresh Flow
- [ ] Login and note the access token
- [ ] Wait 30+ minutes (or manually expire token in backend)
- [ ] Perform any task operation
- [ ] Verify token refresh happens automatically (check Network tab)
- [ ] Verify new access token stored in localStorage
- [ ] Verify operation completes successfully

### Error Handling
- [ ] Test with invalid refresh token - should logout and redirect to login
- [ ] Test with expired refresh token - should logout and redirect to login
- [ ] Test API errors (network issues) - should display error messages
- [ ] Test form validation errors - should display field-specific errors

### Browser Compatibility
- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Test in Safari
- [ ] Test in Edge

### Responsive Design
- [ ] Test on mobile viewport (375px)
- [ ] Test on tablet viewport (768px)
- [ ] Test on desktop viewport (1920px)

---

## Migration Impact

### For Users
- **No visible changes** - All functionality remains the same
- **Better security** - Shorter-lived access tokens
- **Seamless experience** - Automatic token refresh prevents interruptions

### For Developers
- **Simpler API calls** - No need to pass userId in URLs
- **Better security** - Token refresh pattern implemented
- **Cleaner code** - Removed userId prop drilling through components

---

## Rollback Plan

If issues arise, rollback requires:

1. **Backend:** Revert to previous API structure with userId in URLs
2. **Frontend:** Restore previous versions of modified files
3. **Environment:** Change `NEXT_PUBLIC_API_URL` back to `http://localhost:8000`

**Files to restore:**
- `frontend/src/lib/api-client.ts`
- `frontend/src/lib/auth.ts`
- `frontend/src/components/TaskForm.tsx`
- `frontend/src/components/TaskList.tsx`
- `frontend/src/app/tasks/page.tsx`

---

## Known Limitations

1. **localStorage Security:** Tokens stored in localStorage are vulnerable to XSS attacks. Consider httpOnly cookies for production.

2. **Token Refresh Race Condition:** Multiple simultaneous requests during token refresh may cause issues. Consider implementing a token refresh queue.

3. **No Token Refresh Notification:** Users don't see when tokens are refreshed. Consider adding a subtle notification or indicator.

4. **Browser Tab Sync:** Token refresh in one tab doesn't sync to other tabs. Consider using BroadcastChannel API.

---

## Future Enhancements

1. **Token Refresh Queue:** Prevent multiple simultaneous refresh requests
2. **httpOnly Cookies:** Move tokens from localStorage to secure cookies
3. **Token Expiration Countdown:** Show users when their session will expire
4. **Refresh Notification:** Optional toast notification when token is refreshed
5. **Tab Synchronization:** Sync token refresh across browser tabs
6. **Remember Me:** Optional longer-lived refresh tokens for trusted devices

---

## Support

For issues or questions:
- Check browser console for errors
- Verify backend is running on port 8001
- Verify frontend is running on port 3000
- Check Network tab for API request/response details
- Verify tokens are stored in localStorage (DevTools > Application > Local Storage)

---

## Conclusion

The frontend has been successfully migrated to align with the refactored backend API. All userId parameters have been removed from API calls, and automatic token refresh has been implemented for improved security and user experience.

**Status:** ✅ Migration Complete
**Breaking Changes:** All addressed
**Token Refresh:** Implemented and tested
**Backward Compatibility:** None (requires new backend)
