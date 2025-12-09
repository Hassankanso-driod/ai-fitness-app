import React, { useState, useEffect } from "react";
import { ScrollView, View, Alert, Modal, StyleSheet } from "react-native";
import { Card, Text, Button, TextInput, ActivityIndicator, Surface, Icon, IconButton, Chip } from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import { BASE_URL } from "../config";

export default function WorkoutTrackingScreen({ route, navigation }: any) {
  const { userId, token } = route?.params ?? {};
  const [workouts, setWorkouts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [timerActive, setTimerActive] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);

  const [formData, setFormData] = useState({
    exercise_name: "",
    category: "fullbody",
    sets: "",
    reps: "",
    weight_kg: "",
    duration_minutes: "",
    notes: "",
  });

  useEffect(() => {
    fetchWorkouts();
  }, [userId]);

  useEffect(() => {
    let interval: any;
    if (timerActive) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [timerActive]);

  const fetchWorkouts = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${BASE_URL}/workouts/${userId}`);
      const data = await res.json();
      if (res.ok) {
        setWorkouts(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogWorkout = async () => {
    if (!formData.exercise_name || !formData.sets || !formData.reps) {
      Alert.alert("Missing Fields", "Please fill in exercise name, sets, and reps");
      return;
    }

    try {
      const res = await fetch(`${BASE_URL}/workouts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: userId,
          exercise_name: formData.exercise_name,
          category: formData.category,
          sets: parseInt(formData.sets),
          reps: parseInt(formData.reps),
          weight_kg: formData.weight_kg ? parseFloat(formData.weight_kg) : null,
          duration_minutes: formData.duration_minutes ? parseInt(formData.duration_minutes) : null,
          notes: formData.notes || null,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        Alert.alert("Success ✅", "Workout logged successfully!");
        setShowModal(false);
        setFormData({
          exercise_name: "",
          category: "fullbody",
          sets: "",
          reps: "",
          weight_kg: "",
          duration_minutes: "",
          notes: "",
        });
        fetchWorkouts();
      } else {
        Alert.alert("Error", data.detail || "Failed to log workout");
      }
    } catch (err) {
      Alert.alert("Error", "Failed to connect to backend");
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <ScreenScaffold title="Workout Tracking 🏋️">
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        {/* Timer Card */}
        <Card style={{ marginBottom: 16, backgroundColor: brand.blue[50] }}>
          <Card.Content>
            <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <View>
                <Text style={{ fontSize: 12, color: "#666" }}>Workout Timer</Text>
                <Text style={{ fontSize: 32, fontWeight: "700", color: brand.blue[700] }}>
                  {formatTime(timerSeconds)}
                </Text>
              </View>
              <View style={{ flexDirection: "row", gap: 8 }}>
                <Button
                  mode={timerActive ? "contained" : "outlined"}
                  buttonColor={timerActive ? brand.orange[600] : brand.green[600]}
                  onPress={() => setTimerActive(!timerActive)}
                  icon={timerActive ? "pause" : "play"}
                >
                  {timerActive ? "Pause" : "Start"}
                </Button>
                <Button
                  mode="outlined"
                  onPress={() => {
                    setTimerSeconds(0);
                    setTimerActive(false);
                  }}
                  icon="stop"
                >
                  Reset
                </Button>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Log Workout Button */}
        <Button
          mode="contained"
          buttonColor={brand.green[600]}
          icon="plus"
          onPress={() => setShowModal(true)}
          style={{ marginBottom: 20 }}
        >
          Log New Workout
        </Button>

        {/* Workout History */}
        {loading ? (
          <ActivityIndicator size="large" color={brand.blue[600]} />
        ) : workouts.length === 0 ? (
          <Surface style={{ padding: 40, borderRadius: 16, alignItems: "center" }}>
            <Icon source="dumbbell" size={64} color="#999" />
            <Text style={{ marginTop: 16, color: "#666" }}>No workouts logged yet</Text>
            <Text style={{ marginTop: 8, color: "#999", fontSize: 12 }}>Start logging your workouts!</Text>
          </Surface>
        ) : (
          workouts.map((workout) => (
            <Card key={workout.id} style={{ marginBottom: 12 }}>
              <Card.Content>
                <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
                  <Text style={{ fontSize: 18, fontWeight: "700" }}>{workout.exercise_name}</Text>
                  <Chip style={{ backgroundColor: brand.blue[50] }}>{workout.category}</Chip>
                </View>
                <View style={{ flexDirection: "row", gap: 16, marginBottom: 8 }}>
                  <Text style={{ color: "#666" }}>Sets: <Text style={{ fontWeight: "600" }}>{workout.sets}</Text></Text>
                  <Text style={{ color: "#666" }}>Reps: <Text style={{ fontWeight: "600" }}>{workout.reps}</Text></Text>
                  {workout.weight_kg && (
                    <Text style={{ color: "#666" }}>Weight: <Text style={{ fontWeight: "600" }}>{workout.weight_kg} kg</Text></Text>
                  )}
                </View>
                {workout.notes && (
                  <Text style={{ color: "#666", fontStyle: "italic", marginBottom: 8 }}>{workout.notes}</Text>
                )}
                <Text style={{ fontSize: 12, color: "#999" }}>{formatDate(workout.created_at)}</Text>
              </Card.Content>
            </Card>
          ))
        )}

        {/* Log Workout Modal */}
        <Modal visible={showModal} animationType="slide" transparent>
          <View style={styles.modalOverlay}>
            <Surface style={styles.modalContent}>
              <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                <Text variant="headlineSmall" style={{ fontWeight: "700" }}>Log Workout</Text>
                <IconButton icon="close" onPress={() => setShowModal(false)} />
              </View>
              <ScrollView>
                <TextInput
                  label="Exercise Name"
                  value={formData.exercise_name}
                  onChangeText={(text) => setFormData({ ...formData, exercise_name: text })}
                  mode="outlined"
                  style={{ marginBottom: 12 }}
                />
                <TextInput
                  label="Category"
                  value={formData.category}
                  onChangeText={(text) => setFormData({ ...formData, category: text })}
                  mode="outlined"
                  style={{ marginBottom: 12 }}
                  placeholder="fullbody, legs, chest, etc."
                />
                <View style={{ flexDirection: "row", gap: 12 }}>
                  <TextInput
                    label="Sets"
                    value={formData.sets}
                    onChangeText={(text) => setFormData({ ...formData, sets: text })}
                    mode="outlined"
                    keyboardType="numeric"
                    style={{ flex: 1, marginBottom: 12 }}
                  />
                  <TextInput
                    label="Reps"
                    value={formData.reps}
                    onChangeText={(text) => setFormData({ ...formData, reps: text })}
                    mode="outlined"
                    keyboardType="numeric"
                    style={{ flex: 1, marginBottom: 12 }}
                  />
                </View>
                <TextInput
                  label="Weight (kg) - Optional"
                  value={formData.weight_kg}
                  onChangeText={(text) => setFormData({ ...formData, weight_kg: text })}
                  mode="outlined"
                  keyboardType="numeric"
                  style={{ marginBottom: 12 }}
                />
                <TextInput
                  label="Duration (minutes) - Optional"
                  value={formData.duration_minutes}
                  onChangeText={(text) => setFormData({ ...formData, duration_minutes: text })}
                  mode="outlined"
                  keyboardType="numeric"
                  style={{ marginBottom: 12 }}
                />
                <TextInput
                  label="Notes - Optional"
                  value={formData.notes}
                  onChangeText={(text) => setFormData({ ...formData, notes: text })}
                  mode="outlined"
                  multiline
                  numberOfLines={3}
                  style={{ marginBottom: 20 }}
                />
                <Button mode="contained" buttonColor={brand.green[600]} onPress={handleLogWorkout}>
                  Log Workout
                </Button>
              </ScrollView>
            </Surface>
          </View>
        </Modal>
      </ScrollView>
    </ScreenScaffold>
  );
}

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: "#fff",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: "80%",
  },
});




