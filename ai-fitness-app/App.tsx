/**
 * App.tsx - Main Application Entry Point
 * 
 * This is the root component of the AI Fitness App. It sets up:
 * - Navigation (Stack Navigator for screens, Tab Navigator for bottom tabs)
 * - Theme (using React Native Paper)
 * - Notifications (requesting permissions)
 * - All screen routes and navigation structure
 * 
 * For beginners: This file connects all your screens together and defines
 * how users navigate between different parts of the app.
 */

import "react-native-gesture-handler";
import * as React from "react";
import { StatusBar, Alert } from "react-native";
import { NavigationContainer, RouteProp } from "@react-navigation/native";
import { createNativeStackNavigator, NativeStackScreenProps } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import * as Notifications from "expo-notifications";
import { Provider as PaperProvider } from "react-native-paper";
import { MaterialCommunityIcons } from "@expo/vector-icons";

// 🧩 Import all screen components
import WelcomeScreen from "./app/screens/WelcomeScreen";
import LoginScreen from "./app/screens/LoginScreen";
import SignupScreen from "./app/screens/SignupScreen";
import HomeScreen from "./app/screens/HomeScreen";
import WorkoutsScreen from "./app/screens/WorkoutsScreen";
import RemindersScreen from "./app/screens/RemindersScreen";
import SupplementsScreen from "./app/screens/SupplementsScreen";
import AddSupplementScreen from "./app/screens/AddSupplementScreen";
import EditSupplementScreen from "./app/screens/EditSupplementScreen";
import SupplementDetailsScreen from "./app/screens/SupplementDetailsScreen";
import ManagementScreen from "./app/screens/ManagementScreen";
import ProfileScreen from "./app/screens/ProfileScreen";
import WorkoutTrackingScreen from "./app/screens/WorkoutTrackingScreen";
import MealPlanningScreen from "./app/screens/MealPlanningScreen";

// 🧠 Theme - Import colors and theme configuration
import { brand, createTheme, loadDarkModePreference, saveDarkModePreference } from "./app/utils/themeManager";

// Create a context to share dark mode state across the app
export const DarkModeContext = React.createContext<{
  isDark: boolean;
  toggleDarkMode: () => void;
}>({
  isDark: false,
  toggleDarkMode: () => {},
});


// ---------- TypeScript Type Definitions ----------
// These types help TypeScript understand what data each screen expects
// This prevents errors and helps with autocomplete in your code editor
export type RootStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Signup: undefined;
  Tabs: { username?: string; role?: string; user_id?: number; firstName?: string; token?: string } | undefined;
  Reminders: undefined;
  Supplements: { username?: string; role?: string; firstName?: string } | undefined;
  AddSupplement: undefined;
  EditSupplement: { supplement: any } | undefined;
  SupplementDetails: { item: any } | undefined;
  Management: { firstName?: string; token?: string; userId?: number } | undefined;
  Profile: { userId?: number; firstName?: string; token?: string } | undefined;
  WorkoutTracking: { userId?: number; token?: string } | undefined;
  MealPlanning: { userId?: number; token?: string } | undefined;
};

export type TabsParamList = {
  Home: { username?: string; role?: string; user_id?: number; firstName?: string; token?: string } | undefined;
  Workouts: undefined;
  RemindersTab: undefined;
  Profile: { userId?: number; firstName?: string; token?: string } | undefined;
};

// ---------- Navigator Setup ----------
// Create navigators: Stack for full-screen navigation, Tabs for bottom tab bar
const Stack = createNativeStackNavigator<RootStackParamList>();
const Tabs = createBottomTabNavigator<TabsParamList>();

// ---------- Tab Icons Configuration ----------
// Define which icon to show for each tab in the bottom navigation
const TAB_ICON: Record<keyof TabsParamList, React.ComponentProps<typeof MaterialCommunityIcons>["name"]> = {
  Home: "home-variant",
  Workouts: "dumbbell",
  RemindersTab: "bell-outline",
  Profile: "account-circle",
};

// ---------- Main App Component ----------
/**
 * This is the main App component that renders everything
 * It's the entry point that React Native calls when the app starts
 */
export default function App() {
  // Dark mode state - controls whether app uses light or dark theme
  const [isDark, setIsDark] = React.useState(false);

  // Load dark mode preference from storage when app starts
  React.useEffect(() => {
    loadDarkModePreference().then((saved) => setIsDark(saved));
  }, []);

  // Function to toggle dark mode and save preference
  const toggleDarkMode = React.useCallback(async () => {
    const newValue = !isDark;
    setIsDark(newValue);
    await saveDarkModePreference(newValue);
  }, [isDark]);

  // Create the theme (colors, styles) for the entire app based on dark mode
  const theme = createTheme(isDark);

  // 🔔 Request notification permissions when app starts
  // This allows the app to send reminders for workouts, meals, water, etc.
  React.useEffect(() => {
    (async () => {
      try {
        const { status } = await Notifications.requestPermissionsAsync();
        if (status !== "granted") {
          Alert.alert(
            "Permission Required",
            "Please enable notifications to receive reminders 📲"
          );
        } else {
          console.log("✅ Notifications permission granted");
        }
      } catch (e: any) {
        console.warn("Notification permission error:", e?.message);
      }
    })();

    const sub1 = Notifications.addNotificationReceivedListener(() => {});
    const sub2 = Notifications.addNotificationResponseReceivedListener(() => {});
    return () => {
      sub1.remove();
      sub2.remove();
    };
  }, []);

  return (
    <DarkModeContext.Provider value={{ isDark, toggleDarkMode }}>
      <PaperProvider theme={theme}>
        <StatusBar barStyle={isDark ? "light-content" : "dark-content"} />
        <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          {/* ---------- Auth Screens ---------- */}
          <Stack.Screen name="Welcome" component={WelcomeScreen} />
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Signup" component={SignupScreen} />

          {/* ---------- Main App Tabs ---------- */}
          <Stack.Screen name="Tabs" component={TabsShell} />

          {/* ---------- Standalone Screens ---------- */}
          <Stack.Screen name="Reminders" component={RemindersScreen} />
          <Stack.Screen
            name="Supplements"
            component={SupplementsScreen}
            options={{
              headerShown: true,
              title: "Supplements Store 💪",
              headerStyle: { backgroundColor: brand.orange[50] },
            }}
          />
          <Stack.Screen
            name="AddSupplement"
            component={AddSupplementScreen}
            options={{
              headerShown: true,
              title: "Add New Supplement",
              headerStyle: { backgroundColor: brand.green[50] },
            }}
          />
          <Stack.Screen
            name="EditSupplement"
            component={EditSupplementScreen}
            options={{
              headerShown: true,
              title: "Edit Supplement",
              headerStyle: { backgroundColor: brand.blue[50] },
            }}
          />
          <Stack.Screen
            name="SupplementDetails"
            component={SupplementDetailsScreen}
            options={{
              headerShown: true,
              title: "Supplement Details",
              headerStyle: { backgroundColor: brand.orange[50] },
            }}
          />
          <Stack.Screen
            name="Management"
            component={ManagementScreen}
            options={{
              headerShown: true,
              title: "Admin Management",
              headerStyle: { backgroundColor: brand.blue[50] },
            }}
          />
          <Stack.Screen
            name="Profile"
            component={ProfileScreen}
            options={{
              headerShown: true,
              title: "Profile",
              headerStyle: { backgroundColor: brand.blue[50] },
            }}
          />
          <Stack.Screen
            name="WorkoutTracking"
            component={WorkoutTrackingScreen}
            options={{
              headerShown: true,
              title: "Workout Tracking",
              headerStyle: { backgroundColor: brand.green[50] },
            }}
          />
          <Stack.Screen
            name="MealPlanning"
            component={MealPlanningScreen}
            options={{
              headerShown: true,
              title: "Meal Planning",
              headerStyle: { backgroundColor: brand.orange[50] },
            }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </PaperProvider>
    </DarkModeContext.Provider>
  );
}

// ---------- Tabs Shell Component ----------
/**
 * TabsShell creates the bottom tab navigation
 * This shows the Home, Workouts, Reminders, and Profile tabs at the bottom
 * of the screen when users are logged in
 */
type TabsShellProps = NativeStackScreenProps<RootStackParamList, "Tabs">;

function TabsShell({ route }: TabsShellProps) {
  // Get user information passed from login (name, role, token, etc.)
  const userParams = route?.params ?? {};

  return (
    <Tabs.Navigator
      initialRouteName="Home"
      screenOptions={({ route }: { route: RouteProp<TabsParamList> }) => ({
        headerShown: false,
        tabBarActiveTintColor: brand.blue[600],
        tabBarLabelStyle: { fontSize: 12 },
        tabBarIcon: ({ color, size }) => (
          <MaterialCommunityIcons
            name={TAB_ICON[route.name]}
            color={color}
            size={size}
          />
        ),
      })}
    >
      <Tabs.Screen
        name="Home"
        component={HomeScreen}
        initialParams={userParams}
        options={{ title: "Home" }}
      />
      <Tabs.Screen
        name="Workouts"
        component={WorkoutsScreen}
        options={{ title: "Workouts" }}
      />
      <Tabs.Screen
        name="RemindersTab"
        component={RemindersScreen}
        options={{ title: "Reminders" }}
      />
      <Tabs.Screen
        name="Profile"
        component={ProfileScreen}
        initialParams={userParams}
        options={{ title: "Profile" }}
      />
    </Tabs.Navigator>
  );
}
