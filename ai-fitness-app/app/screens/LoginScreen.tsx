/**
 * LoginScreen.tsx - User Login Screen
 */

import React, { useState } from "react";
import {
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  View,
  TouchableOpacity,
  Alert,
  StyleSheet,
} from "react-native";
import {
  TextInput,
  Button,
  Text,
  Checkbox,
  useTheme,
  Surface,
} from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import { BASE_URL } from "../config";

export default function LoginScreen({ navigation }: any) {
  const theme = useTheme();

  const [firstName, setFirstName] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showError, setShowError] = useState(false);

  const valid = firstName.trim().length > 0 && password.trim().length >= 6;

  const handleLogin = async () => {
    if (!valid) {
      setShowError(true);
      return;
    }

    try {
      setLoading(true);

      const res = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          first_name: firstName,
          password: password,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        Alert.alert("✅ Login Successful", `Welcome back ${data.first_name}!`);

        navigation.reset({
          index: 0,
          routes: [
            {
              name: "Tabs",
              params: {
                username: data.first_name,
                firstName: data.first_name,
                role: data.role,
                user_id: data.user_id,
                token: data.access_token,
              },
            },
          ],
        });
      } else {
        Alert.alert(
          "❌ Login Failed",
          data.detail || data.message || "Invalid credentials"
        );
      }
    } catch (err) {
      console.error("Login error:", err);
      Alert.alert("Connection Error", "Cannot connect to the server 😢");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenScaffold>
      <KeyboardAvoidingView
        style={[
          styles.root,
          { backgroundColor: theme.colors.background || "#F9FAFB" },
        ]}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContainer}
          keyboardShouldPersistTaps="handled"
        >
          <Surface style={styles.card} elevation={2}>
            {/* Header */}
            <View style={styles.header}>
              <Text style={styles.title}>Welcome Back</Text>
              <Text style={styles.subtitle}>
                Sign in to continue your fitness journey.
              </Text>
            </View>

            {/* Username/First Name Input */}
            <TextInput
              mode="outlined"
              label="Username"
              placeholder="Enter your username"
              value={firstName}
              onChangeText={(t) => {
                setFirstName(t);
                setShowError(false);
              }}
              left={<TextInput.Icon icon="account" />}
              style={styles.input}
              disabled={loading}
              autoCapitalize="none"
              autoCorrect={false}
            />

            {/* Password Input */}
            <TextInput
              mode="outlined"
              label="Password"
              placeholder="Enter your password"
              value={password}
              onChangeText={(t) => {
                setPassword(t);
                setShowError(false);
              }}
              secureTextEntry={!showPassword}
              left={<TextInput.Icon icon="lock" />}
              right={
                <TextInput.Icon
                  icon={showPassword ? "eye-off" : "eye"}
                  onPress={() => setShowPassword(!showPassword)}
                />
              }
              style={styles.input}
              disabled={loading}
              autoCapitalize="none"
              autoCorrect={false}
            />

            {/* Error Message */}
            {showError && (
              <View style={styles.errorBox}>
                <Text style={styles.errorText}>
                  Please enter a valid username and password (minimum 6
                  characters).
                </Text>
              </View>
            )}

            {/* Remember Me */}
            <View style={styles.rememberRow}>
              <Checkbox
                status={rememberMe ? "checked" : "unchecked"}
                onPress={() => setRememberMe(!rememberMe)}
                color={brand.blue[600]}
              />
              <Text
                onPress={() => setRememberMe(!rememberMe)}
                style={styles.rememberLabel}
              >
                Remember me
              </Text>
            </View>

            {/* Login Button */}
            <Button
              mode="contained"
              buttonColor={brand.green[600]} // نفس لون الأزرار الرئيسية
              textColor="#fff"
              style={styles.mainButton}
              onPress={handleLogin}
              loading={loading}
              disabled={loading || !valid}
              labelStyle={styles.mainButtonLabel}
            >
              Sign In
            </Button>

            {/* Footer: Go to Signup */}
            <View style={styles.footerRow}>
              <Text>Don’t have an account? </Text>
              <TouchableOpacity onPress={() => navigation.navigate("Signup")}>
                <Text style={{ color: brand.green[700], fontWeight: "600" }}>
                  Create one
                </Text>
              </TouchableOpacity>
            </View>
          </Surface>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenScaffold>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  scrollContainer: {
    paddingHorizontal: 24,
    paddingVertical: 24,
    flexGrow: 1,
    justifyContent: "center",
  },
  card: {
    borderRadius: 24,
    paddingHorizontal: 18,
    paddingVertical: 22,
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#E5E7EB",
  },
  header: {
    alignItems: "center",
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: "800",
    marginBottom: 4,
    textAlign: "center",
    color: brand.blue[700],
    letterSpacing: 0.5,
  },
  subtitle: {
    fontSize: 14,
    color: "#6B7280",
    textAlign: "center",
    marginTop: 4,
  },
  input: {
    marginBottom: 12,
    backgroundColor: "#FFFFFF",
  },
  errorBox: {
    backgroundColor: "#FEE2E2",
    padding: 10,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: "#DC2626",
  },
  errorText: {
    color: "#DC2626",
    fontSize: 13,
  },
  rememberRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
  },
  rememberLabel: {
    color: "#4B5563",
    fontSize: 14,
  },
  mainButton: {
    borderRadius: 999,
    marginBottom: 16,
    paddingVertical: 4,
  },
  mainButtonLabel: {
    fontSize: 16,
    fontWeight: "600",
    letterSpacing: 0.5,
  },
  footerRow: {
    flexDirection: "row",
    justifyContent: "center",
  },
});
