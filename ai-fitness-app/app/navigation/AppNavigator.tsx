// navigation/AppNavigator.tsx
import React from "react";
import AuthNavigator from "./AuthNavigator";
import MainNavigator from "./MainNavigator";
import AdminNavigator from "./AdminNavigator";

export default function AppNavigator({ user }: any) {
  if (!user) return <AuthNavigator />;

  if (user.role === "admin") {
    return <AdminNavigator user={user} />;
  }

  return <MainNavigator user={user} />;
}
