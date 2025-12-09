import React, { useState, useEffect } from "react";
import { ScrollView, View, StyleSheet, Alert } from "react-native";
import {
  Card,
  Text,
  Button,
  Switch,
  ActivityIndicator,
  Surface,
  Icon,
  useTheme,
  TextInput,
} from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import { BASE_URL } from "../config";

type DailyTargets = {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  water_liters: number;
};

type DayPlan = {
  day: string;
  breakfast: string;
  lunch: string;
  dinner: string;
  snacks: string;
  tips: string[];
  macros: DailyTargets;
};

type AIMealPlanResponse = {
  daily_targets: DailyTargets;
  week: DayPlan[];
};

export default function MealPlanningScreen({ route }: any) {
  const theme = useTheme();

  const { userId, token } = route?.params ?? {};
  const [diabetes, setDiabetes] = useState(false);
  const [obesity, setObesity] = useState(false);

  // ✅ جديد: تفضيلات الأكل + اللغة
  const [likedFoods, setLikedFoods] = useState("");
  const [dislikedFoods, setDislikedFoods] = useState("");
  const [language, setLanguage] = useState<"en" | "ar">("en");

  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<AIMealPlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const formatNumber = (n?: number, digits: number = 0) => {
    if (n === undefined || n === null || Number.isNaN(n)) return "--";
    return n.toFixed(digits);
  };

  // ✅ جديد: جلب آخر خطة محفوظة عند فتح الشاشة
  useEffect(() => {
    if (!userId) return;

    const fetchLatestPlan = async () => {
      try {
        const response = await fetch(
          `${BASE_URL}/ai/meal-plan/weekly/latest/${userId}`
        );

        if (!response.ok) {
          // 404 يعني ما في خطة محفوظة، عادي نتجاهل
          return;
        }

        const data = await response.json();
        setPlan(data);
      } catch (err) {
        console.warn("Failed to load latest AI meal plan", err);
      }
    };

    fetchLatestPlan();
  }, [userId]);

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
      const response = await fetch(`${BASE_URL}/ai/meal-plan/weekly`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // backend ما بيطلب التوكن، بس منضيفه لو حبيت تعمل حماية لاحقاً
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          user_id: userId,
          flags: {
            diabetes,
            obesity,
          },
          language, // "en" أو "ar"
          preferences: {
            diet_style: null,
            allergies: null,
            cuisine: null,
            liked_foods: likedFoods || null,
            disliked_foods: dislikedFoods || null,
          },
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail =
          typeof data === "string"
            ? data
            : data?.detail || "Failed to generate meal plan";
        throw new Error(detail);
      }

      setPlan(data);
    } catch (err: any) {
      console.error("AI meal plan error:", err);
      setError(err.message || "Error generating meal plan.");
      Alert.alert("Error", err.message || "Error generating meal plan.");
    } finally {
      setLoading(false);
    }
  };

  const renderTargetsCard = () => {
    if (!plan) return null;

    const t = plan.daily_targets;

    return (
      <Card style={styles.targetsCard}>
        <Card.Title
          title="Daily Targets"
          subtitle="Calories • Protein • Carbs • Fats • Water"
          left={(props) => (
            <Icon {...props} source="target" color={brand.blue[600]} />
          )}
        />
        <Card.Content>
          <View style={styles.targetsRow}>
            <View style={styles.targetBox}>
              <Text style={styles.targetLabel}>Calories</Text>
              <Text style={styles.targetValue}>
                {formatNumber(t.calories)} kcal
              </Text>
            </View>
            <View style={styles.targetBox}>
              <Text style={styles.targetLabel}>Protein</Text>
              <Text style={styles.targetValue}>
                {formatNumber(t.protein)} g
              </Text>
            </View>
            <View style={styles.targetBox}>
              <Text style={styles.targetLabel}>Carbs</Text>
              <Text style={styles.targetValue}>
                {formatNumber(t.carbs)} g
              </Text>
            </View>
          </View>

          <View style={styles.targetsRow}>
            <View style={styles.targetBox}>
              <Text style={styles.targetLabel}>Fats</Text>
              <Text style={styles.targetValue}>{formatNumber(t.fat)} g</Text>
            </View>
            <View style={styles.targetBox}>
              <Text style={styles.targetLabel}>Water</Text>
              <Text style={styles.targetValue}>
                {formatNumber(t.water_liters, 1)} L
              </Text>
            </View>
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderDayCard = (day: DayPlan, index: number) => {
    const m = day.macros;

    return (
      <Card
        key={`${day.day}-${index}`}
        style={[
          styles.dayCard,
          {
            // ممكن تضيف تدرّج ألوان خفيف لو حابب
          },
        ]}
      >
        <Card.Title
          title={`Day ${index + 1} – ${day.day}`}
          subtitle={`${formatNumber(m.calories)} kcal • ${formatNumber(
            m.protein
          )}g protein • ${formatNumber(m.carbs)}g carbs`}
          left={(props) => (
            <Icon {...props} source="food" color={brand.orange[600]} />
          )}
        />
        <Card.Content>
          <View style={styles.mealBlock}>
            <Text style={styles.mealTitle}>Breakfast</Text>
            <Text style={styles.mealText}>{day.breakfast}</Text>
          </View>

          <View style={styles.mealBlock}>
            <Text style={styles.mealTitle}>Lunch</Text>
            <Text style={styles.mealText}>{day.lunch}</Text>
          </View>

          <View style={styles.mealBlock}>
            <Text style={styles.mealTitle}>Dinner</Text>
            <Text style={styles.mealText}>{day.dinner}</Text>
          </View>

          <View style={styles.mealBlock}>
            <Text style={styles.mealTitle}>Snacks</Text>
            <Text style={styles.mealText}>{day.snacks}</Text>
          </View>

          {day.tips && day.tips.length > 0 && (
            <View style={styles.mealBlock}>
              <Text style={styles.mealTitle}>Daily Tips</Text>
              {day.tips.map((tip, i) => (
                <Text key={i} style={styles.tipText}>
                  • {tip}
                </Text>
              ))}
            </View>
          )}
        </Card.Content>
      </Card>
    );
  };

  return (
    <ScreenScaffold title="Meal Planning">
      <ScrollView
        contentContainerStyle={[
          styles.scrollContent,
          { backgroundColor: "#FFFFFF" }, // صفحة بيضا وواضحة
        ]}
      >
        {/* Header */}
        <Surface style={[styles.headerSurface, { backgroundColor: "#FFFFFF" }]}>
          <View>
            <Text variant="titleLarge" style={styles.headerTitle}>
              AI Meal Planning
            </Text>
            <Text style={styles.headerSubtitle}>
              Generate a personalized 7-day meal plan using your saved profile
              and health flags.
            </Text>
          </View>
          <Icon
            source="silverware-fork-knife"
            size={36}
            color={brand.orange[600]}
          />
        </Surface>

        {/* Health Flags */}
        <Card style={styles.flagsCard}>
          <Card.Title
            title="Health Flags"
            subtitle="These will influence carbs, portions and tips."
            left={(props) => (
              <Icon {...props} source="heart-pulse" color={brand.green[600]} />
            )}
          />
          <Card.Content>
            <View style={styles.flagRow}>
              <Text style={styles.flagLabel}>
                Diabetes / blood sugar issues
              </Text>
              <Switch
                value={diabetes}
                onValueChange={setDiabetes}
                color={brand.green[600]}
              />
            </View>
            <View style={styles.flagRow}>
              <Text style={styles.flagLabel}>Obesity / high body fat</Text>
              <Switch
                value={obesity}
                onValueChange={setObesity}
                color={brand.green[600]}
              />
            </View>
            <Text style={styles.infoText}>
              The AI uses these flags to adapt the meal plan. This is not a
              medical diagnosis. For medical advice, always consult your doctor.
            </Text>
          </Card.Content>
        </Card>

        {/* ✅ جديد: تفضيلات الأكل */}
        <Card style={styles.flagsCard}>
          <Card.Title
            title="Food Preferences"
            subtitle="Tell the AI what you like or want to avoid."
            left={(props) => (
              <Icon {...props} source="food-apple" color={brand.orange[600]} />
            )}
          />
          <Card.Content>
            <TextInput
              mode="outlined"
              label="Foods you like (e.g. chicken, rice, manoushe...)"
              value={likedFoods}
              onChangeText={setLikedFoods}
              style={{ marginBottom: 8 }}
              multiline
            />
            <TextInput
              mode="outlined"
              label="Foods you dislike / want to avoid"
              value={dislikedFoods}
              onChangeText={setDislikedFoods}
              style={{ marginBottom: 8 }}
              multiline
            />

            {/* ✅ جديد: اختيار اللغة */}
            <Text style={[styles.flagLabel, { marginTop: 4, marginBottom: 8 }]}>
              Plan language
            </Text>
            <View style={styles.languageRow}>
              <Button
                mode={language === "en" ? "contained" : "outlined"}
                onPress={() => setLanguage("en")}
                style={styles.languageButton}
              >
                English
              </Button>
              <Button
                mode={language === "ar" ? "contained" : "outlined"}
                onPress={() => setLanguage("ar")}
                style={styles.languageButton}
              >
                العربية
              </Button>
            </View>
          </Card.Content>
        </Card>

        {/* Generate Button */}
        <View style={styles.buttonWrapper}>
          <Button
            mode="contained"
            onPress={handleGenerate}
            disabled={loading}
            style={styles.generateButton}
            buttonColor={brand.orange[600]}
            textColor="#FFFFFF"
            icon="robot"
          >
            {loading ? "Generating..." : "Generate 7-Day Meal Plan"}
          </Button>
          {loading && (
            <View style={{ marginTop: 8 }}>
              <ActivityIndicator
                animating={true}
                color={brand.orange[600]}
              />
            </View>
          )}
          {error && <Text style={styles.errorText}>{error}</Text>}
        </View>

        {/* Daily Targets */}
        {renderTargetsCard()}

        {/* Week Plan */}
        {plan ? (
          <>
            <Text style={styles.sectionTitle}>Weekly Plan</Text>
            {plan.week.map((day, index) => renderDayCard(day, index))}
          </>
        ) : (
          <Card style={styles.emptyCard}>
            <Card.Content>
              <Text style={styles.infoText}>
                No plan yet. Set your health flags, add your food preferences,
                choose the language, and tap{" "}
                <Text style={{ fontWeight: "600" }}>
                  Generate 7-Day Meal Plan
                </Text>{" "}
                to create your AI plan.
              </Text>
            </Card.Content>
          </Card>
        )}
      </ScrollView>
    </ScreenScaffold>
  );
}

const styles = StyleSheet.create({
  scrollContent: {
    padding: 20,
    paddingBottom: 32,
  },
  headerSurface: {
    marginVertical: 16,
    padding: 20,
    borderRadius: 20,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#E5E7EB",
  },
  headerTitle: {
    fontWeight: "700",
    color: "#111827",
  },
  headerSubtitle: {
    marginTop: 4,
    color: "#6B7280",
    fontSize: 13,
  },
  flagsCard: {
    borderRadius: 18,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    backgroundColor: "#F9FAFB",
    marginBottom: 16,
  },
  flagRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  flagLabel: {
    fontSize: 14,
    color: "#111827",
    flex: 1,
    marginRight: 8,
  },
  infoText: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 6,
  },
  buttonWrapper: {
    marginBottom: 16,
    alignItems: "center",
  },
  generateButton: {
    borderRadius: 999,
    width: "100%",
  },
  errorText: {
    marginTop: 6,
    fontSize: 12,
    color: "#DC2626",
    textAlign: "center",
  },
  targetsCard: {
    borderRadius: 18,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    backgroundColor: "#FFFFFF",
    marginBottom: 16,
  },
  targetsRow: {
    flexDirection: "row",
    marginTop: 8,
  },
  targetBox: {
    flex: 1,
    paddingVertical: 6,
    paddingRight: 8,
  },
  targetLabel: {
    fontSize: 11,
    color: "#6B7280",
  },
  targetValue: {
    fontSize: 14,
    fontWeight: "600",
    color: "#111827",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#111827",
    marginBottom: 8,
    marginTop: 4,
  },
  dayCard: {
    borderRadius: 18,
    borderWidth: 1.2,
    backgroundColor: "#FFFFFF",
    marginBottom: 14,
  },
  mealBlock: {
    marginTop: 6,
  },
  mealTitle: {
    fontSize: 13,
    fontWeight: "600",
    color: "#111827",
    marginBottom: 2,
  },
  mealText: {
    fontSize: 12,
    color: "#4B5563",
  },
  tipText: {
    fontSize: 11,
    color: "#16A34A",
    marginTop: 2,
  },
  emptyCard: {
    borderRadius: 18,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    backgroundColor: "#F9FAFB",
    marginBottom: 20,
  },
  languageRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 8,
  },
  languageButton: {
    flex: 1,
  },
});

