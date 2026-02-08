# Authentication Implementation Guide

**Project:** Todo Full-Stack Web Application
**Security Standard:** OWASP Compliant
**Last Updated:** 2026-01-15

---

## Quick Start

### 1. Setup Environment Variables

Copy `.env.example` to `.env` and update values:

```bash
# Generate a secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with the generated secret
BETTER_AUTH_SECRET=<generated-secret>
```

### 2. Run Database Migration

```bash
# Connect to your Neon database
psql $DATABASE_URL -f backend/migrations/add_security_fields_to_user.sql
```

### 3. Verify Configuration

Ensure these settings are configured in `.env`:

```bash
# JWT Configuration (OWASP Compliant)
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ALGORITHM=HS256

# Password Security
BCRYPT_ROUNDS=12

# Rate Limiting
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_WINDOW_MINUTES=15
ACCOUNT_LOCKOUT_MINUTES=30
```

---

## API Endpoints

### Register New User

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error Response (422 Validation Error):**
```json
{
  "detail": "Password must contain at least one special character"
}
```

---

### Login User

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1
}
```

**Security Features:**
- Generic error messages (prevents email enumeration)
- Account lockout after 5 failed attempts
- 30-minute lockout duration
- Failed attempt tracking

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password"
}
```

**Error Response (Account Locked):**
```json
{
  "detail": "Account temporarily locked due to multiple failed login attempts. Please try again in 25 minutes."
}
```

---

### Refresh Access Token

**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**When to Use:**
- When access token expires (after 30 minutes)
- When you receive 401 error on protected routes
- To maintain user session without re-login

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid refresh token"
}
```

---

### Access Protected Routes

**Endpoint:** `GET /tasks` (example)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Task 1",
    "completed": false
  }
]
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid authentication credentials"
}
```

---

## Frontend Integration

### 1. Registration Flow

```javascript
async function register(email, password) {
  try {
    const response = await fetch('http://localhost:8000/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const user = await response.json();
    console.log('User registered:', user);
    return user;
  } catch (error) {
    console.error('Registration failed:', error.message);
    throw error;
  }
}
```

### 2. Login Flow

```javascript
async function login(email, password) {
  try {
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const data = await response.json();

    // SECURITY: Store tokens securely
    // For web apps: Use httpOnly cookies (recommended)
    // For SPAs: Use secure storage (not localStorage for refresh tokens)
    localStorage.setItem('access_token', data.access_token);
    sessionStorage.setItem('refresh_token', data.refresh_token);

    return data;
  } catch (error) {
    console.error('Login failed:', error.message);
    throw error;
  }
}
```

### 3. Token Refresh Flow

```javascript
async function refreshAccessToken() {
  try {
    const refreshToken = sessionStorage.getItem('refresh_token');

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch('http://localhost:8000/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // Refresh token invalid or expired - redirect to login
      throw new Error('Session expired');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);

    return data.access_token;
  } catch (error) {
    console.error('Token refresh failed:', error.message);
    // Redirect to login page
    window.location.href = '/login';
    throw error;
  }
}
```

### 4. API Request with Auto-Refresh

```javascript
async function apiRequest(url, options = {}) {
  const accessToken = localStorage.getItem('access_token');

  // Add authorization header
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${accessToken}`,
  };

  try {
    let response = await fetch(url, { ...options, headers });

    // If 401, try to refresh token and retry
    if (response.status === 401) {
      console.log('Access token expired, refreshing...');
      const newAccessToken = await refreshAccessToken();

      // Retry request with new token
      headers['Authorization'] = `Bearer ${newAccessToken}`;
      response = await fetch(url, { ...options, headers });
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error.message);
    throw error;
  }
}

// Usage
async function getTasks() {
  return await apiRequest('http://localhost:8000/tasks');
}
```

### 5. Logout Flow

```javascript
function logout() {
  // Clear tokens
  localStorage.removeItem('access_token');
  sessionStorage.removeItem('refresh_token');

  // Redirect to login
  window.location.href = '/login';
}
```

---

## Security Best Practices

### Token Storage

**Web Applications (Recommended):**
- Store refresh tokens in httpOnly cookies
- Store access tokens in memory or sessionStorage
- Never store tokens in localStorage for sensitive apps

**Single Page Applications:**
- Store access tokens in memory (React state, Vuex, etc.)
- Store refresh tokens in secure storage (not localStorage)
- Clear tokens on logout

**Mobile Applications:**
- Use secure storage (Keychain on iOS, Keystore on Android)
- Never store tokens in plain text

### Password Requirements

Enforce these requirements on the frontend for better UX:

```javascript
function validatePassword(password) {
  const errors = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one digit');
  }
  if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }

  return errors;
}
```

### Error Handling

Always handle authentication errors gracefully:

```javascript
try {
  await login(email, password);
} catch (error) {
  if (error.message.includes('locked')) {
    // Account locked - show lockout message
    showError('Your account has been temporarily locked. Please try again later.');
  } else if (error.message.includes('Invalid')) {
    // Invalid credentials - show generic error
    showError('Invalid email or password. Please try again.');
  } else {
    // Other errors
    showError('An error occurred. Please try again.');
  }
}
```

---

## Security Monitoring

### Events to Monitor

1. **Failed Login Attempts**
   - Track failed attempts per user
   - Alert on unusual patterns
   - Monitor for brute-force attacks

2. **Account Lockouts**
   - Log all account lockouts
   - Alert security team
   - Track lockout frequency

3. **Token Refresh Failures**
   - Monitor refresh token failures
   - Track expired tokens
   - Identify suspicious patterns

4. **Successful Logins**
   - Log successful authentications
   - Track login locations/IPs
   - Alert on geographic anomalies

### Log Examples

```python
# Successful login
logger.info(f"User {user.id} logged in successfully from IP {request.client.host}")

# Failed login
logger.warning(f"Failed login attempt for user {user.id} from IP {request.client.host}")

# Account lockout
logger.warning(
    f"Account locked for user {user.id} due to {user.failed_login_attempts} "
    f"failed attempts. Locked until {user.locked_until}"
)

# Token refresh
logger.info(f"Access token refreshed for user {user_id}")
```

---

## Testing

### Unit Tests

```python
import pytest
from datetime import datetime, timedelta

def test_password_hashing():
    """Test password hashing and verification."""
    password = "SecurePass123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_account_lockout():
    """Test account lockout after failed attempts."""
    user = create_test_user()

    # Simulate 5 failed attempts
    for i in range(5):
        await increment_failed_login_attempts(session, user)

    # Check if account is locked
    assert await check_account_lockout(user) is True
    assert user.failed_login_attempts == 5
    assert user.locked_until is not None

def test_token_expiration():
    """Test access token expiration."""
    user_id = 1
    token = create_access_token(user_id)

    # Token should be valid immediately
    payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert payload['sub'] == str(user_id)
    assert payload['type'] == 'access'

    # Token should expire after configured time
    # (Test with mocked time)
```

### Integration Tests

```python
def test_login_flow(client):
    """Test complete login flow."""
    # Register user
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 201

    # Login
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data

    # Access protected route
    response = client.get('/tasks', headers={
        'Authorization': f"Bearer {data['access_token']}"
    })
    assert response.status_code == 200
```

---

## Troubleshooting

### Common Issues

**Issue:** "Invalid authentication credentials"
- **Cause:** Expired or invalid access token
- **Solution:** Use refresh token to get new access token

**Issue:** "Account temporarily locked"
- **Cause:** Too many failed login attempts
- **Solution:** Wait for lockout period to expire (30 minutes)

**Issue:** "Invalid refresh token"
- **Cause:** Refresh token expired or invalid
- **Solution:** User must log in again

**Issue:** "Password must contain at least one special character"
- **Cause:** Password doesn't meet requirements
- **Solution:** Include special characters in password

### Debug Mode

Enable detailed logging for debugging:

```python
# In config.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Generate strong JWT secret (32+ characters)
- [ ] Run database migration
- [ ] Configure HTTPS/TLS
- [ ] Set appropriate token expiration times
- [ ] Enable security headers
- [ ] Configure CORS policies
- [ ] Set up log aggregation
- [ ] Configure monitoring and alerting
- [ ] Test all authentication flows
- [ ] Review error messages
- [ ] Document token storage strategy
- [ ] Set up backup and recovery

### Environment Variables

Ensure all required environment variables are set:

```bash
# Required
BETTER_AUTH_SECRET=<strong-random-secret>
DATABASE_URL=<neon-postgres-url>

# Optional (with defaults)
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=30
```

---

## Support

For security issues or questions:
- Review SECURITY_ASSESSMENT.md for detailed security analysis
- Check OWASP Authentication Cheat Sheet
- Consult auth-skill patterns in `.claude/skills/auth-skill/`

**Last Updated:** 2026-01-15
