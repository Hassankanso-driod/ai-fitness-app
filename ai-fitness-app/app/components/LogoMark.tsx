import React from "react";
import { View } from "react-native";
import { Text, Icon } from "react-native-paper";
import { brand } from "../utils/themeManager";

export default function LogoMark() {
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
      <Icon source="circle" size={10} color={brand.blue[600]} />
      <Icon source="circle" size={10} color={brand.green[600]} />
      <Icon source="circle" size={10} color={brand.orange[600]} />
      <Text style={{ fontWeight: "700", marginLeft: 6 }}>AI Fitness</Text>
    </View>
  );
}
