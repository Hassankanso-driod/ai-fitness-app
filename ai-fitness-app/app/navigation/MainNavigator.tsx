// navigation/MainNavigator.tsx
import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { brand } from "../utils/themeManager";

// Screens
import HomeScreen from "../screens/HomeScreen";
import SupplementsScreen from "../screens/SupplementsScreen";
import WorkoutTrackingScreen from "../screens/WorkoutTrackingScreen";
import MealPlanningScreen from "../screens/MealPlanningScreen";
import ProfileScreen from "../screens/ProfileScreen";

const Tab = createBottomTabNavigator();

export default function MainNavigator({ user }: any) {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: brand.green[600],
        tabBarStyle: { height: 65, paddingBottom: 12 },
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        initialParams={user}
        options={{
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="home" color={color} size={26} />
          ),
        }}
      />

      <Tab.Screen
        name="Supplements"
        component={SupplementsScreen}
        options={{
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="pill" color={color} size={26} />
          ),
        }}
      />

      <Tab.Screen
        name="Workout Tracking"
        component={WorkoutTrackingScreen}
        options={{
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="dumbbell" color={color} size={26} />
          ),
        }}
      />

      <Tab.Screen
        name="Meal Planning"
        component={MealPlanningScreen}
        options={{
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="food-apple" color={color} size={26} />
          ),
        }}
      />

      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        initialParams={user}
        options={{
          tabBarIcon: ({ color }) => (
            <MaterialCommunityIcons name="account" color={color} size={26} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}
