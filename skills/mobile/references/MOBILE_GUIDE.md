# Mobile Development Guide

> BI Analyst Plugin - Mobile Skill Reference
> Version: 1.0.0

## Overview

Comprehensive guide covering mobile development best practices for React Native, Flutter, iOS, and Android platforms with focus on performance, security, and user experience.

## Table of Contents

1. [Platform Selection](#platform-selection)
2. [React Native Patterns](#react-native-patterns)
3. [Flutter Patterns](#flutter-patterns)
4. [Native iOS/Android](#native-iosandroid)
5. [Performance Optimization](#performance-optimization)
6. [Mobile Security](#mobile-security)

---

## Platform Selection

### Decision Matrix

| Factor | React Native | Flutter | Native |
|--------|--------------|---------|--------|
| Performance | Good | Excellent | Best |
| Dev Speed | Fast | Fast | Slower |
| UI Fidelity | Good | Excellent | Perfect |
| Team Skills | JavaScript | Dart | Swift/Kotlin |
| Hot Reload | Yes | Yes | Limited |
| Code Sharing | ~90% | ~95% | 0% |
| App Size | Medium | Larger | Smallest |

### When to Choose Each

```
React Native:
├── Existing JavaScript/React team
├── Need to move fast
├── Moderate performance requirements
└── Web + Mobile code sharing

Flutter:
├── Beautiful custom UI needed
├── High performance required
├── New team without legacy
└── Consistent cross-platform UX

Native:
├── Maximum performance critical
├── Deep platform integration
├── AR/VR/ML features
└── Long-term maintainability priority
```

---

## React Native Patterns

### Component Architecture

```typescript
// src/components/Button/Button.tsx
import React, { memo } from 'react';
import { Pressable, Text, StyleSheet, ActivityIndicator } from 'react-native';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  loading?: boolean;
  disabled?: boolean;
  accessibilityLabel?: string;
}

export const Button = memo<ButtonProps>(({
  title,
  onPress,
  variant = 'primary',
  loading = false,
  disabled = false,
  accessibilityLabel,
}) => {
  const isDisabled = disabled || loading;

  return (
    <Pressable
      style={({ pressed }) => [
        styles.button,
        styles[variant],
        pressed && styles.pressed,
        isDisabled && styles.disabled,
      ]}
      onPress={onPress}
      disabled={isDisabled}
      accessible
      accessibilityLabel={accessibilityLabel || title}
      accessibilityRole="button"
      accessibilityState={{ disabled: isDisabled }}
    >
      {loading ? (
        <ActivityIndicator color="#ffffff" />
      ) : (
        <Text style={[styles.text, styles[`${variant}Text`]]}>
          {title}
        </Text>
      )}
    </Pressable>
  );
});

const styles = StyleSheet.create({
  button: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48, // Accessibility: minimum touch target
  },
  primary: {
    backgroundColor: '#007AFF',
  },
  secondary: {
    backgroundColor: '#5856D6',
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  pressed: {
    opacity: 0.8,
  },
  disabled: {
    opacity: 0.5,
  },
  text: {
    fontSize: 16,
    fontWeight: '600',
  },
  primaryText: {
    color: '#ffffff',
  },
  secondaryText: {
    color: '#ffffff',
  },
  outlineText: {
    color: '#007AFF',
  },
});
```

### State Management with Zustand

```typescript
// src/store/authStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const response = await api.login(email, password);
          set({
            user: response.user,
            token: response.token,
            isAuthenticated: true,
          });
        } finally {
          set({ isLoading: false });
        }
      },

      logout: async () => {
        await api.logout();
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      refreshToken: async () => {
        const token = get().token;
        if (!token) return;

        try {
          const response = await api.refreshToken(token);
          set({ token: response.token });
        } catch {
          await get().logout();
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

### Navigation Pattern

```typescript
// src/navigation/RootNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import { useAuthStore } from '@/store/authStore';
import { AuthNavigator } from './AuthNavigator';
import { HomeScreen } from '@/screens/Home';
import { ProfileScreen } from '@/screens/Profile';
import { SettingsScreen } from '@/screens/Settings';

export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Profile: { userId: string };
  Settings: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#8E8E93',
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarIcon: ({ color }) => <HomeIcon color={color} />,
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        initialParams={{ userId: 'me' }}
      />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

export function RootNavigator() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainTabs} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

---

## Flutter Patterns

### Widget Architecture

```dart
// lib/features/auth/presentation/widgets/login_form.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class LoginForm extends ConsumerStatefulWidget {
  const LoginForm({super.key});

  @override
  ConsumerState<LoginForm> createState() => _LoginFormState();
}

class _LoginFormState extends ConsumerState<LoginForm> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      await ref.read(authControllerProvider.notifier).login(
        email: _emailController.text,
        password: _passwordController.text,
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString())),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(
              labelText: 'Email',
              prefixIcon: Icon(Icons.email),
            ),
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.next,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your email';
              }
              if (!value.contains('@')) {
                return 'Please enter a valid email';
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _passwordController,
            decoration: const InputDecoration(
              labelText: 'Password',
              prefixIcon: Icon(Icons.lock),
            ),
            obscureText: true,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => _handleSubmit(),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your password';
              }
              if (value.length < 8) {
                return 'Password must be at least 8 characters';
              }
              return null;
            },
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _isLoading ? null : _handleSubmit,
            child: _isLoading
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Login'),
          ),
        ],
      ),
    );
  }
}
```

### Riverpod State Management

```dart
// lib/features/auth/application/auth_controller.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'auth_controller.freezed.dart';

@freezed
class AuthState with _$AuthState {
  const factory AuthState.initial() = _Initial;
  const factory AuthState.loading() = _Loading;
  const factory AuthState.authenticated(User user) = _Authenticated;
  const factory AuthState.unauthenticated() = _Unauthenticated;
  const factory AuthState.error(String message) = _Error;
}

final authControllerProvider =
    StateNotifierProvider<AuthController, AuthState>((ref) {
  return AuthController(ref.watch(authRepositoryProvider));
});

class AuthController extends StateNotifier<AuthState> {
  final AuthRepository _repository;

  AuthController(this._repository) : super(const AuthState.initial());

  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = const AuthState.loading();

    final result = await _repository.login(email: email, password: password);

    state = result.fold(
      (failure) => AuthState.error(failure.message),
      (user) => AuthState.authenticated(user),
    );
  }

  Future<void> logout() async {
    await _repository.logout();
    state = const AuthState.unauthenticated();
  }
}
```

---

## Performance Optimization

### React Native Performance

```typescript
// 1. Use FlatList for long lists
import { FlatList } from 'react-native';

function UserList({ users }: { users: User[] }) {
  return (
    <FlatList
      data={users}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <UserCard user={item} />}
      // Performance optimizations
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={5}
      initialNumToRender={10}
      // Optimization for static content
      getItemLayout={(_, index) => ({
        length: ITEM_HEIGHT,
        offset: ITEM_HEIGHT * index,
        index,
      })}
    />
  );
}

// 2. Memoize expensive components
const UserCard = memo(({ user }: { user: User }) => {
  return (
    <View style={styles.card}>
      <Image source={{ uri: user.avatar }} style={styles.avatar} />
      <Text>{user.name}</Text>
    </View>
  );
});

// 3. Use useMemo for expensive calculations
function Analytics({ data }: { data: DataPoint[] }) {
  const processedData = useMemo(() => {
    return data.map(point => ({
      ...point,
      normalized: point.value / Math.max(...data.map(d => d.value)),
    }));
  }, [data]);

  return <Chart data={processedData} />;
}

// 4. Optimize images
import FastImage from 'react-native-fast-image';

<FastImage
  source={{ uri: imageUrl, priority: FastImage.priority.normal }}
  style={styles.image}
  resizeMode={FastImage.resizeMode.cover}
/>
```

### Flutter Performance

```dart
// 1. Use const constructors
const SizedBox(height: 16),
const Padding(padding: EdgeInsets.all(8.0)),

// 2. ListView.builder for long lists
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ItemCard(item: items[index]);
  },
  // Cache extent for smoother scrolling
  cacheExtent: 200,
)

// 3. Cached network images
CachedNetworkImage(
  imageUrl: user.avatarUrl,
  placeholder: (context, url) => const CircularProgressIndicator(),
  errorWidget: (context, url, error) => const Icon(Icons.error),
)

// 4. Repaint boundaries for complex widgets
RepaintBoundary(
  child: ComplexAnimation(),
)
```

---

## Mobile Security

### Secure Storage

```typescript
// React Native - Keychain
import * as Keychain from 'react-native-keychain';

class SecureStorage {
  static async setToken(token: string): Promise<void> {
    await Keychain.setGenericPassword('auth', token, {
      accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED,
      securityLevel: Keychain.SECURITY_LEVEL.SECURE_HARDWARE,
    });
  }

  static async getToken(): Promise<string | null> {
    const credentials = await Keychain.getGenericPassword();
    return credentials ? credentials.password : null;
  }

  static async clearToken(): Promise<void> {
    await Keychain.resetGenericPassword();
  }
}
```

### SSL Pinning

```typescript
// React Native SSL Pinning
import { fetch } from 'react-native-ssl-pinning';

const response = await fetch(url, {
  method: 'GET',
  sslPinning: {
    certs: ['certificate-sha256-hash'],
  },
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Security Checklist

- [ ] Use secure storage for sensitive data
- [ ] Implement SSL pinning
- [ ] Enable root/jailbreak detection
- [ ] Obfuscate production builds
- [ ] Validate all user inputs
- [ ] Implement biometric authentication
- [ ] Use certificate transparency
- [ ] Encrypt local databases

---

## Resources

- [React Native Documentation](https://reactnative.dev)
- [Flutter Documentation](https://flutter.dev/docs)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
- [Material Design 3](https://m3.material.io)
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security)

---

*Last Updated: 2025-01-01*
*BI Analyst Plugin - Mobile Skill*
