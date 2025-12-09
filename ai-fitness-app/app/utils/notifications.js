// app/utils/notifications.js
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import * as Application from "expo-application";
import * as ExpoDevicePush from "expo-notifications";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Platform } from "react-native";

const STORAGE_KEY = "FITNESS_NOTIF_IDS"; // { water:[], meal:[], workout:[], sleep:[] }

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

async function getStoredIds() {
  const raw = await AsyncStorage.getItem(STORAGE_KEY);
  return raw ? JSON.parse(raw) : { water: [], meal: [], workout: [], sleep: [] };
}

async function setStoredIds(next) {
  await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(next));
}

export async function registerForPushNotificationsAsync() {
  if (!Device.isDevice) {
    console.warn("Must use physical device for notifications");
    return { ok: false, expoPushToken: null };
  }

  // iOS: foreground presentation options (for a polished feel)
  if (Platform.OS === "ios") {
    await Notifications.setNotificationCategoryAsync("default", []);
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  if (existingStatus !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync({
      ios: { allowAlert: true, allowSound: true, allowBadge: true },
    });
    finalStatus = status;
  }
  if (finalStatus !== "granted") {
    console.warn("Notifications permission denied");
    return { ok: false, expoPushToken: null };
  }

  // Android channel (high importance)
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "General",
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 150, 150, 150],
      lightColor: "#007AFF",
      lockscreenVisibility: Notifications.AndroidNotificationVisibility.PUBLIC,
      bypassDnd: false,
      showBadge: true,
      sound: "default",
    });
  }

  // Expo push token (for server push later)
  let expoPushToken = null;
  try {
    const projectId = Application.applicationId ?? undefined;
    const token = await Notifications.getExpoPushTokenAsync({ projectId });
    expoPushToken = token?.data ?? null;
  } catch (e) {
    console.log("Expo push token error:", e?.message);
  }

  return { ok: true, expoPushToken };
}

/** Cancel all notifications for a given type (without touching others). */
export async function cancelType(type) {
  const ids = await getStoredIds();
  const list = ids[type] || [];
  for (const notifId of list) {
    try {
      await Notifications.cancelScheduledNotificationAsync(notifId);
    } catch {}
  }
  ids[type] = [];
  await setStoredIds(ids);
}

/** Schedule one or more specific daily times (24h). Example: [{hour:9, minute:0}, {hour:13, minute:0}] */
export async function scheduleDailyTimes(type, title, body, times = []) {
  await cancelType(type);
  const ids = await getStoredIds();

  const created = [];
  for (const t of times) {
    const notifId = await Notifications.scheduleNotificationAsync({
      content: { title, body, sound: "default", categoryIdentifier: "default" },
      trigger: {
        hour: t.hour,
        minute: t.minute,
        repeats: true,
        channelId: "default",
        // iOS: nextTriggerDate is auto-handled. Android exactness depends on OEM/Doze.
      },
    });
    created.push(notifId);
  }

  ids[type] = created;
  await setStoredIds(ids);
  return created.length;
}

/**
 * Schedule repeated reminders within a window (e.g., water every 2h 9:00–21:00).
 * intervalMinutes: number (e.g., 120)
 * window: {startHour, startMinute, endHour, endMinute}
 */
export async function scheduleIntervalWindow(type, title, body, intervalMinutes, window) {
  await cancelType(type);
  const ids = await getStoredIds();

  function* generateTimes() {
    const startM = window.startHour * 60 + (window.startMinute || 0);
    const endM = window.endHour * 60 + (window.endMinute || 0);
    for (let m = startM; m <= endM; m += intervalMinutes) {
      yield { hour: Math.floor(m / 60), minute: m % 60 };
    }
  }

  const created = [];
  for (const t of generateTimes()) {
    const notifId = await Notifications.scheduleNotificationAsync({
      content: { title, body, sound: "default", categoryIdentifier: "default" },
      trigger: { hour: t.hour, minute: t.minute, repeats: true, channelId: "default" },
    });
    created.push(notifId);
  }

  ids[type] = created;
  await setStoredIds(ids);
  return created.length;
}

/** Get a human summary for debug/UX. */
export async function getScheduleSummary() {
  const ids = await getStoredIds();
  return {
    water: ids.water.length,
    meal: ids.meal.length,
    workout: ids.workout.length,
    sleep: ids.sleep.length,
  };
}
