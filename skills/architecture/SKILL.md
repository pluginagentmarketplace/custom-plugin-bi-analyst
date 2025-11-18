---
name: system-architecture
description: Design large-scale systems, understand software architecture patterns, implement design patterns, and master data structures and algorithms. Use when designing systems, choosing architectures, or solving complex engineering problems.
---

# System Architecture & Design Skill

## Quick Start

### System Design Interview Pattern

**Ask clarifying questions:**
- Scale: How many users/requests per second?
- Available: Do we need high availability?
- Latency: What's acceptable response time?
- Consistency: Strong or eventual consistency?

### Basic Architecture Diagram
```
┌─────────────────────────────────────────────────────┐
│                    Load Balancer                    │
└─────────────────────────────────────────────────────┘
              ↓              ↓              ↓
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Server 1 │ │ Server 2 │ │ Server 3 │
└──────────┘ └──────────┘ └──────────┘
              ↓              ↓              ↓
┌─────────────────────────────────────────────────────┐
│         Database Cluster (Master-Slave)             │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│         Cache Layer (Redis/Memcached)               │
└─────────────────────────────────────────────────────┘
```

## Architectural Patterns

### Monolithic Architecture
```
┌────────────────────────────────┐
│       Single Application       │
├────────────────────────────────┤
│  Authentication │ User Service │
│──────────────────────────────│
│  Order Service  │ Payment Svc │
├────────────────────────────────┤
│   Single Database (Shared)     │
└────────────────────────────────┘
```

Pros: Simple, easier to test, good for startups
Cons: Hard to scale, tech lock-in, deployment issues

### Microservices Architecture
```
Auth Service ─────┐
User Service ─────┤
Order Service ─────┼─── API Gateway ─── Client
Payment Service ───┤
Notification Svc ──┘

Each service:
- Independent codebase
- Own database
- Deployed separately
- Communicates via APIs/events
```

Pros: Independent scaling, tech flexibility
Cons: Complex, distributed systems challenges

### Serverless Architecture
```
AWS Lambda Functions ─────┐
│                         │
├─── API Gateway ────── Client
│                         │
Event Sources ────────────┘
  - DynamoDB Streams
  - S3 Events
  - SNS/SQS
```

Pros: No server management, pay per use
Cons: Cold starts, vendor lock-in

### Event-Driven Architecture
```
┌──────────────┐
│  Producer    │ ──→ Event Bus (Kafka/RabbitMQ) ──→ ┌──────────────┐
└──────────────┘                                   │  Consumer 1  │
                                                  └──────────────┘
                                                  ┌──────────────┐
                                                  │  Consumer 2  │
                                                  └──────────────┘
```

### CQRS (Command Query Responsibility Segregation)
```
Write Path (Command):
User Input → Command Handler → Update Model → Event Store

Read Path (Query):
Query → Read Model (Denormalized) → Result
        ↑ (Updated by events)
```

## Database Design

### Normalization (Relational)
```sql
-- 1NF: Atomic values
-- 2NF: No partial dependencies
-- 3NF: No transitive dependencies

Users Table:
┌────┬──────────┬──────────────┐
│ ID │  Name    │  Email       │
├────┼──────────┼──────────────┤
│ 1  │  Alice   │ alice@ex.com │
│ 2  │  Bob     │ bob@ex.com   │
└────┴──────────┴──────────────┘

Posts Table:
┌────┬──────────┬─────────┐
│ ID │  Title   │ User_ID │
├────┼──────────┼─────────┤
│ 1  │  My Post │  1      │
│ 2  │  His Post│  2      │
└────┴──────────┴─────────┘
```

### NoSQL Design (Denormalization)
```json
{
  "_id": "user_1",
  "name": "Alice",
  "email": "alice@example.com",
  "posts": [
    {
      "title": "My Post",
      "content": "...",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ]
}
```

## Scalability Patterns

### Horizontal Scaling
```
Request → Load Balancer
           ├─→ Server 1
           ├─→ Server 2
           └─→ Server 3
Database with replication
```

### Vertical Scaling
```
Upgrade server hardware:
  8GB RAM → 32GB RAM
  1 CPU → 8 CPU
  100GB SSD → 1TB SSD
```

### Database Sharding
```
User ID 1-1000   → Database A
User ID 1001-2000→ Database B
User ID 2001-3000→ Database C

Shard Key determines which database to use
```

### Caching Strategy
```
L1: Application Memory Cache (Fast, small)
    ↓ Miss
L2: Redis/Memcached (Medium, distributed)
    ↓ Miss
L3: Primary Database (Slow, authoritative)
```

## Design Patterns

### Creational Patterns

**Singleton Pattern**
```python
class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

db = Database()
db2 = Database()
assert db is db2  # Same instance
```

**Factory Pattern**
```python
class PaymentProcessorFactory:
    @staticmethod
    def create(payment_method):
        if payment_method == 'credit_card':
            return CreditCardProcessor()
        elif payment_method == 'paypal':
            return PayPalProcessor()
        raise ValueError(f"Unknown method: {payment_method}")
```

### Behavioral Patterns

**Observer Pattern**
```python
class EventEmitter:
    def __init__(self):
        self.listeners = {}

    def on(self, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    def emit(self, event, data):
        for callback in self.listeners.get(event, []):
            callback(data)
```

**Strategy Pattern**
```python
class SortStrategy:
    def sort(self, data):
        raise NotImplementedError

class QuickSort(SortStrategy):
    def sort(self, data):
        # Implementation
        pass

class MergeSort(SortStrategy):
    def sort(self, data):
        # Implementation
        pass

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort(self, data):
        return self.strategy.sort(data)
```

## Data Structures Performance

| Structure | Access | Search | Insert | Delete |
|-----------|--------|--------|--------|--------|
| Array | O(1) | O(n) | O(n) | O(n) |
| Linked List | O(n) | O(n) | O(1) | O(1) |
| Binary Search Tree | O(log n) | O(log n) | O(log n) | O(log n) |
| Hash Table | O(1) | O(1) | O(1) | O(1) |
| Heap | O(log n) | O(n) | O(log n) | O(log n) |

## Algorithms Complexity

### Big O Notation
```
O(1)      - Constant time
O(log n)  - Logarithmic
O(n)      - Linear
O(n log n)- Linearithmic
O(n²)     - Quadratic
O(n³)     - Cubic
O(2ⁿ)     - Exponential
O(n!)     - Factorial
```

### Example Algorithms
```python
# O(1) - Direct access
def get_first(arr):
    return arr[0]

# O(log n) - Binary search
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# O(n) - Linear search
def linear_search(arr, target):
    for i, item in enumerate(arr):
        if item == target:
            return i
    return -1

# O(n²) - Bubble sort
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
```

## CAP Theorem

For distributed systems, you can have:
- **C**onsistency: All nodes have same data
- **A**vailability: System always responsive
- **P**artition tolerance: System works despite network failures

⚠️ Choose 2 of 3:
- **CA**: Strong consistency + Availability (no network issues)
- **AP**: Availability + Partition tolerance (eventual consistency)
- **CP**: Consistency + Partition tolerance (may be unavailable)

## SOLID Principles

**S**ingle Responsibility: One reason to change
**O**pen/Closed: Open for extension, closed for modification
**L**iskov Substitution: Derived can substitute base
**I**nterface Segregation: Many specific interfaces
**D**ependency Inversion: Depend on abstractions

## Load Balancing Strategies

```
Round Robin:      Server 1 → Server 2 → Server 3 → Server 1
Least Connections: Route to server with fewest active connections
IP Hash:          Same client IP always goes to same server
Weighted:         Distribute based on server capacity
```

## Resources
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Design Patterns](https://refactoring.guru/design-patterns)
- [Big O Cheat Sheet](https://www.bigocheatsheet.com/)
