import React from "react";
import { View, Image } from "react-native";
import { Card, Text, Button } from "react-native-paper";
import { brand } from "../utils/themeManager";

export default function SupplementCard({ item, onPress }: any) {
  return (
    <Card
      style={{
        borderRadius: 18,
        borderWidth: 1,
        borderColor: "#E5E7EB",
        marginBottom: 16,
        overflow: "hidden",
        backgroundColor: "#FFFFFF",
      }}
      onPress={onPress}
    >
      {/* Thumbnail */}
      <Image
        source={{ uri: item.image }}
        style={{ width: "100%", height: 160 }}
        resizeMode="cover"
      />

      <Card.Content style={{ paddingVertical: 12 }}>
        <Text variant="titleMedium" style={{ fontWeight: "700", color: "#111827" }}>
          {item.name}
        </Text>
        <Text style={{ color: "#6B7280", fontSize: 14, marginTop: 4 }}>
          {item.description}
        </Text>
        <View style={{ flexDirection: "row", alignItems: "center", marginTop: 10 }}>
          <Text style={{  fontWeight: "700", fontSize: 16 }}>
            ${item.price}
          </Text>
        </View>
      </Card.Content>

      <Card.Actions style={{ justifyContent: "flex-end", paddingHorizontal: 16 }}>
        <Button
          mode="contained"
          buttonColor={brand.blue[600]}
          textColor="#fff"
          onPress={onPress}
          style={{ borderRadius: 10 }}
        >
          View
        </Button>
      </Card.Actions>
    </Card>
  );
}
