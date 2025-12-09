import React from "react";
import { View } from "react-native";
import { Button, Text, Surface } from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager"; // ✅ make sure path is correct

export default function AccountCreatedScreen({ route, navigation }: any) {
  const { firstName = "User" } = route?.params ?? {};

  return (
    <ScreenScaffold title="Account Created">
      <View
        style={{
          flex: 1,
          justifyContent: "center",
          alignItems: "center",
          padding: 24,
          backgroundColor: "#FFFFFF",
        }}
      >
        <Surface
          style={{
            borderRadius: 20,
            padding: 28,
            alignItems: "center",
            backgroundColor: brand.blue[50],
            elevation: 3,
            shadowColor: "#000",
            shadowOpacity: 0.1,
            shadowRadius: 6,
            width: "100%",
          }}
        >
          <Text
            variant="headlineMedium"
            style={{
              fontWeight: "800",
              
              marginBottom: 8,
              textAlign: "center",
              letterSpacing: 0.3,
            }}
          >
            Congratulations, {firstName}! 
          </Text>

          <Text
            style={{
              color: "#374151",
              fontSize: 16,
              textAlign: "center",
              marginBottom: 14,
              opacity: 0.9,
              lineHeight: 22,
            }}
          >
            You’ve just taken the first step toward a stronger, healthier version of
            yourself. Every rep, every meal, every sip of water brings you closer to your
            goal.
          </Text>

          

          <Button
            mode="contained"
            buttonColor={brand.blue[600]}
            textColor="#fff"
            style={{
              borderRadius: 14,
              paddingVertical: 8,
              width: "80%",
              marginTop: 6,
            }}
            labelStyle={{ fontWeight: "600", fontSize: 16, letterSpacing: 0.5 }}
            onPress={() => navigation.replace("Tabs", route.params)}
          >
            Start Your Journey 
          </Button>
        </Surface>

        <Text
          style={{
            marginTop: 32,
            fontSize: 14,
            color: "#6B7280",
            textAlign: "center",
            fontStyle: "italic",
            lineHeight: 20,
            paddingHorizontal: 12,
          }}
        >
          “Success doesn’t come from what you do occasionally — it comes from what you do
          consistently. Let’s make every day count.”
        </Text>
      </View>
    </ScreenScaffold>
  );
}
