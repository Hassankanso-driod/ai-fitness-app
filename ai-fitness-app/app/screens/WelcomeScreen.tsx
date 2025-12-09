import React from "react";
import { View, Image, StyleSheet } from "react-native";
import { Text, Button, useTheme, Surface } from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";

export default function WelcomeScreen({ navigation }: any) {
  const theme = useTheme();

  return (
    <ScreenScaffold>
      <View
        style={[
          styles.root,
          { backgroundColor: theme.colors.background || "#F9FAFB" },
        ]}
      >
        <Surface style={styles.card} elevation={2}>
          {/* 🧠 App Logo or Illustration */}
          <Image
            source={{
              uri: "https://cdn-icons-png.flaticon.com/512/1048/1048949.png",
            }}
            style={styles.image}
            resizeMode="contain"
          />

          {/* 💪 Title */}
          <Text style={styles.title}>AI Fitness Coach 💪</Text>

          {/* ✨ Subtitle */}
          <Text style={styles.subtitle}>
            Your smart personal trainer to guide you step-by-step to a healthier
            lifestyle.
          </Text>

          {/* 🚀 Buttons */}
          <View style={styles.buttonContainer}>
            <Button
              mode="contained"
              buttonColor={brand.green[600]}
              textColor="#fff"
              onPress={() => navigation.navigate("Login")}
              style={styles.button}
              labelStyle={styles.buttonLabel}
            >
              Log In
            </Button>

            <Button
              mode="outlined"
              textColor={brand.green[700]}
              onPress={() => navigation.navigate("Signup")}
              style={[styles.button, styles.outlinedButton]}
              labelStyle={styles.buttonLabel}
            >
              Create Account
            </Button>
          </View>
        </Surface>
      </View>
    </ScreenScaffold>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    paddingHorizontal: 24,
    justifyContent: "center",
  },
  card: {
    borderRadius: 24,
    paddingHorizontal: 20,
    paddingVertical: 28,
    backgroundColor: "#FFFFFF",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#E5E7EB",
  },
  image: {
    width: "80%",
    height: 200,
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: "800",
    textAlign: "center",
    color: brand.blue[700],
    marginBottom: 8,
    letterSpacing: 0.3,
  },
  subtitle: {
    fontSize: 14,
    textAlign: "center",
    color: "#6B7280",
    marginBottom: 24,
    lineHeight: 22,
  },
  buttonContainer: {
    width: "100%",
    alignItems: "center",
    marginTop: 4,
  },
  button: {
    width: "100%",
    marginBottom: 12,
    borderRadius: 999,
  },
  outlinedButton: {
    borderWidth: 2,
    borderColor: brand.green[600],
  },
  buttonLabel: {
    fontSize: 16,
    fontWeight: "600",
  },
});
