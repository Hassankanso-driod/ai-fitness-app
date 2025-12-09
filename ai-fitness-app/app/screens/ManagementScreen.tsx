import React, { useEffect, useState } from "react";
import { View, ScrollView, Alert, RefreshControl, Image } from "react-native";
import { Card, Text, Button, ActivityIndicator, IconButton, Surface, SegmentedButtons } from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import { brand } from "../utils/themeManager";
import { BASE_URL } from "../config";

export default function ManagementScreen({ navigation, route }: any) {
  const [activeTab, setActiveTab] = useState("users");
  const [users, setUsers] = useState<any[]>([]);
  const [supplements, setSupplements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch all users from backend
  const fetchUsers = async () => {
    try {
      const res = await fetch(`${BASE_URL}/admin/users`);
      const data = await res.json();
      if (res.ok) setUsers(data);
      else Alert.alert("Error", data.detail || "Failed to fetch users");
    } catch (err) {
      console.error(err);
      Alert.alert("Connection Error", "Cannot reach backend 😢");
    }
  };

  // Fetch all supplements
  const fetchSupplements = async () => {
    try {
      const res = await fetch(`${BASE_URL}/supplements`);
      const data = await res.json();
      if (res.ok) {
        setSupplements(data);
      } else {
        Alert.alert("Error", data.detail || "Failed to fetch supplements");
      }
    } catch (error) {
      console.error(error);
      Alert.alert("Error", "Failed to connect to the backend 😢");
    }
  };

  const loadData = async () => {
    setLoading(true);
    await Promise.all([fetchUsers(), fetchSupplements()]);
    setLoading(false);
    setRefreshing(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  // Activate or deactivate user
  const toggleUser = async (id: number, active: boolean) => {
    try {
      const res = await fetch(`${BASE_URL}/admin/user/${id}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active: !active }),
      });
      const data = await res.json();
      if (res.ok) {
        Alert.alert("Success ✅", data.message);
        fetchUsers();
      } else Alert.alert("Error ❌", data.detail);
    } catch (err) {
      console.error(err);
      Alert.alert("Connection Error", "Failed to update status");
    }
  };

  // Delete supplement
  const handleDeleteSupplement = async (id: number) => {
    Alert.alert("Confirm Delete", "Delete this supplement permanently?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          try {
            const res = await fetch(`${BASE_URL}/supplements/${id}`, {
              method: "DELETE",
            });
            const data = await res.json();
            if (res.ok) {
              Alert.alert("Deleted ✅", data.message || "Supplement removed");
              fetchSupplements();
            } else {
              Alert.alert("Error ❌", data.detail || "Delete failed");
            }
          } catch (err) {
            console.error(err);
            Alert.alert("Error", "Failed to reach backend 😢");
          }
        },
      },
    ]);
  };

  return (
    <ScreenScaffold title="Admin Management 🛠️">
      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        contentContainerStyle={{ padding: 16 }}
      >
        {/* Tab Selector */}
        <SegmentedButtons
          value={activeTab}
          onValueChange={setActiveTab}
          buttons={[
            {
              value: "users",
              label: "Users 👥",
              icon: "account-group",
            },
            {
              value: "supplements",
              label: "Supplements 💊",
              icon: "bottle-soda",
            },
          ]}
          style={{ marginBottom: 20 }}
        />

        {/* Users Tab */}
        {activeTab === "users" && (
          <>
            <Surface
              style={{
                padding: 16,
                borderRadius: 16,
                backgroundColor: brand.blue[50],
                marginBottom: 16,
              }}
            >
              <Text style={{ fontWeight: "700", fontSize: 18, color: brand.blue[700] }}>
                User Management
              </Text>
              <Text style={{ color: "#555", marginTop: 4 }}>
                View and control user login access. Users deactivate automatically every 30 days.
              </Text>
            </Surface>

            {loading ? (
              <View style={{ alignItems: "center", marginTop: 40 }}>
                <ActivityIndicator size="large" color={brand.blue[600]} />
                <Text style={{ marginTop: 10 }}>Loading users...</Text>
              </View>
            ) : users.length === 0 ? (
              <View style={{ alignItems: "center", marginTop: 40 }}>
                <Text style={{ textAlign: "center" }}>No users found 😔</Text>
              </View>
            ) : (
              users.map((user) => (
                <Card
                  key={user.id}
                  style={{
                    marginBottom: 14,
                    borderRadius: 16,
                    backgroundColor: user.active ? "#E8F5E9" : "#FFEBEE",
                    borderLeftWidth: 5,
                    borderLeftColor: user.active ? brand.green[600] : brand.orange[600],
                    elevation: 2,
                  }}
                >
                  <Card.Title
                    title={user.first_name || user.username || "Unknown User"}
                    subtitle={`Joined: ${new Date(user.created_at).toLocaleDateString()} | Status: ${user.active ? "Active" : "Inactive"}`}
                    left={(props) => (
                      <IconButton {...props} icon="account-circle" iconColor={user.active ? brand.green[600] : brand.orange[600]} />
                    )}
                  />
                  <Card.Content>
                    <Text style={{ color: "#666", fontSize: 12 }}>
                      Email: {user.email || "N/A"}
                    </Text>
                  </Card.Content>
                  <Card.Actions style={{ justifyContent: "flex-end" }}>
                    <Button
                      mode="contained"
                      buttonColor={user.active ? brand.orange[600] : brand.green[600]}
                      textColor="#fff"
                      onPress={() => toggleUser(user.id, user.active)}
                      style={{ borderRadius: 12 }}
                      icon={user.active ? "account-off" : "account-check"}
                    >
                      {user.active ? "Deactivate" : "Activate"}
                    </Button>
                  </Card.Actions>
                </Card>
              ))
            )}
          </>
        )}

        {/* Supplements Tab */}
        {activeTab === "supplements" && (
          <>
            <Surface
              style={{
                padding: 16,
                borderRadius: 16,
                backgroundColor: brand.orange[50],
                marginBottom: 16,
              }}
            >
              <Text style={{ fontWeight: "700", fontSize: 18, color: brand.orange[700] }}>
                Supplement Management
              </Text>
              <Text style={{ color: "#555", marginTop: 4 }}>
                Add, edit, or delete supplements from your store.
              </Text>
            </Surface>

            <View style={{ marginBottom: 16 }}>
              <Button
                mode="contained"
                buttonColor={brand.green[600]}
                textColor="#fff"
                icon="plus"
                onPress={() => navigation.navigate("AddSupplement")}
                style={{ borderRadius: 12 }}
              >
                Add New Supplement
              </Button>
            </View>

            {loading ? (
              <View style={{ alignItems: "center", marginTop: 40 }}>
                <ActivityIndicator size="large" color={brand.orange[600]} />
                <Text style={{ marginTop: 10 }}>Loading supplements...</Text>
              </View>
            ) : supplements.length === 0 ? (
              <View style={{ alignItems: "center", marginTop: 40 }}>
                <Text style={{ textAlign: "center" }}>No supplements found 😔</Text>
              </View>
            ) : (
              supplements.map((item) => (
                <Card
                  key={item.id}
                  style={{
                    marginBottom: 14,
                    borderRadius: 16,
                    backgroundColor: "#fff",
                    borderLeftWidth: 5,
                    borderLeftColor: brand.orange[600],
                    elevation: 3,
                  }}
                >
                  <View style={{ flexDirection: "row" }}>
                    {item.image_url && (
                      <Image
                        source={{
                          uri: item.image_url?.startsWith("http")
                            ? item.image_url
                            : `${BASE_URL}${item.image_url || ""}`,
                        }}
                        style={{
                          width: 100,
                          height: 100,
                          borderTopLeftRadius: 16,
                          borderBottomLeftRadius: 16,
                          resizeMode: "cover",
                        }}
                      />
                    )}
                    <View style={{ flex: 1, padding: 12 }}>
                      <Text style={{ fontWeight: "700", fontSize: 16, marginBottom: 4 }}>
                        {item.name}
                      </Text>
                      <Text
                        numberOfLines={2}
                        style={{ color: "#666", fontSize: 12, marginBottom: 8 }}
                      >
                        {item.description}
                      </Text>
                      <Text style={{ fontWeight: "bold", color: brand.green[700], fontSize: 16 }}>
                        ${Number(item.price).toFixed(2)}
                      </Text>
                    </View>
                  </View>
                  <Card.Actions style={{ justifyContent: "flex-end" }}>
                    <Button
                      mode="outlined"
                      icon="pencil"
                      onPress={() =>
                        navigation.navigate("EditSupplement", {
                          supplement: item,
                        })
                      }
                      style={{ marginRight: 8 }}
                    >
                      Edit
                    </Button>
                    <Button
                      mode="outlined"
                      icon="delete"
                      textColor="red"
                      onPress={() => handleDeleteSupplement(item.id)}
                    >
                      Delete
                    </Button>
                  </Card.Actions>
                </Card>
              ))
            )}
          </>
        )}
      </ScrollView>
    </ScreenScaffold>
  );
}
