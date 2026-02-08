---
name: backend-routes
description: Create backend routes, handle HTTP requests and responses, and connect to databases for web applications.
---

# Backend Skill – Routes, Requests/Responses, Database Connection

## Instructions

1. **Route Generation**
   - Define RESTful endpoints (`GET`, `POST`, `PUT`, `DELETE`)
   - Organize routes by resource or module
   - Use route parameters and query strings effectively

2. **Request Handling**
   - Parse incoming requests (body, params, query)
   - Validate and sanitize user input
   - Handle authentication and authorization

3. **Response Management**
   - Send proper HTTP status codes
   - Return JSON or HTML responses
   - Handle errors gracefully with descriptive messages

4. **Database Connection**
   - Establish connection to SQL or NoSQL databases
   - Use ORMs or query builders for CRUD operations
   - Handle connection errors and pooling

## Best Practices
- Follow RESTful API conventions
- Keep route handlers modular and reusable
- Validate inputs before database operations
- Handle errors and exceptions consistently
- Secure sensitive data (passwords, tokens)
- Log requests and responses for debugging

## Example Structure
```javascript
// Express.js Example

const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const { Pool } = require('pg'); // PostgreSQL

app.use(bodyParser.json());

// Database connection
const pool = new Pool({
  user: 'dbuser',
  host: 'localhost',
  database: 'mydb',
  password: 'password',
  port: 5432,
});

// Routes
app.get('/users', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM users');
    res.status(200).json(result.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/users', async (req, res) => {
  const { name, email } = req.body;
  try {
    const result = await pool.query(
      'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *',
      [name, email]
    );
    res.status(201).json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start server
app.listen(3000, () => {
  console.log('Server running on port 3000');
});


