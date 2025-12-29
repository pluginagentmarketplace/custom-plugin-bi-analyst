# Programming Languages Guide

> BI Analyst Plugin - Languages Skill Reference
> Version: 1.0.0

## Overview

Comprehensive guide covering programming language fundamentals, paradigms, and best practices across Python, Go, Rust, JavaScript/TypeScript, and other major languages.

## Table of Contents

1. [Language Selection Guide](#language-selection-guide)
2. [Python Best Practices](#python-best-practices)
3. [Go Best Practices](#go-best-practices)
4. [Rust Best Practices](#rust-best-practices)
5. [TypeScript Best Practices](#typescript-best-practices)
6. [Cross-Language Patterns](#cross-language-patterns)

---

## Language Selection Guide

### Decision Matrix

| Criterion | Python | Go | Rust | TypeScript | Java |
|-----------|--------|-----|------|------------|------|
| Learning Curve | Easy | Medium | Hard | Medium | Medium |
| Performance | Medium | High | Very High | Medium | High |
| Concurrency | Good | Excellent | Excellent | Good | Good |
| Memory Safety | GC | GC | Compile-time | GC | GC |
| Ecosystem | Vast | Growing | Growing | Vast | Vast |
| Use Cases | ML, Scripts, Web | Cloud, CLI, Microservices | Systems, Performance | Web, Full-stack | Enterprise |

### When to Use Each Language

```
Python → Data Science, ML, Scripting, Rapid Prototyping
Go     → Cloud Infrastructure, Microservices, CLI Tools
Rust   → Systems Programming, Performance-Critical, WebAssembly
TypeScript → Web Applications, Node.js Backend, Full-Stack
Java   → Enterprise Applications, Android, Large Teams
C/C++  → Embedded Systems, Game Engines, Performance
```

---

## Python Best Practices

### Modern Python (3.10+)

```python
from dataclasses import dataclass
from typing import Protocol, TypeVar, Generic
from collections.abc import Sequence
from functools import cache


# Type hints with generics
T = TypeVar('T')


class Repository(Protocol[T]):
    """Protocol for repository pattern."""
    def get(self, id: int) -> T | None: ...
    def save(self, entity: T) -> T: ...
    def delete(self, id: int) -> bool: ...


# Dataclasses for data models
@dataclass(frozen=True, slots=True)
class User:
    """Immutable user model with slots for memory efficiency."""
    id: int
    name: str
    email: str
    active: bool = True


# Pattern matching (Python 3.10+)
def process_event(event: dict) -> str:
    match event:
        case {"type": "login", "user": user}:
            return f"User {user} logged in"
        case {"type": "logout", "user": user}:
            return f"User {user} logged out"
        case {"type": "error", "message": msg}:
            return f"Error: {msg}"
        case _:
            return "Unknown event"


# Caching with functools
@cache
def fibonacci(n: int) -> int:
    """Cached fibonacci calculation."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# Context managers
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def timer(name: str) -> Iterator[None]:
    """Context manager for timing code blocks."""
    import time
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{name}: {elapsed:.4f}s")


# Async patterns
import asyncio
from typing import Awaitable


async def gather_with_concurrency(
    tasks: list[Awaitable[T]],
    limit: int = 10
) -> list[T]:
    """Run async tasks with concurrency limit."""
    semaphore = asyncio.Semaphore(limit)

    async def limited_task(task: Awaitable[T]) -> T:
        async with semaphore:
            return await task

    return await asyncio.gather(*(limited_task(t) for t in tasks))
```

### Project Structure

```
project/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── services.py
│       └── api/
│           ├── __init__.py
│           └── routes.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── pyproject.toml
└── README.md
```

---

## Go Best Practices

### Idiomatic Go

```go
package main

import (
    "context"
    "errors"
    "fmt"
    "sync"
    "time"
)

// Use interfaces for abstraction
type UserRepository interface {
    Get(ctx context.Context, id int) (*User, error)
    Save(ctx context.Context, user *User) error
}

// Struct with proper tags
type User struct {
    ID        int       `json:"id" db:"id"`
    Name      string    `json:"name" db:"name"`
    Email     string    `json:"email" db:"email"`
    CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// Custom errors
var (
    ErrUserNotFound = errors.New("user not found")
    ErrInvalidInput = errors.New("invalid input")
)

// Error wrapping
func (r *repository) Get(ctx context.Context, id int) (*User, error) {
    user, err := r.db.GetUser(ctx, id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, ErrUserNotFound
        }
        return nil, fmt.Errorf("failed to get user %d: %w", id, err)
    }
    return user, nil
}

// Concurrency with goroutines and channels
func processItems(items []Item) []Result {
    results := make(chan Result, len(items))
    var wg sync.WaitGroup

    for _, item := range items {
        wg.Add(1)
        go func(item Item) {
            defer wg.Done()
            results <- process(item)
        }(item)
    }

    go func() {
        wg.Wait()
        close(results)
    }()

    var output []Result
    for result := range results {
        output = append(output, result)
    }
    return output
}

// Context for cancellation
func longRunningTask(ctx context.Context) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-time.After(5 * time.Second):
        return nil
    }
}

// Options pattern for flexible APIs
type ServerOption func(*Server)

func WithPort(port int) ServerOption {
    return func(s *Server) {
        s.port = port
    }
}

func WithTimeout(timeout time.Duration) ServerOption {
    return func(s *Server) {
        s.timeout = timeout
    }
}

func NewServer(opts ...ServerOption) *Server {
    s := &Server{
        port:    8080,
        timeout: 30 * time.Second,
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

---

## Rust Best Practices

### Safe and Idiomatic Rust

```rust
use std::error::Error;
use std::fmt;

// Custom error types
#[derive(Debug)]
pub enum AppError {
    NotFound(String),
    ValidationError(String),
    DatabaseError(String),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::NotFound(msg) => write!(f, "Not found: {}", msg),
            AppError::ValidationError(msg) => write!(f, "Validation error: {}", msg),
            AppError::DatabaseError(msg) => write!(f, "Database error: {}", msg),
        }
    }
}

impl Error for AppError {}

// Result type alias
type Result<T> = std::result::Result<T, AppError>;

// Struct with derive macros
#[derive(Debug, Clone, PartialEq)]
pub struct User {
    pub id: u64,
    pub name: String,
    pub email: String,
}

// Traits for abstraction
pub trait Repository<T> {
    fn get(&self, id: u64) -> Result<Option<T>>;
    fn save(&mut self, entity: T) -> Result<T>;
    fn delete(&mut self, id: u64) -> Result<bool>;
}

// Implementation with generics
impl<T: Clone> Repository<T> for Vec<(u64, T)> {
    fn get(&self, id: u64) -> Result<Option<T>> {
        Ok(self.iter().find(|(i, _)| *i == id).map(|(_, t)| t.clone()))
    }

    fn save(&mut self, entity: T) -> Result<T> {
        // Implementation
        Ok(entity)
    }

    fn delete(&mut self, id: u64) -> Result<bool> {
        let len = self.len();
        self.retain(|(i, _)| *i != id);
        Ok(self.len() < len)
    }
}

// Error handling with ? operator
fn process_user(repo: &impl Repository<User>, id: u64) -> Result<String> {
    let user = repo.get(id)?
        .ok_or_else(|| AppError::NotFound(format!("User {}", id)))?;

    Ok(format!("Processed: {}", user.name))
}

// Iterator patterns
fn sum_even_squares(numbers: &[i32]) -> i32 {
    numbers
        .iter()
        .filter(|&&n| n % 2 == 0)
        .map(|&n| n * n)
        .sum()
}

// Async with tokio
use tokio::sync::mpsc;

async fn async_processor(mut rx: mpsc::Receiver<String>) {
    while let Some(msg) = rx.recv().await {
        println!("Received: {}", msg);
    }
}
```

---

## TypeScript Best Practices

### Type-Safe TypeScript

```typescript
// Strict types with utility types
interface User {
  readonly id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  metadata?: Record<string, unknown>;
}

// Partial, Pick, Omit utilities
type UserUpdate = Partial<Omit<User, 'id'>>;
type UserSummary = Pick<User, 'id' | 'name'>;

// Discriminated unions
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function processResult<T>(result: Result<T>): T | null {
  if (result.success) {
    return result.data;
  }
  console.error(result.error);
  return null;
}

// Generic constraints
interface HasId {
  id: number;
}

function findById<T extends HasId>(items: T[], id: number): T | undefined {
  return items.find(item => item.id === id);
}

// Type guards
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value &&
    'email' in value
  );
}

// Mapped types
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Optional<T> = {
  [P in keyof T]?: T[P];
};

// Template literal types
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type APIEndpoint = `/api/v1/${string}`;
type Route = `${HTTPMethod} ${APIEndpoint}`;

// Conditional types
type Unwrap<T> = T extends Promise<infer U> ? U : T;
type ArrayElement<T> = T extends (infer E)[] ? E : never;

// Class with proper encapsulation
class Repository<T extends HasId> {
  private items: Map<number, T> = new Map();

  get(id: number): T | undefined {
    return this.items.get(id);
  }

  save(item: T): T {
    this.items.set(item.id, item);
    return item;
  }

  delete(id: number): boolean {
    return this.items.delete(id);
  }

  findAll(): T[] {
    return Array.from(this.items.values());
  }
}

// Async patterns
async function fetchWithRetry<T>(
  fn: () => Promise<T>,
  retries: number = 3,
  delay: number = 1000
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (retries <= 0) throw error;
    await new Promise(resolve => setTimeout(resolve, delay));
    return fetchWithRetry(fn, retries - 1, delay * 2);
  }
}
```

---

## Cross-Language Patterns

### Common Design Patterns

| Pattern | Python | Go | Rust | TypeScript |
|---------|--------|-----|------|------------|
| Singleton | `@lru_cache` | `sync.Once` | `lazy_static!` | Module scope |
| Factory | `classmethod` | Constructor func | `impl Default` | Factory function |
| Builder | Fluent methods | Options pattern | Builder pattern | Method chaining |
| Observer | `abc.ABC` | Channels | Traits + callbacks | EventEmitter |
| Strategy | Protocol/ABC | Interfaces | Traits | Interfaces |

### Error Handling Comparison

```python
# Python - Exceptions
try:
    result = risky_operation()
except ValueError as e:
    handle_error(e)
```

```go
// Go - Explicit error returns
result, err := riskyOperation()
if err != nil {
    return fmt.Errorf("operation failed: %w", err)
}
```

```rust
// Rust - Result type
match risky_operation() {
    Ok(result) => use_result(result),
    Err(e) => handle_error(e),
}
// Or with ? operator
let result = risky_operation()?;
```

```typescript
// TypeScript - Try/catch with types
try {
  const result = riskyOperation();
} catch (error) {
  if (error instanceof CustomError) {
    handleError(error);
  }
}
```

---

## Resources

- [Python Documentation](https://docs.python.org)
- [Go Documentation](https://go.dev/doc)
- [Rust Book](https://doc.rust-lang.org/book)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Effective Go](https://go.dev/doc/effective_go)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example)

---

*Last Updated: 2025-01-01*
*BI Analyst Plugin - Languages Skill*
