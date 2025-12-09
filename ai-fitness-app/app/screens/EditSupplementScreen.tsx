/**
 * EditSupplementScreen.tsx - Edit Existing Supplement
 *
 * - Edit name, description, price
 * - Optional: change image (gallery or camera)
 * - Sends multipart/form-data to FastAPI backend
 */

import React, { useState } from "react";
import {
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  View,
  Image,
} from "react-native";
import { TextInput, Button, Text, Card, useTheme } from "react-native-paper";
import * as ImagePicker from "expo-image-picker";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import { BASE_URL } from "../config";

export default function EditSupplementScreen({ route, navigation }: any) {
  const theme = useTheme();
  const { supplement } = route.params;

  // Form state - initialized with existing supplement data
  const [name, setName] = useState(supplement.name);
  const [description, setDescription] = useState(supplement.description);
  const [price, setPrice] = useState(String(supplement.price));
  const [newImageUri, setNewImageUri] = useState<string | null>(null); // New image if user selects one
  const [loading, setLoading] = useState(false);

  // Existing image URL
  const existingImageUrl = supplement.image_url
    ? `${BASE_URL}/uploads/${supplement.image_url}`
    : null;

  // ------------ Image Pickers ------------

  const pickImageFromGallery = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission Required", "Please grant access to your photos.");
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setNewImageUri(result.assets[0].uri);
        Alert.alert("Image Selected ✅", "New image will replace the current one.");
      }
    } catch (error: any) {
      Alert.alert("Error", `Failed to open gallery: ${error.message}`);
    }
  };

  const takePhotoWithCamera = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission Required", "Please grant camera access.");
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setNewImageUri(result.assets[0].uri);
        Alert.alert("Photo Taken ✅", "New image will replace the current one.");
      }
    } catch (error: any) {
      Alert.alert("Error", `Failed to open camera: ${error.message}`);
    }
  };

  // ------------ Update Handler ------------

  const handleUpdate = async () => {
    if (!name.trim() || !description.trim() || !price.trim()) {
      Alert.alert("Missing Fields", "Please fill in all fields.");
      return;
    }

    const priceNum = parseFloat(price);
    if (isNaN(priceNum) || priceNum <= 0) {
      Alert.alert("Invalid Price", "Please enter a valid price.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();

      formData.append("name", name.trim());
      formData.append("description", description.trim());
      formData.append("price", priceNum.toString());

      if (newImageUri) {
        const filename = newImageUri.split("/").pop() || "image.jpg";
        const match = /\.(\w+)$/.exec(filename);
        const type = match ? `image/${match[1]}` : "image/jpeg";

        formData.append("image", {
          uri: newImageUri,
          name: filename,
          type,
        } as any);
      }

      // ❗ مهم: ما منحط Content-Type هون
      const response = await fetch(`${BASE_URL}/supplements/${supplement.id}`, {
        method: "PUT",
        body: formData,
      });

      // جرّب أول شي تقرا النص إذا في error
      let data: any = {};
      try {
        data = await response.json();
      } catch {
        // ignore parse error
      }

      if (response.ok) {
        Alert.alert("Success ✅", "Supplement updated successfully!", [
          { text: "OK", onPress: () => navigation.goBack() },
        ]);
      } else {
        console.log("Update error status:", response.status, data);
        Alert.alert("Error ❌", data?.detail || `Failed to update supplement (code ${response.status}).`);
      }
    } catch (error: any) {
      console.error("Update error:", error);
      Alert.alert("Connection Error", "Cannot connect to server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ------------ UI ------------

  return (
    <ScreenScaffold title="Edit Supplement ✏️">
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          contentContainerStyle={{
            padding: 20,
            backgroundColor: theme.colors.background,
          }}
        >
          <Text
            style={{
              fontSize: 24,
              fontWeight: "700",
              marginBottom: 20,
              color: theme.colors.onBackground,
              textAlign: "center",
            }}
          >
            Edit Product
          </Text>

          <Card
            style={{
              padding: 16,
              backgroundColor: theme.colors.surface,
              marginBottom: 16,
            }}
          >
            {/* Name Input */}
            <TextInput
              label="Name"
              mode="outlined"
              value={name}
              onChangeText={setName}
              style={{ marginBottom: 12 }}
            />

            {/* Description Input */}
            <TextInput
              label="Description"
              mode="outlined"
              multiline
              numberOfLines={4}
              value={description}
              onChangeText={setDescription}
              style={{ marginBottom: 12 }}
            />

            {/* Price Input */}
            <TextInput
              label="Price"
              mode="outlined"
              keyboardType="numeric"
              value={price}
              onChangeText={setPrice}
              style={{ marginBottom: 12 }}
            />
          </Card>

          {/* Image Section */}
          <Card
            style={{
              padding: 16,
              backgroundColor: theme.colors.surface,
              marginBottom: 16,
            }}
          >
            <Text
              style={{
                fontSize: 16,
                fontWeight: "600",
                marginBottom: 12,
                color: theme.colors.onSurface,
              }}
            >
              Product Image
            </Text>

            <View style={{ alignItems: "center", marginBottom: 12 }}>
              {newImageUri ? (
                <Image
                  source={{ uri: newImageUri }}
                  style={{ width: 180, height: 180, borderRadius: 12 }}
                  resizeMode="cover"
                />
              ) : existingImageUrl ? (
                <Image
                  source={{ uri: existingImageUrl }}
                  style={{ width: 180, height: 180, borderRadius: 12 }}
                  resizeMode="cover"
                />
              ) : (
                <View
                  style={{
                    width: 180,
                    height: 180,
                    borderRadius: 12,
                    borderWidth: 1,
                    borderColor: "#ccc",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Text>No image</Text>
                </View>
              )}
            </View>

            <Button
              mode="outlined"
              onPress={pickImageFromGallery}
              style={{ marginBottom: 8 }}
            >
              Choose from Gallery
            </Button>
            <Button mode="outlined" onPress={takePhotoWithCamera}>
              Take Photo
            </Button>
          </Card>

          {/* Save Button */}
          <Button
            mode="contained"
            onPress={handleUpdate}
            loading={loading}
            disabled={loading}
            style={{ marginBottom: 24, backgroundColor: brand.blue[600] }}
          >
            Save Changes
          </Button>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenScaffold>
  );
}
