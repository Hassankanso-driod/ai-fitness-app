/**
 * ScreenScaffold.tsx - Reusable Screen Wrapper Component
 * 
 * This component provides a consistent header and layout for all screens.
 * It automatically adapts to dark mode using React Native Paper's theme.
 * 
 * Features:
 * - Back button (if navigation history exists)
 * - Screen title
 * - Logo mark
 * - Theme-aware styling (works with dark mode)
 */

import React from "react";
import { View } from "react-native";
import { Appbar, useTheme } from "react-native-paper";
import LogoMark from "./LogoMark";
import HeaderRing from "./HeaderRing";
import { brand } from "../utils/themeManager";
import { useNavigation } from "@react-navigation/native";

export default function ScreenScaffold({
  title,
  children,
  showHeaderRing,
  mode,
  onToggleTheme,
}: any) {
  const navigation = useNavigation();
  const canBack = navigation.canGoBack();
  const theme = useTheme(); // Get current theme (light/dark)

  return (
    <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
      <Appbar.Header mode="small" style={{ backgroundColor: theme.colors.surface }}>
        {canBack && (
          <Appbar.Action
            icon="arrow-left"
            onPress={() => navigation.goBack()}
            iconColor={theme.colors.onSurface}
          />
        )}
        <Appbar.Content
          title={title}
          titleStyle={{ color: theme.colors.onSurface }}
        />
        {showHeaderRing && <HeaderRing color={brand.orange[600]} />}
        {onToggleTheme && (
          <Appbar.Action
            icon={mode === "dark" ? "white-balance-sunny" : "weather-night"}
            onPress={onToggleTheme}
            iconColor={theme.colors.onSurface}
          />
        )}
        <LogoMark />
      </Appbar.Header>
      {children}
    </View>
  );
}
