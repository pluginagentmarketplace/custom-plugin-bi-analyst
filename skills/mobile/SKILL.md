---
name: mobile-development
description: Build native iOS and Android apps, or cross-platform mobile applications with React Native and Flutter. Master mobile UI, platform APIs, performance optimization, and app deployment.
---

# Mobile Development Skill

## Quick Start

### iOS with Swift
```swift
import SwiftUI

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var count = 0

    var body: some View {
        VStack(spacing: 20) {
            Text("Counter: \(count)")
                .font(.largeTitle)
                .fontWeight(.bold)

            Button(action: { count += 1 }) {
                Text("Increment")
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }

            List {
                ForEach(0..<count, id: \.self) { index in
                    Text("Item \(index + 1)")
                }
            }
        }
        .padding()
    }
}
```

### Android with Kotlin
```kotlin
package com.example.myapp

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.compose.foundation.layout.*
import androidx.compose.material.Button
import androidx.compose.material.Text
import androidx.compose.runtime.*

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CounterApp()
        }
    }
}

@Composable
fun CounterApp() {
    var count by remember { mutableStateOf(0) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Counter: $count", fontSize = 24.sp)

        Button(onClick = { count++ }) {
            Text("Increment")
        }

        LazyColumn {
            items(count) { index ->
                Text("Item ${index + 1}")
            }
        }
    }
}
```

### React Native
```javascript
import React, { useState } from 'react';
import {
  View,
  Text,
  Button,
  FlatList,
  StyleSheet,
  SafeAreaView,
} from 'react-native';

export default function CounterApp() {
  const [count, setCount] = useState(0);

  const items = Array.from({ length: count }, (_, i) => ({
    id: `${i}`,
    title: `Item ${i + 1}`,
  }));

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Counter: {count}</Text>

      <Button
        title="Increment"
        onPress={() => setCount(count + 1)}
      />

      <FlatList
        data={items}
        renderItem={({ item }) => (
          <Text style={styles.item}>{item.title}</Text>
        )}
        keyExtractor={item => item.id}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  item: {
    paddingVertical: 10,
    fontSize: 16,
  },
});
```

### Flutter
```dart
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Counter App',
      home: const CounterPage(),
    );
  }
}

class CounterPage extends StatefulWidget {
  const CounterPage({Key? key}) : super(key: key);

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Counter App')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Count: $_count',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => setState(() => _count++),
              child: const Text('Increment'),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: _count,
                itemBuilder: (context, index) {
                  return ListTile(title: Text('Item ${index + 1}'));
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

## Mobile UI Patterns

### Responsive Design
```swift
// SwiftUI responsive layout
struct ResponsiveLayout: View {
    @Environment(\.horizontalSizeClass) var sizeClass

    var body: some View {
        if sizeClass == .compact {
            // Mobile layout
            VStack { /* ... */ }
        } else {
            // Tablet/landscape layout
            HStack { /* ... */ }
        }
    }
}
```

### Navigation
```swift
// SwiftUI navigation
NavigationView {
    VStack {
        NavigationLink("Go to Details", destination: DetailsView())
    }
    .navigationTitle("Home")
}

// React Native navigation
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Details" component={DetailsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## State Management

### iOS (Combine Framework)
```swift
import Combine

class UserViewModel: ObservableObject {
    @Published var user: User?
    @Published var isLoading = false
    @Published var error: Error?

    func fetchUser(id: Int) {
        isLoading = true
        // API call
        isLoading = false
    }
}

struct UserView: View {
    @StateObject var viewModel = UserViewModel()

    var body: some View {
        if viewModel.isLoading {
            ProgressView()
        } else if let user = viewModel.user {
            Text(user.name)
        }
    }
}
```

### Android (ViewModel & LiveData)
```kotlin
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun fetchUser(id: Int) {
        viewModelScope.launch {
            _user.value = userRepository.getUser(id)
        }
    }
}

class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val viewModel = ViewModelProvider(this).get(UserViewModel::class.java)
        viewModel.user.observe(this) { user ->
            // Update UI
        }
    }
}
```

### React Native & Flutter State
```javascript
// Redux for React Native
import { useSelector, useDispatch } from 'react-redux';

function UserComponent() {
  const user = useSelector(state => state.user);
  const dispatch = useDispatch();

  return <Text>{user.name}</Text>;
}
```

```dart
// Provider for Flutter
class UserProvider with ChangeNotifier {
  User? _user;

  User? get user => _user;

  Future<void> fetchUser(int id) async {
    _user = await userRepository.getUser(id);
    notifyListeners();
  }
}

class UserWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(userProvider);
    return Text(user?.name ?? 'Loading');
  }
}
```

## Networking

### iOS HTTP Requests
```swift
struct UserService {
    func fetchUser(id: Int) async throws -> User {
        let url = URL(string: "https://api.example.com/users/\(id)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(User.self, from: data)
    }
}
```

### Android Retrofit
```kotlin
interface UserService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Int): User
}

class UserRepository(private val userService: UserService) {
    suspend fun getUser(id: Int): User = userService.getUser(id)
}
```

### React Native & Axios
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.example.com',
});

export const userAPI = {
  getUser: (id) => api.get(`/users/${id}`),
  createUser: (data) => api.post('/users', data),
};

// Usage in component
useEffect(() => {
  userAPI.getUser(1).then(res => setUser(res.data));
}, []);
```

## Testing Mobile Apps

### iOS Testing
```swift
import XCTest

class CounterTests: XCTestCase {
    var sut: Counter!

    override func setUp() {
        super.setUp()
        sut = Counter()
    }

    func testIncrement() {
        sut.increment()
        XCTAssertEqual(sut.count, 1)
    }
}
```

### Android Testing
```kotlin
@RunWith(AndroidJUnit4::class)
class UserViewModelTest {
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        viewModel = UserViewModel()
    }

    @Test
    fun testFetchUser() {
        viewModel.fetchUser(1)
        assertEquals("John", viewModel.user.value?.name)
    }
}
```

## Performance Optimization

### Battery & Memory
- [ ] Reduce location service usage
- [ ] Optimize image sizes and compression
- [ ] Limit background processes
- [ ] Use lazy loading for lists
- [ ] Implement pagination
- [ ] Cache data locally
- [ ] Profile memory usage

### App Store Deployment
- [ ] Code signing setup
- [ ] Certificate management
- [ ] Build optimization
- [ ] Version management
- [ ] Release notes
- [ ] Beta testing (TestFlight/Firebase)
- [ ] App review guidelines

## Platform APIs

### iOS/Android Common APIs
```swift
// Location services
import CoreLocation
let manager = CLLocationManager()
manager.requestWhenInUseAuthorization()

// Camera access
import AVFoundation
// Request permission and access camera

// Push notifications
import UserNotifications
UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])
```

## Resources
- [Swift Official Documentation](https://www.swift.org/documentation/)
- [Android Developer Docs](https://developer.android.com/docs)
- [React Native Documentation](https://reactnative.dev)
- [Flutter Documentation](https://flutter.dev/docs)
