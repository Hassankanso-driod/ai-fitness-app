import React, { useEffect, useState } from "react";
import { ScrollView, View, ActivityIndicator } from "react-native";
import { Card, Text, Button, Surface, Icon, useTheme } from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import StatCard from "../components/StatCard";
import { brand } from "../utils/themeManager";
import { layoutStyles } from "../styles/globalStyles";
import { BASE_URL } from "../config";

export default function HomeScreen({ route, navigation }: any) {
  const theme = useTheme();

  // 👤 User info from login
  const { firstName, token, role, user_id, username } = route?.params ?? {};
  const displayName = firstName || username || "User";

  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // 🧠 Fetch user health stats
  const fetchUserStats = async () => {
    if (!user_id) {
      console.log("No user_id available, skipping stats fetch");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);

      const res = await fetch(`${BASE_URL}/user/${user_id}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();

      if (res.ok) {
        setStats(data);
      } else {
        console.log("Failed to fetch user stats:", data.detail || "Unknown error");
      }
    } catch (err) {
      console.error("Error fetching user stats:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user_id) {
      fetchUserStats();
    } else {
      setLoading(false);
    }
  }, [user_id]);

  return (
    <ScreenScaffold title="Home">
      <ScrollView
        contentContainerStyle={{
          padding: 20,
          backgroundColor: theme.colors.background,
        }}
      >
        {/* 👋 Welcome Header */}
        <Surface
          style={{
            marginVertical: 16,
            padding: 20,
            borderRadius: 20,
            backgroundColor: theme.colors.surface,
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <View>
            <Text
              variant="titleLarge"
              style={{ fontWeight: "700", color: theme.colors.onSurface }}
            >
              Welcome, {displayName}
            </Text>
            <Text style={{ color: theme.colors.onSurfaceVariant }}>
              {role === "admin" ? "Administrator Dashboard" : "Your Daily Overview"}
            </Text>
          </View>
          <Icon source="account-circle" size={36} color={brand.blue[600]} />
        </Surface>

        {/* 🔄 Loading state */}
        {loading && (
          <View style={{ alignItems: "center", marginTop: 50 }}>
            <ActivityIndicator size="large" color={brand.green[600]} />
            <Text style={{ marginTop: 10 }}>Loading your stats...</Text>
          </View>
        )}

        {/* 📊 Stats Cards + Goal */}
        {!loading && stats && (
          <>
            <View style={layoutStyles.rowWrap}>
              <StatCard
                icon="scale-bathroom"
                label="BMI"
                value={stats.bmi ?? "N/A"}
                color="blue"
              />
              <StatCard
                icon="fire"
                label="BMR"
                value={stats.bmr ? `${stats.bmr} kcal` : "N/A"}
                color="green"
              />
              <StatCard
                icon="cup-water"
                label="Water"
                value={stats.water_intake_l ? `${stats.water_intake_l} L/day` : "N/A"}
                color="orange"
              />
            </View>

            {/* 🎯 Goal */}
            <StatCard
              icon="target"
              label="Goal"
              value={stats.goal ? String(stats.goal).toUpperCase() : "N/A"}
              color="blue"
            />
          </>
        )}

        {/* 🛍️ Supplements Store */}
        <Card
          style={{
            borderRadius: 18,
            borderWidth: 1.5,
            borderColor: brand.orange[600],
            backgroundColor: "#FFF8F1",
            marginTop: 24,
            marginBottom: 20,
            shadowColor: "#000",
            shadowOpacity: 0.08,
            shadowRadius: 4,
            elevation: 3,
          }}
        >
          <Card.Title
            title="Supplements Store"
            subtitle="Explore nutrition boosters and performance enhancers."
            left={(props) => (
              <Icon {...props} source="bottle-soda-outline" color={brand.orange[600]} />
            )}
          />
          <Card.Actions style={{ marginTop: 10 }}>
            <Button
              mode="contained"
              buttonColor={brand.orange[600]}
              textColor="#fff"
              style={{ borderRadius: 10 }}
              onPress={() =>
                navigation.navigate("Supplements", {
                  firstName: displayName,
                  role,
                  userId: user_id,
                })
              }
            >
              {role === "admin" ? "Manage Store" : "View Store"}
            </Button>
          </Card.Actions>
        </Card>

        {/* 🧠 AI Workout Plan (WorkoutsScreen) */}
        <Card
          style={{
            borderRadius: 18,
            borderWidth: 1.5,
            borderColor: brand.green[600],
            backgroundColor: "#F0FDF4",
            marginBottom: 20,
          }}
        >
          <Card.Title
            title="AI Workout Plan"
            subtitle="Generate a 1-month smart training plan."
            left={(props) => <Icon {...props} source="dumbbell" color={brand.green[600]} />}
          />
          <Card.Actions>
            <Button
              mode="contained"
              buttonColor={brand.green[600]}
              textColor="#fff"
              onPress={() =>
                navigation.navigate("Workouts", {
                  userId: user_id,
                  token,
                })
              }
            >
              Open Workout Planner
            </Button>
          </Card.Actions>
        </Card>

        {/* 🍽️ AI Meal Planning */}
        <Card
          style={{
            borderRadius: 18,
            borderWidth: 1.5,
            borderColor: brand.orange[600],
            backgroundColor: "#FFF7ED",
            marginBottom: 20,
          }}
        >
          <Card.Title
            title="Meal Planning"
            subtitle="AI-powered 7-day meal plan tailored to you."
            left={(props) => <Icon {...props} source="food" color={brand.orange[600]} />}
          />
          <Card.Actions>
            <Button
              mode="contained"
              buttonColor={brand.orange[600]}
              textColor="#fff"
              onPress={() =>
                navigation.navigate("MealPlanning", {
                  userId: user_id,
                  token,
                })
              }
            >
              Plan Meals
            </Button>
          </Card.Actions>
        </Card>

        {/* 🛠️ Admin Panel (only for admins) */}
        {role === "admin" && (
          <Card
            style={{
              borderRadius: 18,
              borderWidth: 1.5,
              borderColor: brand.blue[600],
              backgroundColor: "#E0F2FE",
              marginBottom: 20,
            }}
          >
            <Card.Title
              title="Admin Panel"
              subtitle="Manage data and advanced features"
              left={(props) => <Icon {...props} source="shield-account" />}
            />
            <Card.Actions style={{ flexDirection: "column", gap: 8 }}>
              <Button
                mode="contained"
                buttonColor={brand.blue[600]}
                textColor="#fff"
                icon="view-dashboard"
                style={{ width: "100%", marginBottom: 8 }}
                onPress={() =>
                  navigation.navigate("Management", {
                    firstName: displayName,
                    token,
                    userId: user_id,
                  })
                }
              >
                Management Dashboard
              </Button>
              <Button
                mode="outlined"
                textColor={brand.orange[700]}
                icon="store"
                style={{ width: "100%" }}
                onPress={() =>
                  navigation.navigate("Supplements", {
                    firstName: displayName,
                    role: "admin",
                    userId: user_id,
                  })
                }
              >
                Manage Supplements
              </Button>
            </Card.Actions>
          </Card>
        )}
      </ScrollView>
    </ScreenScaffold>
  );
}
