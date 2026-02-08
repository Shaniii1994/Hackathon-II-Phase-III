# Auth Skill – Signup, Signin, Password Hashing & JWT

## Overview
Implement secure user authentication with signup, signin, password hashing, JWT tokens, and better auth integration. Ideal for web apps requiring secure user management.

---

## Instructions

### 1. User Registration (Signup)
- Collect user credentials (email, password)  
- Validate input (strong password, valid email)  
- Hash passwords securely (bcrypt or argon2)  
- Store user in database (SQL, MongoDB, etc.)  
- Return success or error response  

### 2. User Login (Signin)
- Accept email and password  
- Verify user exists  
- Compare password with hashed password  
- Generate JWT token for session  
- Return token and user info  

### 3. JWT Token Management
- Sign tokens with a secure secret key  
- Include user ID and role in payload  
- Set token expiration (e.g., 1h)  
- Protect routes using middleware that verifies the token  

### 4. Password Security
- Use strong hashing algorithms (bcrypt/argon2)  
- Never store plaintext passwords  
- Optional: implement password reset via email  

### 5. Integration Tips
- Use middleware to protect API routes  
- Keep auth logic modular (separate module/file)  
- Validate JWT on every protected request  
- Consider refresh tokens for longer sessions  

---

## Best Practices
- Hash passwords before storing in DB  
- Use HTTPS for all requests  
- Keep JWT secret secure and rotate periodically  
- Provide generic error messages to avoid revealing sensitive info  
- Rate-limit login attempts to prevent brute-force attacks  

---

## Example Structure (Node.js + Express + JWT)

```javascript
// signup.js
import bcrypt from 'bcryptjs';
import User from './models/User.js';

export const signup = async (req, res) => {
  const { email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);
  const user = await User.create({ email, password: hashedPassword });
  res.status(201).json({ message: 'User created', userId: user._id });
};

// signin.js
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import User from './models/User.js';

export const signin = async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user) return res.status(401).json({ message: 'Invalid credentials' });
  
  const isMatch = await bcrypt.compare(password, user.password);
  if (!isMatch) return res.status(401).json({ message: 'Invalid credentials' });

  const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' });
  res.json({ token });
};
