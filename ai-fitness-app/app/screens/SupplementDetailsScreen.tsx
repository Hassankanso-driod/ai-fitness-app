/**
 * SupplementDetailsScreen - Shows detailed information about a supplement
 * This screen displays all the details of a selected supplement including
 * image, name, description, and price.
 */

import React from "react";
import { ScrollView, View, Image, StyleSheet, Alert } from "react-native";
import { Card, Text, Button, Surface, Icon } from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import { BASE_URL } from "../config";

export default function SupplementDetailsScreen({ route, navigation }: any) {
  // Get the supplement item from navigation params
  const { item, role } = route?.params ?? {};

  // If no item provided, show error and go back
  if (!item) {
    Alert.alert("Error", "No supplement information available");
    navigation.goBack();
    return null;
  }

  // Format the image URL
  // Backend stores only filename (e.g., "abc123.jpg")
  // Construct full URL: http://server:8000/uploads/filename.jpg
  const imageUrl = item.image_url
    ? `${BASE_URL}/uploads/${item.image_url}`
    : "https://via.placeholder.com/400x300?text=No+Image";

  return (
    <ScreenScaffold title="Supplement Details">
      <ScrollView contentContainerStyle={styles.container}>
        {/* Image Section */}
        <Card style={styles.imageCard}>
          <Image
            source={{ uri: imageUrl }}
            style={styles.image}
            resizeMode="cover"
          />
        </Card>

        {/* Details Section */}
        <Surface style={styles.detailsCard}>
          <Text variant="headlineSmall" style={styles.title}>
            {item.name}
          </Text>

          <View style={styles.priceContainer}>
            <Icon source="currency-usd" size={24} color={brand.green[600]} />
            <Text variant="headlineMedium" style={styles.price}>
              ${Number(item.price).toFixed(2)}
            </Text>
          </View>

          <View style={styles.divider} />

          <Text variant="titleMedium" style={styles.sectionTitle}>
            Description
          </Text>
          <Text style={styles.description}>{item.description || "No description available."}</Text>

          {/* Admin Actions */}
          {role === "admin" && (
            <>
              <View style={styles.divider} />
              <View style={styles.adminActions}>
                <Button
                  mode="contained"
                  buttonColor={brand.blue[600]}
                  icon="pencil"
                  onPress={() =>
                    navigation.navigate("EditSupplement", {
                      supplement: item,
                    })
                  }
                  style={styles.actionButton}
                >
                  Edit Supplement
                </Button>
              </View>
            </>
          )}

          {/* User Actions */}
          {role === "user" && (
            <>
              <View style={styles.divider} />
              <Button
                mode="contained"
                buttonColor={brand.green[600]}
                icon="cart"
                onPress={() =>
                  Alert.alert("Added to Cart", `${item.name} has been added to your cart!`)
                }
                style={styles.actionButton}
              >
                Add to Cart
              </Button>
            </>
          )}
        </Surface>
      </ScrollView>
    </ScreenScaffold>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: "#F9FAFB",
  },
  imageCard: {
    borderRadius: 20,
    overflow: "hidden",
    marginBottom: 16,
    elevation: 4,
  },
  image: {
    width: "100%",
    height: 300,
    backgroundColor: "#E5E7EB",
  },
  detailsCard: {
    borderRadius: 20,
    padding: 20,
    backgroundColor: "#FFFFFF",
    elevation: 2,
  },
  title: {
    fontWeight: "700",
    color: "#111827",
    marginBottom: 12,
  },
  priceContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
  },
  price: {
    fontWeight: "700",
    color: brand.green[600],
    marginLeft: 8,
  },
  divider: {
    height: 1,
    backgroundColor: "#E5E7EB",
    marginVertical: 16,
  },
  sectionTitle: {
    fontWeight: "600",
    color: brand.blue[700],
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
    color: "#4B5563",
    marginBottom: 8,
  },
  adminActions: {
    gap: 12,
  },
  actionButton: {
    borderRadius: 12,
    marginTop: 8,
  },
});

