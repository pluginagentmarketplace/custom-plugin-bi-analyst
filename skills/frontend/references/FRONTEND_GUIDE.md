# Frontend Development Guide

> BI Analyst Plugin - Frontend Skill Reference
> Version: 1.0.0

## Overview

This guide covers modern frontend development best practices for building scalable, performant, and accessible web applications. It emphasizes React ecosystem patterns while providing framework-agnostic principles.

## Table of Contents

1. [Component Architecture](#component-architecture)
2. [State Management](#state-management)
3. [Performance Optimization](#performance-optimization)
4. [Accessibility (a11y)](#accessibility)
5. [Testing Strategies](#testing-strategies)
6. [TypeScript Best Practices](#typescript-best-practices)

---

## Component Architecture

### Atomic Design Principles

```
atoms/       → Basic building blocks (Button, Input, Icon)
molecules/   → Simple combinations (SearchBar, FormField)
organisms/   → Complex components (Header, ProductCard)
templates/   → Page layouts (DashboardLayout, AuthLayout)
pages/       → Complete views (HomePage, SettingsPage)
```

### Component Best Practices

```tsx
// ✅ GOOD: Single Responsibility
interface UserAvatarProps {
  name: string;
  imageUrl?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function UserAvatar({ name, imageUrl, size = 'md' }: UserAvatarProps) {
  const initials = name.split(' ').map(n => n[0]).join('');

  return (
    <div className={styles[size]} aria-label={`Avatar for ${name}`}>
      {imageUrl ? (
        <img src={imageUrl} alt={name} />
      ) : (
        <span>{initials}</span>
      )}
    </div>
  );
}

// ❌ BAD: Too many responsibilities
function UserCard({ user, onEdit, onDelete, showActions, theme, locale... }) {
  // 300+ lines doing everything
}
```

### Composition Over Inheritance

```tsx
// Compose components instead of creating deep inheritance
function Card({ children, header, footer }: CardProps) {
  return (
    <article className={styles.card}>
      {header && <header>{header}</header>}
      <main>{children}</main>
      {footer && <footer>{footer}</footer>}
    </article>
  );
}

// Usage with composition
<Card
  header={<CardTitle>Dashboard</CardTitle>}
  footer={<CardActions onSave={save} />}
>
  <MetricsGrid data={metrics} />
</Card>
```

---

## State Management

### State Management Decision Tree

```
Local UI State (form inputs, toggles)
  → useState / useReducer

Shared Component State (sibling communication)
  → Lift state up / Context

Server Cache State (API data)
  → TanStack Query / SWR

Global App State (auth, theme, preferences)
  → Zustand / Redux Toolkit

URL State (filters, pagination, search)
  → URL params + React Router
```

### TanStack Query Pattern

```tsx
// queries/useUsers.ts
export function useUsers(filters: UserFilters) {
  return useQuery({
    queryKey: ['users', filters],
    queryFn: () => api.getUsers(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000,   // 30 minutes cache
  });
}

// mutations/useCreateUser.ts
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('User created successfully');
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });
}
```

---

## Performance Optimization

### Key Optimization Techniques

| Technique | When to Use | Impact |
|-----------|-------------|--------|
| `React.memo` | Expensive re-renders | High |
| `useMemo` | Expensive calculations | Medium |
| `useCallback` | Callbacks in deps | Medium |
| Code Splitting | Large bundles | Very High |
| Virtualization | Long lists (100+ items) | Very High |
| Image Optimization | Image-heavy pages | High |

### Code Splitting Example

```tsx
// Route-based splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
const Analytics = lazy(() => import('./pages/Analytics'));

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
}
```

### Virtualization for Long Lists

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualizedList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: virtualRow.start,
              height: virtualRow.size,
            }}
          >
            <ListItem item={items[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Accessibility

### WCAG 2.1 AA Checklist

- [ ] All images have meaningful alt text
- [ ] Color contrast ratio ≥ 4.5:1 for normal text
- [ ] Focus indicators visible on all interactive elements
- [ ] Keyboard navigation works for all functionality
- [ ] Form inputs have associated labels
- [ ] Error messages are announced to screen readers
- [ ] Skip links provided for main content
- [ ] Headings follow logical hierarchy (h1 → h2 → h3)

### Accessible Form Pattern

```tsx
function AccessibleForm() {
  const [error, setError] = useState<string | null>(null);

  return (
    <form aria-labelledby="form-title">
      <h2 id="form-title">Create Account</h2>

      <div role="group" aria-labelledby="email-label">
        <label id="email-label" htmlFor="email">
          Email Address <span aria-hidden="true">*</span>
        </label>
        <input
          id="email"
          type="email"
          aria-required="true"
          aria-invalid={!!error}
          aria-describedby={error ? 'email-error' : 'email-hint'}
        />
        <p id="email-hint" className="hint">
          We'll never share your email.
        </p>
        {error && (
          <p id="email-error" role="alert" className="error">
            {error}
          </p>
        )}
      </div>

      <button type="submit">
        Create Account
      </button>
    </form>
  );
}
```

---

## Testing Strategies

### Testing Pyramid

```
        /‾‾‾‾‾‾‾‾‾\
       /   E2E     \     ← Few, slow, high confidence
      /‾‾‾‾‾‾‾‾‾‾‾‾‾\
     /  Integration  \   ← Some, medium speed
    /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
   /      Unit         \ ← Many, fast, isolated
  /_____________________\
```

### Component Testing with Vitest + Testing Library

```tsx
import { render, screen, userEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SearchBar } from './SearchBar';

describe('SearchBar', () => {
  it('calls onSearch when form is submitted', async () => {
    const onSearch = vi.fn();
    const user = userEvent.setup();

    render(<SearchBar onSearch={onSearch} />);

    await user.type(screen.getByRole('searchbox'), 'react hooks');
    await user.click(screen.getByRole('button', { name: /search/i }));

    expect(onSearch).toHaveBeenCalledWith('react hooks');
  });

  it('shows suggestions when typing', async () => {
    const user = userEvent.setup();

    render(<SearchBar suggestions={['react', 'redux', 'router']} />);

    await user.type(screen.getByRole('searchbox'), 're');

    expect(screen.getByRole('listbox')).toBeInTheDocument();
    expect(screen.getAllByRole('option')).toHaveLength(2);
  });
});
```

---

## TypeScript Best Practices

### Discriminated Unions for State

```tsx
type LoadingState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function DataDisplay<T>({ state }: { state: LoadingState<T> }) {
  switch (state.status) {
    case 'idle':
      return <p>Click to load data</p>;
    case 'loading':
      return <Spinner />;
    case 'success':
      return <DataView data={state.data} />; // TypeScript knows data exists
    case 'error':
      return <ErrorMessage error={state.error} />; // TypeScript knows error exists
  }
}
```

### Generic Component Patterns

```tsx
interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  getRowKey: (item: T) => string;
  onRowClick?: (item: T) => void;
}

function Table<T>({ data, columns, getRowKey, onRowClick }: TableProps<T>) {
  return (
    <table>
      <thead>
        <tr>
          {columns.map(col => (
            <th key={col.key}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map(item => (
          <tr key={getRowKey(item)} onClick={() => onRowClick?.(item)}>
            {columns.map(col => (
              <td key={col.key}>{col.render(item)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

## Resources

- [React Documentation](https://react.dev)
- [TanStack Query](https://tanstack.com/query)
- [Vitest](https://vitest.dev)
- [Testing Library](https://testing-library.com)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [web.dev Performance](https://web.dev/performance)

---

*Last Updated: 2025-01-01*
*BI Analyst Plugin - Frontend Skill*
