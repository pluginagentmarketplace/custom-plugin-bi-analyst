---
name: frontend-development
description: Build modern, responsive web applications with HTML, CSS, JavaScript/TypeScript, and modern frameworks like React, Vue, and Angular. Use when working on web UI, frontend architecture, styling, or web frameworks.
---

# Frontend Development Skill

## Quick Start

### HTML5 Fundamentals
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Web Page</title>
  </head>
  <body>
    <header>Content</header>
    <main>Main content</main>
    <footer>Footer</footer>
  </body>
</html>
```

### CSS3 Styling with Tailwind
```html
<div class="grid grid-cols-3 gap-4 p-6">
  <div class="bg-blue-500 text-white rounded-lg p-4">
    Card content
  </div>
</div>
```

### JavaScript ES6+ Basics
```javascript
// Arrow functions
const add = (a, b) => a + b;

// Destructuring
const { name, age } = person;

// Template literals
const greeting = `Hello, ${name}!`;

// Promises & Async/Await
const fetchData = async () => {
  const response = await fetch('/api/data');
  return response.json();
};
```

### React Component Example
```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}

export default Counter;
```

## Framework Selection Guide

| Framework | Best For | Learning Curve |
|-----------|----------|-----------------|
| **React** | Large SPAs, component reusability | Medium |
| **Vue** | Rapid development, smaller teams | Low |
| **Angular** | Enterprise applications | High |
| **Next.js** | Full-stack, SSR/SSG | Medium |
| **Svelte** | Small bundles, performance | Medium |

## Performance Optimization Checklist
- [ ] Implement code splitting and lazy loading
- [ ] Optimize images (WebP, responsive sizes)
- [ ] Minimize JavaScript bundle size
- [ ] Use CSS-in-JS or utility-first CSS
- [ ] Implement caching strategies
- [ ] Monitor Core Web Vitals (CLS, FID, LCP)
- [ ] Set up critical CSS
- [ ] Use service workers for offline support

## Testing Best Practices
```javascript
// Jest + React Testing Library
import { render, screen } from '@testing-library/react';

test('button click updates count', () => {
  render(<Counter />);
  const button = screen.getByRole('button');
  fireEvent.click(button);
  expect(screen.getByText(/Count: 1/)).toBeInTheDocument();
});
```

## Common Patterns

### State Management Pattern
- Local state (useState)
- Context API for cross-cutting concerns
- Redux/Zustand for complex state
- Recoil for atom-based state

### Component Architecture
- Presentational vs Container components
- Compound components pattern
- Render props pattern
- Custom hooks for logic reuse

### API Integration
- Fetch API or Axios for HTTP requests
- SWR or React Query for data fetching
- Optimistic updates for better UX
- Error boundary for error handling

## Resources
- [MDN Web Docs](https://developer.mozilla.org)
- [React Documentation](https://react.dev)
- [Web.dev](https://web.dev) - Performance & Best Practices
- [Tailwind CSS Docs](https://tailwindcss.com)
