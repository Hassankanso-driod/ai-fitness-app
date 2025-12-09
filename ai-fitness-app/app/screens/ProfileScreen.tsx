/**
 * ProfileScreen.tsx - User Profile
 *
 * - View & edit profile: name, age, height, weight, goal
 * - Shows BMI, BMR, recommended water
 * - Quick navigation to Workout Tracking & Meal Planning
 * - Logout button
 */

import React, { useState, useEffect } from "react";
import {
  ScrollView,
  View,
  Alert,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
} from "react-native";
import {
  Card,
  Text,
  Button,
  TextInput,
  ActivityIndicator,
  Surface,
  Icon,
} from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import { BASE_URL } from "../config";

export default function ProfileScreen({ route, navigation }: any) {
  // Support both userId (Stack) and user_id (Tabs initialParams)
  const { userId: stackUserId, user_id, firstName, token } = route?.params ?? {};
  const userId = stackUserId ?? user_id;

  // State management
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [user, setUser] = useState<any>(null);

  const [formData, setFormData] = useState({
    first_name: "",
    age: "",
    height_cm: "",
    weight_kg: "",
    goal: "",
  });

  useEffect(() => {
    fetchUserProfile();
  }, [userId]);

  /**
   * fetchUserProfile - Loads user data from the backend API
   */
  const fetchUserProfile = async () => {
    if (!userId) {
      console.log("⚠️ No userId passed to ProfileScreen");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const res = await fetch(`${BASE_URL}/user/${userId}`, {
        headers: token
          ? { Authorization: `Bearer ${token}` }
          : undefined,
      });
      const data = await res.json();

      if (res.ok) {
        setUser(data);
        setFormData({
          first_name: data.first_name || "",
          age: data.age?.toString() || "",
          height_cm: data.height_cm?.toString() || "",
          weight_kg: data.weight_kg?.toString() || "",
          goal: data.goal || "",
        });
      } else {
        console.log("Failed to fetch user profile:", data?.detail || data);
        Alert.alert("Error", data?.detail || "Failed to load profile");
      }
    } catch (err) {
      console.error("Error fetching user profile:", err);
      Alert.alert("Error", "Could not connect to server");
    } finally {
      setLoading(false);
    }
  };

  /**
   * handleSave - Saves edited profile information to the database
   */
  const handleSave = async () => {
    if (!userId) {
      Alert.alert("Error", "User ID is missing");
      return;
    }

    try {
      setSaving(true);
      const res = await fetch(`${BASE_URL}/user/${userId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          first_name: formData.first_name || undefined,
          age: formData.age ? parseInt(formData.age) : undefined,
          height_cm: formData.height_cm ? parseFloat(formData.height_cm) : undefined,
          weight_kg: formData.weight_kg ? parseFloat(formData.weight_kg) : undefined,
          goal: formData.goal || undefined,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        Alert.alert(
          "Success ✅",
          "Profile updated successfully.\nBMI, BMR and water target have been recalculated."
        );
        setEditing(false);
        await fetchUserProfile();
      } else {
        Alert.alert("Error", data.detail || "Failed to update profile");
      }
    } catch (err) {
      console.error("Error updating profile:", err);
      Alert.alert("Error", "Failed to connect to backend");
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    Alert.alert("Logout", "Are you sure you want to logout?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Logout",
        style: "destructive",
        onPress: () => {
          navigation.reset({
            index: 0,
            routes: [{ name: "Welcome" }],
          });
        },
      },
    ]);
  };

  if (loading) {
    return (
      <ScreenScaffold title="Profile">
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={brand.blue[600]} />
        </View>
      </ScreenScaffold>
    );
  }

  return (
    <ScreenScaffold title="Profile">
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={{ flex: 1 }}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {/* Profile Header */}
          <Surface style={styles.headerSurface}>
            <View style={styles.headerLeft}>
              <Text style={styles.greetingText}>Welcome back,</Text>
              <Text style={styles.nameText}>
                {user?.first_name || firstName || "Athlete"}
              </Text>
              <Text style={styles.goalText}>
                {user?.goal
                  ? `Goal: ${user.goal.toUpperCase()}`
                  : "Set your fitness goal to get better recommendations."}
              </Text>
            </View>
            <Icon source="account-circle" size={72} color={brand.blue[600]} />
          </Surface>

          {/* Stats Cards - BMI, BMR, Water */}
          <View style={styles.statsRow}>
            <Card style={[styles.statCard, { backgroundColor: brand.green[50] }]}>
              <Text style={styles.statLabel}>BMI</Text>
              <Text style={[styles.statValue, { color: brand.green[700] }]}>
                {user?.bmi ? user.bmi.toFixed(1) : "N/A"}
              </Text>
            </Card>
            <Card style={[styles.statCard, { backgroundColor: brand.blue[50] }]}>
              <Text style={styles.statLabel}>BMR</Text>
              <Text style={[styles.statValue, { color: brand.blue[700] }]}>
                {user?.bmr ? `${user.bmr} kcal` : "N/A"}
              </Text>
            </Card>
            <Card style={[styles.statCard, { backgroundColor: brand.orange[50] }]}>
              <Text style={styles.statLabel}>Water</Text>
              <Text style={[styles.statValue, { color: brand.orange[700] }]}>
                {user?.water_intake_l ? `${user.water_intake_l} L` : "N/A"}
              </Text>
            </Card>
          </View>

          {/* Edit Profile Form */}
          <Card style={styles.sectionCard}>
            <Card.Title
              title="Personal Information"
              subtitle="Keep your profile updated for accurate plans"
              right={(props) => (
                <Button
                  {...props}
                  mode={editing ? "contained" : "outlined"}
                  onPress={() => {
                    if (editing) {
                      handleSave();
                    } else {
                      setEditing(true);
                    }
                  }}
                  loading={saving}
                >
                  {editing ? "Save" : "Edit"}
                </Button>
              )}
            />
            <Card.Content>
              <TextInput
                label="Name"
                value={formData.first_name}
                onChangeText={(text) =>
                  setFormData((prev) => ({ ...prev, first_name: text }))
                }
                mode="outlined"
                disabled={!editing}
                style={styles.input}
              />
              <View style={styles.row}>
                <TextInput
                  label="Age"
                  value={formData.age}
                  onChangeText={(text) =>
                    setFormData((prev) => ({ ...prev, age: text }))
                  }
                  mode="outlined"
                  keyboardType="numeric"
                  disabled={!editing}
                  style={[styles.input, styles.halfInput]}
                />
                <TextInput
                  label="Height (cm)"
                  value={formData.height_cm}
                  onChangeText={(text) =>
                    setFormData((prev) => ({ ...prev, height_cm: text }))
                  }
                  mode="outlined"
                  keyboardType="numeric"
                  disabled={!editing}
                  style={[styles.input, styles.halfInput]}
                />
              </View>
              <TextInput
                label="Weight (kg)"
                value={formData.weight_kg}
                onChangeText={(text) =>
                  setFormData((prev) => ({ ...prev, weight_kg: text }))
                }
                mode="outlined"
                keyboardType="numeric"
                disabled={!editing}
                style={styles.input}
              />
              <TextInput
                label="Goal"
                value={formData.goal}
                onChangeText={(text) =>
                  setFormData((prev) => ({ ...prev, goal: text }))
                }
                mode="outlined"
                disabled={!editing}
                placeholder="lose, maintain, gain"
                style={styles.input}
              />
            </Card.Content>
          </Card>

          {/* Quick Actions */}
          <Card style={styles.sectionCard}>
            <Card.Title
              title="Quick Actions"
              subtitle="Jump to your main tools"
            />
            <Card.Content>
              <Button
                mode="outlined"
                icon="dumbbell"
                onPress={() =>
                  navigation.navigate("WorkoutTracking", { userId, token })
                }
                style={styles.actionButton}
              >
                Workout Tracking
              </Button>
              <Button
                mode="outlined"
                icon="food"
                onPress={() =>
                  navigation.navigate("MealPlanning", { userId, token })
                }
                style={styles.actionButton}
              >
                Meal Planning
              </Button>
            </Card.Content>
          </Card>

          {/* Reminders shortcut */}
          <Card style={styles.sectionCard}>
            <Card.Title
              title="Reminders & Notifications"
              subtitle="Manage your water, meal and workout reminders"
            />
            <Card.Content>
              <Button
                mode="outlined"
                icon="bell"
                onPress={() => navigation.navigate("Reminders")}
                style={styles.actionButton}
              >
                Reminder Settings
              </Button>
            </Card.Content>
          </Card>

          {/* Logout */}
          <Button
            mode="contained"
            buttonColor="#DC2626"
            textColor="#fff"
            icon="logout"
            onPress={handleLogout}
            style={styles.logoutButton}
          >
            Logout
          </Button>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenScaffold>
  );
}

const styles = StyleSheet.create({
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
    backgroundColor: "#F9FAFB",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  headerSurface: {
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#E5E7EB",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  headerLeft: {
    flex: 1,
    paddingRight: 12,
  },
  greetingText: {
    fontSize: 13,
    color: "#6B7280",
  },
  nameText: {
    fontSize: 22,
    fontWeight: "700",
    color: "#111827",
    marginTop: 2,
  },
  goalText: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 6,
  },
  statsRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    padding: 12,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#E5E7EB",
  },
  statLabel: {
    fontSize: 11,
    color: "#6B7280",
  },
  statValue: {
    fontSize: 18,
    fontWeight: "700",
    marginTop: 4,
  },
  sectionCard: {
    marginBottom: 20,
    borderRadius: 18,
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#E5E7EB",
  },
  input: {
    marginBottom: 12,
  },
  row: {
    flexDirection: "row",
    gap: 12,
  },
  halfInput: {
    flex: 1,
  },
  actionButton: {
    marginBottom: 8,
  },
  logoutButton: {
    marginTop: 8,
    marginBottom: 40,
    borderRadius: 999,
  },
});

