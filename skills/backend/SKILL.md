---
name: backend-development
description: Build scalable server-side applications with Node.js, Python, databases, APIs, and microservices. Use when working on server architecture, databases, API design, authentication, or backend frameworks.
---

# Backend Development Skill

## Quick Start

### Express.js REST API
```javascript
import express from 'express';
const app = express();

app.use(express.json());

// GET endpoint
app.get('/api/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  res.json(user);
});

// POST endpoint with validation
app.post('/api/users', async (req, res) => {
  const { email, name } = req.body;
  const user = await db.users.create({ email, name });
  res.status(201).json(user);
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### FastAPI Python Backend
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.get_user(user_id)
    return user

@app.post("/users")
async def create_user(user: User):
    new_user = await db.create_user(user)
    return new_user
```

### GraphQL Query
```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    posts {
      id
      title
      content
    }
  }
}
```

### Database Design Pattern
```sql
-- Normalized relational design
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  title VARCHAR(255),
  content TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for common queries
CREATE INDEX idx_posts_user_id ON posts(user_id);
```

## API Design Patterns

### RESTful API Best Practices
```
GET    /api/v1/users              - List all users
GET    /api/v1/users/:id          - Get specific user
POST   /api/v1/users              - Create user
PUT    /api/v1/users/:id          - Update user
DELETE /api/v1/users/:id          - Delete user
POST   /api/v1/users/:id/posts    - Create post for user
```

### Error Handling
```javascript
// Structured error response
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email is required",
    "details": { "field": "email" },
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Authentication & Authorization

### JWT Implementation
```javascript
import jwt from 'jsonwebtoken';

// Create token
const token = jwt.sign(
  { userId: user.id, role: user.role },
  process.env.JWT_SECRET,
  { expiresIn: '24h' }
);

// Verify token (middleware)
const authenticateToken = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.sendStatus(401);

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};
```

## Database Selection Guide

| Database | Best For | Trade-offs |
|----------|----------|-----------|
| **PostgreSQL** | ACID compliance, complex queries | More setup |
| **MongoDB** | Flexible schema, rapid dev | Less transaction support |
| **Redis** | Caching, sessions, real-time | In-memory only |
| **Elasticsearch** | Full-text search, analytics | Complex |

## Performance Optimization

### Query Optimization
- [ ] Use indexes for frequently queried fields
- [ ] Implement pagination for large datasets
- [ ] Use database-level aggregation
- [ ] Monitor slow query logs
- [ ] Cache frequently accessed data

### Caching Strategy
```javascript
// Redis caching layer
const cacheKey = `user:${userId}`;
const cached = await redis.get(cacheKey);
if (cached) return JSON.parse(cached);

const user = await db.users.findById(userId);
await redis.setex(cacheKey, 3600, JSON.stringify(user));
return user;
```

## Scaling Patterns
- **Vertical Scaling**: Increase server resources
- **Horizontal Scaling**: Add more servers with load balancing
- **Database Replication**: Master-slave, multi-master
- **Sharding**: Partition data across multiple databases
- **Microservices**: Split into independent services
- **Caching**: Reduce database queries
- **Async Processing**: Use message queues

## Common Frameworks

| Framework | Language | Features |
|-----------|----------|----------|
| **Express** | Node.js | Lightweight, flexible |
| **NestJS** | Node.js | Opinionated, enterprise |
| **Django** | Python | Full-featured, batteries-included |
| **FastAPI** | Python | Modern, async-first |
| **Spring Boot** | Java | Enterprise, mature |
| **Laravel** | PHP | Elegant, community-rich |

## Testing Backend Code
```javascript
describe('User API', () => {
  test('GET /users/:id returns user', async () => {
    const response = await request(app)
      .get('/users/1')
      .expect(200);
    expect(response.body).toHaveProperty('id');
  });

  test('POST /users creates user', async () => {
    const response = await request(app)
      .post('/users')
      .send({ email: 'test@example.com', name: 'Test' })
      .expect(201);
  });
});
```

## Resources
- [REST API Best Practices](https://restfulapi.net)
- [Database Design Patterns](https://www.postgresql.org/docs/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
