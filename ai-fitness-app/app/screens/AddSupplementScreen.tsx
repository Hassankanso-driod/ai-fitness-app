/**
 * AddSupplementScreen.tsx - Add New Supplement
 * 
 * This screen allows admin to add a new supplement with an image.
 * 
 * How it works:
 * 1. User fills in name, description, and price
 * 2. User selects an image from gallery or camera
 * 3. When submitting, we create FormData with all fields
 * 4. Backend receives multipart/form-data and saves image as file
 * 5. Backend stores only the filename in database
 * 
 * Image Upload:
 * - Uses FormData (multipart/form-data) instead of base64
 * - Image is sent as a file, not as base64 string
 * - Much more efficient and no size limits
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

export default function AddSupplementScreen({ navigation }: any) {
  const theme = useTheme();
  
  // Form state - stores user input
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [imageUri, setImageUri] = useState<string | null>(null); // Local image URI for preview
  const [loading, setLoading] = useState(false);

  /**
   * pickImageFromGallery - Opens gallery to select an image
   */
  const pickImageFromGallery = async () => {
    try {
      // Request permission
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission Required", "Please grant access to your photos.");
        return;
      }

      // Open image picker
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setImageUri(result.assets[0].uri);
        Alert.alert("Image Selected ✅", "Image ready to upload!");
      }
    } catch (error: any) {
      Alert.alert("Error", `Failed to open gallery: ${error.message}`);
    }
  };

  /**
   * takePhotoWithCamera - Opens camera to take a photo
   */
  const takePhotoWithCamera = async () => {
    try {
      // Request permission
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission Required", "Please grant camera access.");
        return;
      }

      // Open camera
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setImageUri(result.assets[0].uri);
        Alert.alert("Photo Taken ✅", "Image ready to upload!");
      }
    } catch (error: any) {
      Alert.alert("Error", `Failed to open camera: ${error.message}`);
    }
  };

  /**
   * showImagePickerOptions - Shows dialog to choose camera or gallery
   */
  const showImagePickerOptions = () => {
    Alert.alert(
      "Select Image",
      "Choose how you want to add an image",
      [
        { text: "Cancel", style: "cancel" },
        { text: "📷 Take Photo", onPress: takePhotoWithCamera },
        { text: "🖼️ Choose from Gallery", onPress: pickImageFromGallery },
      ]
    );
  };

  /**
   * handleSubmit - Submits the supplement form with image
   * 
   * This function:
   * 1. Validates all required fields
   * 2. Creates FormData object
   * 3. Appends name, description, price as form fields
   * 4. Appends image as a file (if selected)
   * 5. Sends multipart/form-data to backend
   * 6. Backend saves image file and stores filename in database
   */
  const handleSubmit = async () => {
    // Validate required fields
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
      // Create FormData object for multipart/form-data
      const formData = new FormData();
      
      // Append text fields
      formData.append("name", name.trim());
      formData.append("description", description.trim());
      formData.append("price", priceNum.toString());

      // Append image file if selected
      if (imageUri) {
        // Get filename from URI
        const filename = imageUri.split("/").pop() || "image.jpg";
        const match = /\.(\w+)$/.exec(filename);
        const type = match ? `image/${match[1]}` : "image/jpeg";

        // Append image as file
        formData.append("image", {
          uri: imageUri,
          name: filename,
          type: type,
        } as any);
      }

      // Send to backend
      const response = await fetch(`${BASE_URL}/supplements`, {
        method: "POST",
        headers: {
          "Content-Type": "multipart/form-data", // Important: tells backend it's a file upload
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        Alert.alert("Success ✅", "Supplement added successfully!", [
          { text: "OK", onPress: () => navigation.goBack() },
        ]);
      } else {
        Alert.alert("Error ❌", data.detail || "Failed to add supplement.");
      }
    } catch (error: any) {
      console.error("Submit error:", error);
      Alert.alert("Connection Error", "Cannot connect to server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenScaffold title="Add Supplement 💊">
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
            Add New Product
          </Text>

          <Card style={{ padding: 16, backgroundColor: theme.colors.surface, marginBottom: 16 }}>
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
              label="Price ($)"
              mode="outlined"
              keyboardType="decimal-pad"
              value={price}
              onChangeText={setPrice}
              style={{ marginBottom: 12 }}
            />

            {/* Image Preview */}
            {imageUri && (
              <View style={{ marginBottom: 12, alignItems: "center" }}>
                <Image
                  source={{ uri: imageUri }}
                  style={{
                    width: "100%",
                    height: 200,
                    borderRadius: 10,
                    backgroundColor: theme.colors.surfaceVariant,
                  }}
                  resizeMode="cover"
                />
                <Text style={{ fontSize: 11, color: theme.colors.onSurfaceVariant, marginTop: 4 }}>
                  Preview - Image will be uploaded when you save
                </Text>
              </View>
            )}

            {/* Image Selection Button */}
            <Button
              mode={imageUri ? "outlined" : "contained"}
              icon="camera"
              onPress={showImagePickerOptions}
              style={{ marginBottom: 12 }}
              buttonColor={imageUri ? undefined : brand.blue[600]}
            >
              {imageUri ? "Change Image" : "Add Image"}
            </Button>

            {/* Submit Button */}
            <Button
              mode="contained"
              buttonColor={brand.green[600]}
              textColor="#fff"
              onPress={handleSubmit}
              loading={loading}
              disabled={loading}
              style={{ borderRadius: 12 }}
            >
              Add Supplement
            </Button>
          </Card>

          <Button
            mode="text"
            onPress={() => navigation.goBack()}
            textColor={brand.blue[600]}
          >
            ← Back to Store
          </Button>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenScaffold>
  );
}

