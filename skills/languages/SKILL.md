---
name: programming-languages
description: Master programming languages, paradigms, and fundamentals. Learn Python, JavaScript, Go, Rust, Java, C++, and core computer science concepts like data structures and algorithms.
---

# Programming Languages Skill

## Quick Start

### Python Fundamentals
```python
# Variables and data types
name = "Alice"
age = 30
is_active = True

# Data structures
numbers = [1, 2, 3, 4, 5]  # List (mutable)
colors = ('red', 'green', 'blue')  # Tuple (immutable)
person = {'name': 'Bob', 'age': 25}  # Dictionary
unique = {1, 2, 3, 4}  # Set

# Functions
def greet(name, greeting='Hello'):
    return f'{greeting}, {name}!'

# List comprehension
squares = [x**2 for x in range(10)]

# Lambda
multiply = lambda x, y: x * y

# Classes
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def describe(self):
        return f'{self.name} is {self.age} years old'
```

### JavaScript ES6+
```javascript
// Variables
const PI = 3.14159;
let counter = 0;
var deprecated = 'avoid this';

// Objects and arrays
const user = { name: 'Alice', age: 30 };
const numbers = [1, 2, 3, 4, 5];

// Destructuring
const { name, age } = user;
const [first, second, ...rest] = numbers;

// Arrow functions
const add = (a, b) => a + b;
const greet = name => `Hello, ${name}!`;

// Template literals
const message = `User: ${user.name}, Age: ${user.age}`;

// Promise
const promise = new Promise((resolve, reject) => {
    setTimeout(() => resolve('Done!'), 1000);
});

// Async/Await
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Classes
class Dog {
    constructor(name) {
        this.name = name;
    }

    bark() {
        console.log(`${this.name} barks!`);
    }
}
```

### Go Basics
```go
package main

import (
    "fmt"
    "strings"
)

func main() {
    // Variables
    var name string = "Alice"
    age := 30
    active := true

    // Arrays and slices
    numbers := []int{1, 2, 3, 4, 5}
    numbers = append(numbers, 6)

    // Maps
    person := map[string]interface{}{
        "name": "Bob",
        "age":  25,
    }

    // Functions
    result := add(10, 20)
    fmt.Println(result)

    // Structs
    type User struct {
        Name string
        Age  int
    }

    user := User{Name: "Charlie", Age: 35}
    fmt.Println(user.Name)

    // Goroutines
    go doSomethingConcurrently()

    // Channels
    messages := make(chan string)
    go func() {
        messages <- "Hello from goroutine"
    }()
    msg := <-messages
}

func add(a, b int) int {
    return a + b
}

func doSomethingConcurrently() {
    fmt.Println("Running concurrently")
}
```

### Rust Ownership
```rust
fn main() {
    // Ownership
    let s1 = String::from("Hello");
    let s2 = s1;  // s1 is moved, no longer valid

    // Borrowing (References)
    let s3 = String::from("world");
    let len = calculate_length(&s3);  // Immutable borrow
    println!("'{}' has length {}", s3, len);

    // Mutable borrowing
    let mut s4 = String::from("hello");
    change_string(&mut s4);  // Mutable borrow

    // Pattern matching
    let result: Result<i32, String> = Ok(42);
    match result {
        Ok(value) => println!("Value: {}", value),
        Err(e) => println!("Error: {}", e),
    }

    // Iterators
    let v = vec![1, 2, 3, 4, 5];
    let sum: i32 = v.iter().map(|x| x * 2).sum();
}

fn calculate_length(s: &String) -> usize {
    s.len()
}

fn change_string(s: &mut String) {
    s.push_str(", world");
}
```

## Data Structures

### Arrays, Lists, and Vectors
```python
# Python
numbers = [1, 2, 3, 4, 5]           # Dynamic array
numbers.append(6)
numbers.insert(0, 0)
first = numbers.pop(0)

# Time complexity: O(1) average access, O(n) insertion
```

### Linked Lists
```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
```

### Hash Tables / Dictionaries
```python
# O(1) average time complexity for operations
user = {'name': 'Alice', 'age': 30}
user['email'] = 'alice@example.com'
del user['age']

# Check existence
if 'name' in user:
    print(user['name'])
```

### Trees & Graphs
```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

    def inorder(self):
        if self.left:
            self.left.inorder()
        print(self.value)
        if self.right:
            self.right.inorder()
```

## Algorithms

### Sorting
```python
# Built-in
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
sorted(numbers)

# Quick sort
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if x < pivot]
    right = [x for x in arr[1:] if x >= pivot]
    return quick_sort(left) + [pivot] + quick_sort(right)

# Merge sort - O(n log n)
```

### Searching
```python
# Binary search - O(log n)
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
```

### Dynamic Programming
```python
# Fibonacci - O(n) instead of O(2^n)
def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    return memo[n]
```

## Language Paradigms

### Object-Oriented Programming
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return f'{self.name} barks!'

class Cat(Animal):
    def speak(self):
        return f'{self.name} meows!'
```

### Functional Programming
```python
# Pure functions - no side effects
def add(a, b):
    return a + b

# Map, filter, reduce
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))

from functools import reduce
sum_all = reduce(lambda x, y: x + y, numbers)

# Immutability and recursion
def sum_list(lst):
    if not lst:
        return 0
    return lst[0] + sum_list(lst[1:])
```

## Type Systems

### Static Typing (TypeScript, Go, Rust)
```typescript
// TypeScript
interface User {
    name: string;
    age: number;
    isActive: boolean;
}

function greetUser(user: User): string {
    return `Hello, ${user.name}!`;
}
```

### Dynamic Typing (Python, JavaScript)
```python
# Type hints (optional in Python)
def greet(name: str) -> str:
    return f'Hello, {name}!'
```

## Resources
- [Python Official Docs](https://docs.python.org/3/)
- [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [Go Tour](https://tour.golang.org/)
- [Rust Book](https://doc.rust-lang.org/book/)
- [LeetCode](https://leetcode.com/) - Practice data structures & algorithms
