/**
 * RemindersScreen.tsx - Smart Reminder Management
 * 
 * This screen allows users to set up and manage reminders for:
 * - Water intake (interval-based reminders)
 * - Meals (daily at specific time)
 * - Workouts (daily at specific time)
 * - Sleep (daily bedtime reminder)
 * 
 * Features:
 * - Toggle reminders on/off
 * - Set custom times for daily reminders
 * - Configure water reminder intervals (30, 60, 90, 120, 180 minutes)
 * - Set water reminder time window (start and end times)
 * - View all scheduled notifications
 * - Save preferences to Firebase Firestore
 * 
 * How it works:
 * 1. User toggles a reminder type on
 * 2. App schedules notifications using expo-notifications
 * 3. Preferences are saved to Firebase for persistence
 * 4. Notifications are sent at the specified times
 */

import React, { useState, useEffect } from "react";
import { ScrollView, Alert, View, Modal, Pressable, StyleSheet } from "react-native";
import { Card, Switch, Button, Text } from "react-native-paper";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import DateTimePicker from "@react-native-community/datetimepicker";
import * as Notifications from "expo-notifications";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import {
  registerForPushNotificationsAsync,
  scheduleDailyTimes,
  scheduleIntervalWindow,
  cancelType,
} from "../utils/notifications";
import { db } from "../utils/firebaseconfig";
import { doc, getDoc, setDoc } from "firebase/firestore";

// Type definitions for TypeScript
type ReminderType = "water" | "meal" | "workout" | "sleep";
type TimeHM = { hour: number; minute: number };
type WaterWindow = { startHour: number; startMinute: number; endHour: number; endMinute: number };

export default function RemindersScreen() {
  // User ID - In a real app, this would come from authentication
  const userId = "user_demo";

  // --- States --------------------------------------------------------------
  const [waterOn, setWaterOn] = useState(false);
  const [mealOn, setMealOn] = useState(false);
  const [workoutOn, setWorkoutOn] = useState(false);
  const [sleepOn, setSleepOn] = useState(false);

  const [waterInterval, setWaterInterval] = useState(120);
  const [waterWindow, setWaterWindow] = useState<WaterWindow>({
    startHour: 9,
    startMinute: 0,
    endHour: 21,
    endMinute: 0,
  });

  const [mealTime, setMealTime] = useState<TimeHM>({ hour: 13, minute: 0 });
  const [workoutTime, setWorkoutTime] = useState<TimeHM>({ hour: 18, minute: 0 });
  const [sleepTime, setSleepTime] = useState<TimeHM>({ hour: 23, minute: 0 });

  const [showPicker, setShowPicker] = useState(false);
  const [pickerType, setPickerType] = useState<ReminderType | null>(null);
  const [currentValue, setCurrentValue] = useState(new Date());
  const [showIntervalModal, setShowIntervalModal] = useState(false);

  const [scheduledList, setScheduledList] = useState<
    { title: string; time: string }[]
  >([]);

  // --- Initial setup -------------------------------------------------------
  useEffect(() => {
    (async () => {
      const { ok, expoPushToken } = await registerForPushNotificationsAsync();
      if (ok && expoPushToken)
        await setDoc(doc(db, "users", userId), { expoPushToken }, { merge: true });
      await loadReminders();
      await refreshScheduled();
    })();
  }, []);

  async function loadReminders() {
    const ref = doc(db, "reminders", userId);
    const snap = await getDoc(ref);
    if (!snap.exists()) return;
    const d = snap.data();
    if (d.waterOn !== undefined) setWaterOn(d.waterOn);
    if (d.mealOn !== undefined) setMealOn(d.mealOn);
    if (d.workoutOn !== undefined) setWorkoutOn(d.workoutOn);
    if (d.sleepOn !== undefined) setSleepOn(d.sleepOn);
    if (d.waterInterval) setWaterInterval(d.waterInterval);
    if (d.waterWindow) setWaterWindow(d.waterWindow);
    if (d.mealTime) setMealTime(d.mealTime);
    if (d.workoutTime) setWorkoutTime(d.workoutTime);
    if (d.sleepTime) setSleepTime(d.sleepTime);
  }

  async function saveReminders(updates: any) {
    await setDoc(doc(db, "reminders", userId), updates, { merge: true });
  }

  // --- Notification scheduling ---------------------------------------------
  async function enableWater() {
    await scheduleIntervalWindow(
      "water",
      "💧 Water Reminder",
      "Stay hydrated!",
      waterInterval,
      waterWindow
    );
  }
  async function enableMeal() {
    await scheduleDailyTimes("meal", "🍽️ Meal Reminder", "Time for your meal!", [mealTime]);
  }
  async function enableWorkout() {
    await scheduleDailyTimes(
      "workout",
      "🏋️ Workout Reminder",
      "Get ready to train!",
      [workoutTime]
    );
  }
  async function enableSleep() {
    await scheduleDailyTimes("sleep", "😴 Sleep Reminder", "Wind down for bed.", [sleepTime]);
  }

  async function refreshScheduled() {
    const all = await Notifications.getAllScheduledNotificationsAsync();
    const formatted = all.map((n) => {
      const t = n.trigger as any;
      const time =
        t?.hour !== undefined
          ? `${String(t.hour).padStart(2, "0")}:${String(t.minute).padStart(2, "0")}`
          : "custom";
      return { title: n.content.title || "Reminder", time };
    });
    setScheduledList(formatted);
  }

  // --- Toggle logic --------------------------------------------------------
  async function handleToggle(type: ReminderType, value: boolean) {
    switch (type) {
      case "water":
        setWaterOn(value);
        value ? await enableWater() : await cancelType("water");
        await saveReminders({ waterOn: value });
        break;
      case "meal":
        setMealOn(value);
        value ? await enableMeal() : await cancelType("meal");
        await saveReminders({ mealOn: value });
        break;
      case "workout":
        setWorkoutOn(value);
        value ? await enableWorkout() : await cancelType("workout");
        await saveReminders({ workoutOn: value });
        break;
      case "sleep":
        setSleepOn(value);
        value ? await enableSleep() : await cancelType("sleep");
        await saveReminders({ sleepOn: value });
        break;
    }
    await refreshScheduled();
  }

  // --- Picker logic --------------------------------------------------------
  function openTimePicker(type: ReminderType) {
    setPickerType(type);
    let init = new Date();
    if (type === "meal") init.setHours(mealTime.hour, mealTime.minute);
    if (type === "workout") init.setHours(workoutTime.hour, workoutTime.minute);
    if (type === "sleep") init.setHours(sleepTime.hour, sleepTime.minute);
    setCurrentValue(init);
    setShowPicker(true);
  }

  async function handlePickedTime(selectedDate?: Date) {
    if (!selectedDate || !pickerType) {
      setShowPicker(false);
      return;
    }

    const newHour = selectedDate.getHours();
    const newMinute = selectedDate.getMinutes();
    const newObj = { hour: newHour, minute: newMinute };

    switch (pickerType) {
      case "meal":
        setMealTime(newObj);
        await saveReminders({ mealTime: newObj });
        if (mealOn) await enableMeal();
        break;
      case "workout":
        setWorkoutTime(newObj);
        await saveReminders({ workoutTime: newObj });
        if (workoutOn) await enableWorkout();
        break;
      case "sleep":
        setSleepTime(newObj);
        await saveReminders({ sleepTime: newObj });
        if (sleepOn) await enableSleep();
        break;
    }

    setShowPicker(false);
    await refreshScheduled();
    Alert.alert("✅ Time updated!");
  }

  // --- Water interval modal -----------------------------------------------
  async function handleIntervalChange(min: number) {
    setShowIntervalModal(false);
    setWaterInterval(min);
    await saveReminders({ waterInterval: min });
    if (waterOn) await enableWater();
    await refreshScheduled();
    Alert.alert(`Water reminder set every ${min} minutes.`);
  }

  // --- UI -----------------------------------------------------------------
  return (
    <ScreenScaffold title="Reminders">
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        {/* Summary */}
        <Card style={styles.summary}>
          <Text style={styles.summaryTitle}>Your Active Reminders</Text>
          <Text>💧 Water: {waterOn ? "On" : "Off"} ({waterInterval} min)</Text>
          <Text>
            🍽️ Meal: {mealOn ? "On" : "Off"} at {mealTime.hour}:
            {mealTime.minute.toString().padStart(2, "0")}
          </Text>
          <Text>
            🏋️ Workout: {workoutOn ? "On" : "Off"} at {workoutTime.hour}:
            {workoutTime.minute.toString().padStart(2, "0")}
          </Text>
          <Text>
            😴 Sleep: {sleepOn ? "On" : "Off"} at {sleepTime.hour}:
            {sleepTime.minute.toString().padStart(2, "0")}
          </Text>
          <Button mode="outlined" icon="bell" style={{ marginTop: 8 }} onPress={refreshScheduled}>
            View Scheduled Notifications
          </Button>
        </Card>

        {/* Pretty notification list */}
        {scheduledList.length > 0 && (
          <Card style={styles.notifCard}>
            <Text style={styles.notifTitle}>📅 Scheduled Notifications</Text>
            {scheduledList.map((n, i) => (
              <View key={i} style={styles.notifRow}>
                <MaterialCommunityIcons name="bell-outline" color="#007AFF" size={18} />
                <Text style={{ marginLeft: 6 }}>
                  {n.title.replace("Reminder", "").trim()} → {n.time}
                </Text>
              </View>
            ))}
          </Card>
        )}

        {/* Water */}
        <Card style={[styles.card, { borderLeftColor: brand.blue[600] }]}>
          <Card.Title
            title="Water 💧"
            subtitle={`Every ${waterInterval} min (${waterWindow.startHour}:00 → ${waterWindow.endHour}:00)`}
            left={() => <MaterialCommunityIcons name="cup-water" color={brand.blue[600]} size={28} />}
            right={() => (
              <View style={styles.row}>
                <Button onPress={() => setShowIntervalModal(true)}>🔁 Interval</Button>
                <Switch value={waterOn} onValueChange={(v) => handleToggle("water", v)} color={brand.blue[600]} />
              </View>
            )}
          />
        </Card>

        {/* Meal */}
        <Card style={[styles.card, { borderLeftColor: brand.green[600] }]}>
          <Card.Title
            title="Meal 🍽️"
            subtitle={`Next at ${mealTime.hour}:${mealTime.minute.toString().padStart(2, "0")}`}
            left={() => <MaterialCommunityIcons name="food" color={brand.green[600]} size={28} />}
            right={() => (
              <View style={styles.row}>
                <Button onPress={() => openTimePicker("meal")}>🕒 Time</Button>
                <Switch value={mealOn} onValueChange={(v) => handleToggle("meal", v)} color={brand.green[600]} />
              </View>
            )}
          />
        </Card>

        {/* Workout */}
        <Card style={[styles.card, { borderLeftColor: brand.orange[600] }]}>
          <Card.Title
            title="Workout 🏋️"
            subtitle={`At ${workoutTime.hour}:${workoutTime.minute.toString().padStart(2, "0")}`}
            left={() => <MaterialCommunityIcons name="dumbbell" color={brand.orange[600]} size={28} />}
            right={() => (
              <View style={styles.row}>
                <Button onPress={() => openTimePicker("workout")}>🕒 Time</Button>
                <Switch value={workoutOn} onValueChange={(v) => handleToggle("workout", v)} color={brand.orange[600]} />
              </View>
            )}
          />
        </Card>

        {/* Sleep */}
        <Card style={[styles.card, { borderLeftColor: "#9b59b6" }]}>
          <Card.Title
            title="Sleep 😴"
            subtitle={`At ${sleepTime.hour}:${sleepTime.minute.toString().padStart(2, "0")}`}
            left={() => <MaterialCommunityIcons name="sleep" color="#9b59b6" size={28} />}
            right={() => (
              <View style={styles.row}>
                <Button onPress={() => openTimePicker("sleep")}>🕒 Time</Button>
                <Switch value={sleepOn} onValueChange={(v) => handleToggle("sleep", v)} color="#9b59b6" />
              </View>
            )}
          />
        </Card>

        {/* Interval Modal */}
        <Modal visible={showIntervalModal} transparent animationType="slide">
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Choose Water Interval</Text>
              {[30, 60, 90, 120, 180].map((min) => (
                <Pressable key={min} onPress={() => handleIntervalChange(min)} style={styles.intervalBtn}>
                  <Text style={styles.intervalText}>{`Every ${min} minutes`}</Text>
                </Pressable>
              ))}
              <Button onPress={() => setShowIntervalModal(false)} textColor="red">
                Cancel
              </Button>
            </View>
          </View>
        </Modal>

        {/* Time Picker */}
        {showPicker && (
          <DateTimePicker
            mode="time"
            is24Hour
            value={currentValue}
            onChange={(_, d) => handlePickedTime(d || undefined)}
          />
        )}
      </ScrollView>
    </ScreenScaffold>
  );
}

// --- Styles ---------------------------------------------------------------
const styles = StyleSheet.create({
  summary: {
    padding: 16,
    borderRadius: 16,
    backgroundColor: "#e8f0ff",
    marginBottom: 16,
  },
  summaryTitle: { fontWeight: "700", marginBottom: 6 },
  notifCard: { padding: 12, borderRadius: 12, marginBottom: 16 },
  notifTitle: { fontWeight: "700", marginBottom: 6 },
  notifRow: { flexDirection: "row", alignItems: "center", marginVertical: 3 },
  card: { borderRadius: 16, borderLeftWidth: 4, marginBottom: 16 },
  row: { flexDirection: "row", alignItems: "center", gap: 4 },
  modalContainer: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.4)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: "#fff",
    padding: 20,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
  },
  modalTitle: { fontSize: 18, fontWeight: "700", marginBottom: 12, textAlign: "center" },
  intervalBtn: { paddingVertical: 10, borderBottomWidth: 0.5, borderColor: "#ccc" },
  intervalText: { fontSize: 16, textAlign: "center" },
});
