import React, { useState } from "react";
import { ScrollView, View, StyleSheet, Alert } from "react-native";
import {
  Card,
  Button,
  Text,
  SegmentedButtons,
  TextInput,
  ActivityIndicator,
  Icon,
  useTheme,
} from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import { BASE_URL } from "../config";

type WorkoutExercise = {
  name: string;
  sets: string;
  reps: string;
  rest: string;
  notes?: string;
};

type WorkoutDay = {
  label: string;
  focus: string;
  exercises: WorkoutExercise[];
  notes: string[];
};

type WorkoutWeek = {
  week_number: number;
  goal_focus: string;
  days: WorkoutDay[];
};

type AIWorkoutPlanResponse = {
  meta: {
    split: string;
    days_per_week: number;
    experience: string;
    focus: string;
    equipment: string;
    language: "en" | "ar";
  };
  weeks: WorkoutWeek[];
};

export default function WorkoutsScreen({ route }: any) {
  const theme = useTheme();
  const { userId, token } = route?.params ?? {};

  // User inputs (all English)
  const [experience, setExperience] = useState<"beginner" | "intermediate" | "advanced">(
    "beginner"
  );
  const [daysPerWeek, setDaysPerWeek] = useState<"3" | "4" | "5" | "6">("4");
  const [split, setSplit] = useState<"full_body" | "upper_lower" | "push_pull_legs" | "bro_split">(
    "push_pull_legs"
  );
  const [equipment, setEquipment] = useState<"gym" | "home" | "both">("gym");
  const [focus, setFocus] = useState<
    "strength" | "muscle_gain" | "fat_loss" | "athletic" | "general_fitness"
  >("muscle_gain");
  const [injuries, setInjuries] = useState("");

  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<AIWorkoutPlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!userId) {
      Alert.alert(
        "Missing user",
        "userId is not available. Make sure you pass userId from HomeScreen navigation."
      );
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${BASE_URL}/ai/workout-plan/monthly`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          user_id: userId,
          prefs: {
            experience,
            days_per_week: Number(daysPerWeek),
            split,
            equipment,
            focus,
            injuries: injuries || null,
            language: "en", // 🔥 Always English
          },
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail =
          typeof data === "string" ? data : data?.detail || "Failed to generate workout plan";
        throw new Error(detail);
      }

      setPlan(data);
    } catch (err: any) {
      console.error("AI workout plan error:", err);
      setError(err.message || "Error generating workout plan.");
      Alert.alert("Error", err.message || "Error generating workout plan.");
    } finally {
      setLoading(false);
    }
  };

  const renderMetaCard = () => {
    if (!plan) return null;
    const m = plan.meta;

    return (
      <Card style={styles.metaCard}>
        <Card.Title
          title="Plan Overview"
          subtitle="Split • Days per week • Experience"
          left={(props) => <Icon {...props} source="dumbbell" color={brand.blue[600]} />}
        />
        <Card.Content>
          <Text style={styles.metaLine}>
            Split: <Text style={styles.metaValue}>{m.split}</Text>
          </Text>
          <Text style={styles.metaLine}>
            Days / week: <Text style={styles.metaValue}>{m.days_per_week}</Text>
          </Text>
          <Text style={styles.metaLine}>
            Experience: <Text style={styles.metaValue}>{m.experience}</Text>
          </Text>
          <Text style={styles.metaLine}>
            Focus: <Text style={styles.metaValue}>{m.focus}</Text>
          </Text>
          <Text style={styles.metaLine}>
            Equipment: <Text style={styles.metaValue}>{m.equipment}</Text>
          </Text>
        </Card.Content>
      </Card>
    );
  };

  const renderPlan = () => {
    if (!plan) return null;

    return (
      <>
        {plan.weeks.map((week) => (
          <Card key={week.week_number} style={styles.weekCard}>
            <Card.Title
              title={`Week ${week.week_number}`}
              subtitle={week.goal_focus}
              left={(props) => <Icon {...props} source="calendar-week" color={brand.green[600]} />}
            />
            <Card.Content>
              {week.days.map((day, index) => (
                <View key={index} style={styles.dayBlock}>
                  <Text style={styles.dayLabel}>{day.label}</Text>
                  <Text style={styles.dayFocus}>{day.focus}</Text>

                  {day.exercises.map((ex, i) => (
                    <View key={i} style={styles.exerciseRow}>
                      <Text style={styles.exerciseName}>• {ex.name}</Text>
                      <Text style={styles.exerciseDetail}>
                        Sets: {ex.sets} • Reps: {ex.reps} • Rest: {ex.rest}
                      </Text>
                      {ex.notes ? (
                        <Text style={styles.exerciseNotes}>Note: {ex.notes}</Text>
                      ) : null}
                    </View>
                  ))}

                  {day.notes && day.notes.length > 0 && (
                    <View style={styles.notesBlock}>
                      <Text style={styles.notesTitle}>Day Notes:</Text>
                      {day.notes.map((n, idx) => (
                        <Text key={idx} style={styles.noteItem}>
                          - {n}
                        </Text>
                      ))}
                    </View>
                  )}
                </View>
              ))}
            </Card.Content>
          </Card>
        ))}
      </>
    );
  };

  return (
    <ScreenScaffold title="AI Workout Plan">
      <ScrollView
        contentContainerStyle={{
          padding: 20,
          backgroundColor: theme.colors.background,
          gap: 16,
        }}
      >
        {/* Header */}
        <Card style={styles.headerCard}>
          <Card.Title
            title="AI Workout Coach"
            subtitle="Enter your preferences to get a full 1-month plan."
            left={(props) => <Icon {...props} source="arm-flex" color={brand.green[600]} />}
          />
        </Card>

        {/* Experience & Days */}
        <Card style={styles.card}>
          <Card.Title
            title="Experience & Frequency"
            left={(props) => <Icon {...props} source="progress-check" color={brand.blue[600]} />}
          />
          <Card.Content style={{ gap: 12 }}>
            <Text style={styles.label}>Experience level:</Text>
            <SegmentedButtons
              value={experience}
              onValueChange={(val) =>
                setExperience(val as "beginner" | "intermediate" | "advanced")
              }
              buttons={[
                { value: "beginner", label: "Beginner" },
                { value: "intermediate", label: "Intermediate" },
                { value: "advanced", label: "Advanced" },
              ]}
            />

            <Text style={[styles.label, { marginTop: 12 }]}>Days per week:</Text>
            <SegmentedButtons
              value={daysPerWeek}
              onValueChange={(val) => setDaysPerWeek(val as "3" | "4" | "5" | "6")}
              buttons={[
                { value: "3", label: "3" },
                { value: "4", label: "4" },
                { value: "5", label: "5" },
                { value: "6", label: "6" },
              ]}
            />
          </Card.Content>
        </Card>

        {/* Split & Equipment */}
        <Card style={styles.card}>
          <Card.Title
            title="Split & Equipment"
            left={(props) => <Icon {...props} source="dumbbell" color={brand.blue[600]} />}
          />
          <Card.Content style={{ gap: 12 }}>
            <Text style={styles.label}>Training split:</Text>
            <SegmentedButtons
              value={split}
              onValueChange={(val) =>
                setSplit(val as "full_body" | "upper_lower" | "push_pull_legs" | "bro_split")
              }
              buttons={[
                { value: "full_body", label: "Full body" },
                { value: "upper_lower", label: "Upper/Lower" },
                { value: "push_pull_legs", label: "PPL" },
                { value: "bro_split", label: "Bro Split" },
              ]}
            />

            <Text style={[styles.label, { marginTop: 12 }]}>Available equipment:</Text>
            <SegmentedButtons
              value={equipment}
              onValueChange={(val) => setEquipment(val as "gym" | "home" | "both")}
              buttons={[
                { value: "gym", label: "Gym" },
                { value: "home", label: "Home" },
                { value: "both", label: "Both" },
              ]}
            />
          </Card.Content>
        </Card>

        {/* Focus & Injuries */}
        <Card style={styles.card}>
          <Card.Title
            title="Goal focus & Injuries"
            left={(props) => <Icon {...props} source="target" color={brand.blue[600]} />}
          />
          <Card.Content style={{ gap: 12 }}>
            <Text style={styles.label}>Plan focus:</Text>
            <SegmentedButtons
              value={focus}
              onValueChange={(val) =>
                setFocus(
                  val as
                    | "strength"
                    | "muscle_gain"
                    | "fat_loss"
                    | "athletic"
                    | "general_fitness"
                )
              }
              buttons={[
                { value: "strength", label: "Strength" },
                { value: "muscle_gain", label: "Muscle gain" },
                { value: "fat_loss", label: "Fat loss" },
                { value: "athletic", label: "Athletic" },
                { value: "general_fitness", label: "General fitness" },
              ]}
            />

            <TextInput
              label="Injuries / limitations (optional)"
              value={injuries}
              onChangeText={setInjuries}
              mode="outlined"
              multiline
              style={{ marginTop: 8 }}
            />
          </Card.Content>
        </Card>

        {/* Generate Button */}
        <Button
          mode="contained"
          onPress={handleGenerate}
          style={styles.generateButton}
          buttonColor={brand.green[600]}
          disabled={loading}
          icon="lightning-bolt"
        >
          {loading ? "Generating plan..." : "Generate 1-Month Workout Plan"}
        </Button>

        {loading && (
          <ActivityIndicator
            style={{ marginTop: 12 }}
            animating={true}
            size="large"
            color={brand.green[600]}
          />
        )}

        {error && (
          <Text style={{ color: theme.colors.error, marginTop: 8, textAlign: "center" }}>
            {error}
          </Text>
        )}

        {/* Result */}
        {renderMetaCard()}
        {renderPlan()}
      </ScrollView>
    </ScreenScaffold>
  );
}

const styles = StyleSheet.create({
  headerCard: {
    borderRadius: 16,
  },
  card: {
    borderRadius: 16,
  },
  metaCard: {
    borderRadius: 16,
    marginTop: 12,
  },
  metaLine: {
    fontSize: 14,
    marginBottom: 4,
  },
  metaValue: {
    fontWeight: "600",
  },
  weekCard: {
    borderRadius: 16,
    marginTop: 12,
  },
  dayBlock: {
    marginTop: 8,
    paddingVertical: 8,
    borderTopWidth: 0.5,
    borderTopColor: "#ccc",
  },
  dayLabel: {
    fontWeight: "700",
    fontSize: 15,
    marginBottom: 2,
  },
  dayFocus: {
    fontSize: 13,
    opacity: 0.8,
    marginBottom: 6,
  },
  exerciseRow: {
    marginBottom: 6,
  },
  exerciseName: {
    fontWeight: "600",
  },
  exerciseDetail: {
    fontSize: 13,
  },
  exerciseNotes: {
    fontSize: 12,
    fontStyle: "italic",
    opacity: 0.8,
  },
  notesBlock: {
    marginTop: 6,
  },
  notesTitle: {
    fontWeight: "600",
    fontSize: 13,
  },
  noteItem: {
    fontSize: 12,
  },
  label: {
    fontSize: 14,
    marginBottom: 4,
    fontWeight: "500",
  },
  generateButton: {
    marginTop: 12,
    borderRadius: 24,
    paddingVertical: 6,
  },
});
