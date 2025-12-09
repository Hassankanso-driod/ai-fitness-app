import React, { useState } from "react";
import {
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  View,
  Alert,
  StyleSheet,
} from "react-native";
import {
  TextInput,
  Button,
  Text,
  SegmentedButtons,
  RadioButton,
  useTheme,
  Surface,
} from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import { BASE_URL } from "../config";

type Goal = "lose" | "maintain" | "gain" | "stress";
type Sex = "male" | "female";

export default function SignupScreen({ navigation }: any) {
  const theme = useTheme();

  const [firstName, setFirstName] = useState("");
  const [sex, setSex] = useState<Sex>("male");
  const [age, setAge] = useState("");
  const [heightCm, setHeightCm] = useState("");
  const [weightKg, setWeightKg] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [goal, setGoal] = useState<Goal>("maintain");
  const [loading, setLoading] = useState(false);

  const valid =
    firstName &&
    age &&
    heightCm &&
    weightKg &&
    password.length >= 6 &&
    Number(age) > 10;

  const handleSignup = async () => {
    if (!valid) {
      Alert.alert("Incomplete Form", "Please fill all fields correctly.");
      return;
    }

    try {
      setLoading(true);

      const res = await fetch(`${BASE_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          first_name: firstName.trim(),
          sex: sex,
          age: Number(age),
          height_cm: Number(heightCm),
          weight_kg: Number(weightKg),
          password: password,
          goal: goal,
          role: "user",
        }),
      });

      const data = await res.json();

      if (res.ok) {
        Alert.alert(
          "🎉 Account Created",
          `Welcome ${firstName}! You can now log in.`,
          [
            {
              text: "Go to Login",
              onPress: () => navigation.navigate("Login"),
            },
          ]
        );
      } else {
        Alert.alert(
          "❌ Signup Failed",
          data.detail || data.message || "Please try again"
        );
      }
    } catch (err) {
      console.error("Signup error:", err);
      Alert.alert("Connection Error", "Cannot reach the backend 😢");
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
            <Text style={styles.title}>Create Account ✨</Text>
            <Text style={styles.subtitle}>
              Fill in your details to personalize your fitness journey.
            </Text>

            {/* First Name */}
            <TextInput
              mode="outlined"
              label="First Name"
              value={firstName}
              onChangeText={setFirstName}
              style={styles.input}
            />

            {/* Gender Selection */}
            <Text style={styles.sectionLabel}>Gender</Text>
            <SegmentedButtons
              value={sex}
              onValueChange={(v) => setSex(v as Sex)}
              buttons={[
                { value: "male", label: "Male", icon: "account" },
                { value: "female", label: "Female", icon: "account-outline" },
              ]}
              style={styles.segmented}
            />

            {/* Age */}
            <TextInput
              mode="outlined"
              label="Age"
              keyboardType="number-pad"
              value={age}
              onChangeText={setAge}
              style={styles.input}
            />

            {/* Height */}
            <TextInput
              mode="outlined"
              label="Height (cm)"
              keyboardType="decimal-pad"
              value={heightCm}
              onChangeText={setHeightCm}
              style={styles.input}
            />

            {/* Weight */}
            <TextInput
              mode="outlined"
              label="Weight (kg)"
              keyboardType="decimal-pad"
              value={weightKg}
              onChangeText={setWeightKg}
              style={styles.input}
            />

            {/* Password */}
            <TextInput
              mode="outlined"
              label="Password"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              left={<TextInput.Icon icon="lock" />}
              right={
                <TextInput.Icon
                  icon={showPassword ? "eye-off" : "eye"}
                  onPress={() => setShowPassword(!showPassword)}
                />
              }
              style={styles.input}
            />

            {/* Goal Selection */}
            <Text style={[styles.sectionLabel, { marginTop: 8 }]}>Goal</Text>
            <RadioButton.Group
              onValueChange={(v) => setGoal(v as Goal)}
              value={goal}
            >
              <View style={styles.radioRow}>
                <RadioButton.Item label="Lose" value="lose" />
                <RadioButton.Item label="Maintain" value="maintain" />
              </View>
              <View style={styles.radioRow}>
                <RadioButton.Item label="Gain" value="gain" />
                <RadioButton.Item label="Stress" value="stress" />
              </View>
            </RadioButton.Group>

            {/* Signup Button */}
            <Button
              mode="contained"
              buttonColor={brand.green[600]}
              textColor="#fff"
              disabled={!valid || loading}
              loading={loading}
              style={styles.mainButton}
              onPress={handleSignup}
              labelStyle={styles.mainButtonLabel}
            >
              Create Account
            </Button>

            {/* Already have an account */}
            <View style={styles.footerRow}>
              <Text>Already have an account? </Text>
              <Button
                onPress={() => navigation.navigate("Login")}
                compact
                textColor={brand.green[700]}
              >
                Log in
              </Button>
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
  title: {
    fontSize: 26,
    fontWeight: "800",
    textAlign: "center",
    color: brand.blue[700],
    marginBottom: 4,
  },
  subtitle: {
    color: "#6B7280",
    marginBottom: 16,
    textAlign: "center",
    fontSize: 14,
  },
  input: {
    marginBottom: 12,
    backgroundColor: "#FFFFFF",
  },
  sectionLabel: {
    fontWeight: "600",
    fontSize: 13,
    color: "#111827",
    marginBottom: 4,
  },
  segmented: {
    marginBottom: 12,
  },
  radioRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  mainButton: {
    borderRadius: 999,
    marginTop: 16,
    marginBottom: 8,
  },
  mainButtonLabel: {
    fontSize: 16,
    fontWeight: "600",
  },
  footerRow: {
    flexDirection: "row",
    justifyContent: "center",
    marginTop: 8,
  },
});
