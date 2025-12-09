/**
 * themeManager.ts - App Theme and Color Configuration
 * 
 * This file defines all the colors used throughout the app.
 * 
 * Brand Colors:
 * - Blue: Primary color for main actions and headers
 * - Green: Success actions, positive indicators
 * - Orange: Warnings, supplements, secondary actions
 * 
 * Color Numbers (50, 600, 700):
 * - 50: Very light shade (for backgrounds)
 * - 600: Main color (for buttons, icons)
 * - 700: Darker shade (for text, borders)
 * 
 * Usage: Import { brand } from this file and use brand.blue[600] for colors
 */

import { MD3LightTheme, MD3DarkTheme } from "react-native-paper";
import AsyncStorage from "@react-native-async-storage/async-storage";

// Brand color palette - organized by color family
export const brand = {
  blue:   { 50:"#EFF6FF", 600:"#2563EB", 700:"#1D4ED8" },
  green:  { 50:"#ECFDF5", 600:"#16A34A", 700:"#15803D" },
  orange: { 50:"#FFF7ED", 600:"#D97706", 700:"#B45309" },
};

// Storage key for dark mode preference
const DARK_MODE_KEY = "@fitness_app_dark_mode";

/**
 * Saves dark mode preference to device storage
 * @param isDark - Whether dark mode is enabled
 */
export const saveDarkModePreference = async (isDark: boolean) => {
  try {
    await AsyncStorage.setItem(DARK_MODE_KEY, JSON.stringify(isDark));
  } catch (error) {
    console.error("Error saving dark mode preference:", error);
  }
};

/**
 * Loads dark mode preference from device storage
 * @returns Promise<boolean> - Whether dark mode is enabled
 */
export const loadDarkModePreference = async (): Promise<boolean> => {
  try {
    const value = await AsyncStorage.getItem(DARK_MODE_KEY);
    return value ? JSON.parse(value) : false;
  } catch (error) {
    console.error("Error loading dark mode preference:", error);
    return false;
  }
};

/**
 * Creates the app theme using React Native Paper's Material Design 3 theme
 * Supports both light and dark modes
 * 
 * @param isDark - Whether to use dark theme (default: false)
 * @returns Theme object for React Native Paper
 */
export const createTheme = (isDark: boolean = false) => {
  const baseTheme = isDark ? MD3DarkTheme : MD3LightTheme;
  
  return {
    ...baseTheme,
    colors: {
      ...baseTheme.colors,
      primary: brand.blue[600],      // Main app color
      secondary: brand.green[600],   // Secondary actions
      tertiary: brand.orange[600],  // Tertiary actions
      background: isDark ? "#121212" : "#FFFFFF",         // Main background color
      surface: isDark ? "#1E1E1E" : "#F9FAFB",            // Card/surface background
      surfaceVariant: isDark ? "#2C2C2C" : "#F3F4F6",     // Variant surface color
      text: isDark ? "#FFFFFF" : "#111827",               // Main text color
      onSurface: isDark ? "#FFFFFF" : "#111827",          // Text on surfaces
      onBackground: isDark ? "#FFFFFF" : "#111827",       // Text on background
      onSurfaceVariant: isDark ? "#E5E7EB" : "#4B5563",   // Text on variant surfaces
      outline: isDark ? "#4B5563" : "#D1D5DB",            // Outline/border color
      outlineVariant: isDark ? "#374151" : "#E5E7EB",     // Variant outline color
      // Ensure all text colors work in dark mode
      error: isDark ? "#EF4444" : "#DC2626",              // Error color
      errorContainer: isDark ? "#7F1D1D" : "#FEE2E2",     // Error container
      onError: "#FFFFFF",                                   // Text on error
      onErrorContainer: isDark ? "#FEE2E2" : "#7F1D1D",   // Text on error container
    },
  };
};
