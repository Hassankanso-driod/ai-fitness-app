// navigation/AdminNavigator.tsx
import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import ManagementScreen from "../screens/ManagementScreen";
import SupplementsScreen from "../screens/SupplementsScreen";
import AddSupplementScreen from "../screens/AddSupplementScreen";
import EditSupplementScreen from "../screens/EditSupplementScreen";
import ProfileScreen from "../screens/ProfileScreen";

const Stack = createNativeStackNavigator();

export default function AdminNavigator({ user }: any) {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen
        name="Management"
        component={ManagementScreen}
        initialParams={user}
      />

      <Stack.Screen name="Supplements" component={SupplementsScreen} />

      <Stack.Screen name="AddSupplement" component={AddSupplementScreen} />

      <Stack.Screen name="EditSupplement" component={EditSupplementScreen} />

      <Stack.Screen name="AdminProfile" component={ProfileScreen} />
    </Stack.Navigator>
  );
}
