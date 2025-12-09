import React from "react";
import { View } from "react-native";

export default function HeaderRing({ color }: { color: string }) {
  return (
    <View style={{ alignItems: "center", marginRight: 8 }}>
      <View
        style={{
          width: 28,
          height: 28,
          borderRadius: 14,
          borderWidth: 3,
          borderColor: color,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <View
          style={{
            width: 14,
            height: 14,
            borderRadius: 7,
            backgroundColor: "#fff",
          }}
        />
      </View>
    </View>
  );
}
