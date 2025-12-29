# System Architecture Guide

> BI Analyst Plugin - Architecture Skill Reference
> Version: 1.0.0

## Overview

Comprehensive guide covering system design patterns, architectural styles, scalability strategies, and best practices for building robust, maintainable systems.

## Table of Contents

1. [Architecture Styles](#architecture-styles)
2. [Design Patterns](#design-patterns)
3. [Scalability Patterns](#scalability-patterns)
4. [Data Architecture](#data-architecture)
5. [Resilience Patterns](#resilience-patterns)
6. [System Design Examples](#system-design-examples)

---

## Architecture Styles

### Comparison Matrix

| Style | Complexity | Scalability | Team Size | Use Case |
|-------|------------|-------------|-----------|----------|
| Monolith | Low | Vertical | Small | MVP, Startups |
| Modular Monolith | Medium | Vertical | Medium | Growing Products |
| Microservices | High | Horizontal | Large | Enterprise, Scale |
| Serverless | Medium | Auto | Any | Event-driven, Variable Load |
| Event-Driven | High | Horizontal | Large | Real-time, Async |

### Microservices Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                            │
│                   (Authentication, Rate Limiting)           │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │  User   │    │  Order  │    │ Payment │    │Inventory│
    │ Service │    │ Service │    │ Service │    │ Service │
    └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
         │              │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │  User   │    │  Order  │    │ Payment │    │Inventory│
    │   DB    │    │   DB    │    │   DB    │    │   DB    │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
                          │
              ┌───────────┴───────────┐
              │     Message Queue     │
              │   (RabbitMQ/Kafka)    │
              └───────────────────────┘
```

### Clean Architecture (Hexagonal)

```
                    ┌──────────────────────┐
                    │    Infrastructure    │
                    │  (DB, HTTP, Queue)   │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │      Application     │
                    │   (Use Cases, DTOs)  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │        Domain        │
                    │ (Entities, Services) │
                    └──────────────────────┘
```

```python
# Domain Layer - Pure business logic
class Order:
    def __init__(self, id: str, customer_id: str, items: list[OrderItem]):
        self.id = id
        self.customer_id = customer_id
        self.items = items
        self.status = OrderStatus.PENDING

    def calculate_total(self) -> Decimal:
        return sum(item.price * item.quantity for item in self.items)

    def can_cancel(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]


# Application Layer - Use cases
class CreateOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        inventory_service: InventoryService,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.inventory_service = inventory_service
        self.event_publisher = event_publisher

    async def execute(self, command: CreateOrderCommand) -> Order:
        # Check inventory
        await self.inventory_service.check_availability(command.items)

        # Create order
        order = Order(
            id=generate_id(),
            customer_id=command.customer_id,
            items=command.items,
        )

        # Persist
        await self.order_repository.save(order)

        # Publish event
        await self.event_publisher.publish(OrderCreatedEvent(order))

        return order


# Infrastructure Layer - Implementations
class PostgresOrderRepository(OrderRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, order: Order) -> None:
        db_order = OrderModel.from_domain(order)
        self.db.add(db_order)
        await self.db.commit()
```

---

## Design Patterns

### Repository Pattern

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class Repository(ABC, Generic[T]):
    """Abstract repository interface."""

    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass

    @abstractmethod
    async def find_all(self, **filters) -> list[T]:
        pass


class UserRepository(Repository[User]):
    """User-specific repository with custom queries."""

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def find_active(self) -> list[User]:
        pass
```

### CQRS Pattern

```python
# Commands (Write Side)
@dataclass
class CreateUserCommand:
    email: str
    name: str
    password: str


class CreateUserHandler:
    def __init__(self, repository: UserRepository, hasher: PasswordHasher):
        self.repository = repository
        self.hasher = hasher

    async def handle(self, command: CreateUserCommand) -> str:
        hashed_password = self.hasher.hash(command.password)
        user = User(
            id=generate_id(),
            email=command.email,
            name=command.name,
            password_hash=hashed_password,
        )
        await self.repository.save(user)
        return user.id


# Queries (Read Side)
@dataclass
class GetUserQuery:
    user_id: str


@dataclass
class UserDTO:
    id: str
    email: str
    name: str
    created_at: datetime


class GetUserHandler:
    def __init__(self, read_db: ReadDatabase):
        self.read_db = read_db

    async def handle(self, query: GetUserQuery) -> Optional[UserDTO]:
        row = await self.read_db.fetch_one(
            "SELECT id, email, name, created_at FROM users_view WHERE id = $1",
            query.user_id
        )
        return UserDTO(**row) if row else None
```

### Saga Pattern (Distributed Transactions)

```python
class OrderSaga:
    """Saga for order processing with compensation."""

    def __init__(
        self,
        order_service: OrderService,
        payment_service: PaymentService,
        inventory_service: InventoryService,
        notification_service: NotificationService,
    ):
        self.order_service = order_service
        self.payment_service = payment_service
        self.inventory_service = inventory_service
        self.notification_service = notification_service

    async def execute(self, order_id: str) -> SagaResult:
        saga_log = SagaLog(saga_id=generate_id())

        try:
            # Step 1: Reserve inventory
            await self.inventory_service.reserve(order_id)
            saga_log.add_step("inventory_reserved")

            # Step 2: Process payment
            await self.payment_service.charge(order_id)
            saga_log.add_step("payment_charged")

            # Step 3: Confirm order
            await self.order_service.confirm(order_id)
            saga_log.add_step("order_confirmed")

            # Step 4: Send notification
            await self.notification_service.send(order_id)
            saga_log.add_step("notification_sent")

            return SagaResult(success=True, saga_log=saga_log)

        except Exception as e:
            # Compensate in reverse order
            await self._compensate(saga_log)
            return SagaResult(success=False, error=str(e), saga_log=saga_log)

    async def _compensate(self, saga_log: SagaLog):
        """Rollback completed steps in reverse order."""
        for step in reversed(saga_log.completed_steps):
            if step == "payment_charged":
                await self.payment_service.refund(saga_log.order_id)
            elif step == "inventory_reserved":
                await self.inventory_service.release(saga_log.order_id)
            elif step == "order_confirmed":
                await self.order_service.cancel(saga_log.order_id)
```

---

## Scalability Patterns

### Horizontal Scaling

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
    │  Instance 1 │   │  Instance 2 │   │  Instance 3 │
    │   (API)     │   │   (API)     │   │   (API)     │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                    ┌────────▼────────┐
                    │   Shared Cache  │
                    │     (Redis)     │
                    └────────┬────────┘
                    ┌────────▼────────┐
                    │   Database      │
                    │ Primary + Read  │
                    │   Replicas      │
                    └─────────────────┘
```

### Caching Strategies

```python
from enum import Enum
from typing import Optional, Callable, TypeVar
import redis
import json

T = TypeVar('T')


class CacheStrategy(Enum):
    CACHE_ASIDE = "cache_aside"
    READ_THROUGH = "read_through"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"


class CacheAside:
    """Cache-aside (Lazy Loading) pattern."""

    def __init__(self, cache: redis.Redis, ttl: int = 3600):
        self.cache = cache
        self.ttl = ttl

    async def get(
        self,
        key: str,
        fetch_fn: Callable[[], T],
        ttl: Optional[int] = None
    ) -> T:
        # Try cache first
        cached = await self.cache.get(key)
        if cached:
            return json.loads(cached)

        # Cache miss - fetch from source
        value = await fetch_fn()

        # Update cache
        await self.cache.setex(
            key,
            ttl or self.ttl,
            json.dumps(value)
        )

        return value

    async def invalidate(self, key: str) -> None:
        await self.cache.delete(key)


# Usage
cache = CacheAside(redis_client)

user = await cache.get(
    f"user:{user_id}",
    lambda: user_repository.get(user_id),
    ttl=1800
)
```

### Database Sharding

```python
from hashlib import md5


class ShardRouter:
    """Route queries to appropriate shard."""

    def __init__(self, shard_count: int):
        self.shard_count = shard_count
        self.shards = {}

    def get_shard_id(self, partition_key: str) -> int:
        """Consistent hashing to determine shard."""
        hash_value = int(md5(partition_key.encode()).hexdigest(), 16)
        return hash_value % self.shard_count

    def get_connection(self, partition_key: str):
        """Get database connection for shard."""
        shard_id = self.get_shard_id(partition_key)
        return self.shards[shard_id]


# Usage
router = ShardRouter(shard_count=4)

# Route user queries by user_id
shard = router.get_shard_id(user_id)
connection = router.get_connection(user_id)
```

---

## Resilience Patterns

### Circuit Breaker

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, TypeVar
import asyncio

T = TypeVar('T')


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_requests: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: datetime | None = None

    async def call(self, fn: Callable[[], T]) -> T:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitOpenError("Circuit is open")

        try:
            result = await fn()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_requests:
                self.state = CircuitState.CLOSED
                self.failure_count = 0

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(
            seconds=self.recovery_timeout
        )
```

### Retry with Exponential Backoff

```python
import asyncio
import random
from typing import Callable, TypeVar

T = TypeVar('T')


async def retry_with_backoff(
    fn: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> T:
    """Retry with exponential backoff and optional jitter."""

    for attempt in range(max_retries):
        try:
            return await fn()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            # Calculate delay
            delay = min(base_delay * (exponential_base ** attempt), max_delay)

            # Add jitter to prevent thundering herd
            if jitter:
                delay = delay * (0.5 + random.random())

            await asyncio.sleep(delay)
```

---

## System Design Examples

### URL Shortener Design

```
Requirements:
- Shorten long URLs to ~7 character codes
- Handle 100M new URLs/month
- 10B redirects/month

Design:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│     CDN     │───▶│     LB      │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                   ┌─────────────────────────┼─────────────────────────┐
                   │                         │                         │
            ┌──────▼──────┐           ┌──────▼──────┐           ┌──────▼──────┐
            │  API Server │           │  API Server │           │  API Server │
            └──────┬──────┘           └──────┬──────┘           └──────┬──────┘
                   │                         │                         │
                   └─────────────────────────┼─────────────────────────┘
                                             │
                   ┌─────────────────────────┼─────────────────────────┐
                   │                         │                         │
            ┌──────▼──────┐           ┌──────▼──────┐           ┌──────▼──────┐
            │    Cache    │           │    Cache    │           │    Cache    │
            │   (Redis)   │           │   (Redis)   │           │   (Redis)   │
            └─────────────┘           └─────────────┘           └─────────────┘
                                             │
                                      ┌──────▼──────┐
                                      │   Database  │
                                      │ (Cassandra) │
                                      └─────────────┘

Key Decisions:
- Base62 encoding for short codes
- Distributed ID generation (Snowflake)
- Read-heavy: 100:1 read/write ratio
- Cache hot URLs (90% hit rate expected)
```

---

## Resources

- [Martin Fowler - Patterns of Enterprise Application Architecture](https://martinfowler.com/books/eaa.html)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Designing Data-Intensive Applications](https://dataintensive.net)
- [Cloud Design Patterns](https://docs.microsoft.com/azure/architecture/patterns)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected)

---

*Last Updated: 2025-01-01*
*BI Analyst Plugin - Architecture Skill*
