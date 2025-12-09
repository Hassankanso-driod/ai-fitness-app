import React, { useEffect, useState } from "react";
import {
  ScrollView,
  View,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from "react-native";
import {
  Text,
  Button,
  Searchbar,
  Chip,
  useTheme,
} from "react-native-paper";
import ScreenScaffold from "../components/ScreenScaffold";
import ProductCard from "../components/ProductCard";
import SurfaceCard from "../components/SurfaceCard";
import { brand } from "../utils/themeManager";
import { layoutStyles, buttonStyles, textStyles } from "../styles/globalStyles";
import { BASE_URL } from "../config";

export default function SupplementsScreen({ navigation, route }: any) {
  const theme = useTheme(); // Get theme for dark mode support
  const [supplements, setSupplements] = useState<any[]>([]);
  const [filteredSupplements, setFilteredSupplements] = useState<any[]>([]);
  const [favorites, setFavorites] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const role = route?.params?.role || "user";
  const userId = route?.params?.userId;

  // 🧠 Fetch all supplements
  const fetchSupplements = async () => {
    try {
      setLoading(true);
      console.log("Fetching supplements from:", `${BASE_URL}/supplements`);
      const res = await fetch(`${BASE_URL}/supplements`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        console.error("API Error:", res.status, errorText);
        try {
          const errorData = JSON.parse(errorText);
          Alert.alert("Error", errorData.detail || "Failed to fetch supplements");
        } catch {
          Alert.alert("Error", `Server error: ${res.status}`);
        }
        setSupplements([]);
        return;
      }
      
      const data = await res.json();
      setSupplements(data || []);
    } catch (error: any) {
      console.error("Network error:", error);
      Alert.alert(
        "Connection Error", 
        `Cannot connect to backend at ${BASE_URL}\n\nPlease check:\n- Backend server is running\n- IP address is correct\n- Phone and computer are on same network`,
        [{ text: "OK" }]
      );
      setSupplements([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSupplements();
  }, []);

  useEffect(() => {
    if (userId) {
      fetchFavorites();
    }
  }, [userId]);

  useEffect(() => {
    filterAndSortSupplements();
  }, [supplements, searchQuery, sortBy, showFavoritesOnly, favorites]);

  const fetchFavorites = async () => {
    if (!userId) return;
    
    try {
      const res = await fetch(`${BASE_URL}/favorites/${userId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      if (!res.ok) {
        // If response is not ok, set empty favorites and return
        setFavorites([]);
        return;
      }
      
      const data = await res.json();
      
      // Handle various response formats and null cases
      if (!data) {
        setFavorites([]);
        return;
      }
      
      // If data is an array, process it safely
      if (Array.isArray(data)) {
        const favoriteIds: number[] = [];
        for (const item of data) {
          // Safely check each item before accessing properties
          if (item != null && typeof item === 'object' && 'supplement_id' in item) {
            const supplementId = item.supplement_id;
            if (supplementId != null) {
              favoriteIds.push(supplementId);
            }
          }
        }
        setFavorites(favoriteIds);
      } else {
        // If response is not an array, set empty favorites
        setFavorites([]);
      }
    } catch (err) {
      console.error("Error fetching favorites:", err);
      // Set empty favorites on error to prevent UI issues
      setFavorites([]);
      // Don't show alert for favorites - it's not critical
    }
  };

  const filterAndSortSupplements = () => {
    let filtered = [...supplements];
    
    // Favorites filter - show only favorited items
    if (showFavoritesOnly && userId) {
      filtered = filtered.filter((item) => favorites.includes(item.id));
    }
    
    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (item) =>
          item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Sort
    filtered.sort((a, b) => {
      if (sortBy === "name") return a.name.localeCompare(b.name);
      if (sortBy === "price-low") return a.price - b.price;
      if (sortBy === "price-high") return b.price - a.price;
      return 0;
    });
    
    setFilteredSupplements(filtered);
  };

  const toggleFavorite = async (supplementId: number) => {
    if (!userId) {
      Alert.alert("Login Required", "Please login to add favorites");
      return;
    }

    const isFavorite = favorites.includes(supplementId);
    
    try {
      if (isFavorite) {
        // Find favorite ID and remove
        const res = await fetch(`${BASE_URL}/favorites/${userId}`);
        if (res.ok) {
          const data = await res.json();
          // Safely find favorite with null check
          const fav = Array.isArray(data)
            ? data.find((f: any) => f != null && f.supplement_id === supplementId)
            : null;
          if (fav) {
            await fetch(`${BASE_URL}/favorites/${fav.id}`, { method: "DELETE" });
          }
        }
        setFavorites(favorites.filter((id) => id !== supplementId));
      } else {
        await fetch(`${BASE_URL}/favorites/${userId}/${supplementId}`, { method: "POST" });
        setFavorites([...favorites, supplementId]);
      }
    } catch (err) {
      Alert.alert("Error", "Failed to update favorite");
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchSupplements();
  };


  return (
    <ScreenScaffold title="Supplements Store 💪">
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={[
          layoutStyles.container,
          { backgroundColor: theme.colors.background }
        ]}
      >
        {/* 🧩 Professional Header */}
        <SurfaceCard
          title="Fuel Your Fitness 💪"
          subtitle="Premium supplements for peak performance"
          icon="bottle-soda"
          color="blue"
        />

        {/* 🔄 Loading State */}
        {loading && (
          <View style={{ alignItems: "center", marginTop: 60 }}>
            <ActivityIndicator size="large" color={brand.green[600]} />
            <Text style={{ marginTop: 10 }}>Loading products...</Text>
          </View>
        )}

        {/* Search and Filter */}
        <View style={{ marginBottom: 16 }}>
          <Searchbar
            placeholder="Search supplements..."
            onChangeText={setSearchQuery}
            value={searchQuery}
            style={{ marginBottom: 12 }}
          />
          
          {/* Favorites Filter Button */}
          {userId && (
            <Button
              mode={showFavoritesOnly ? "contained" : "outlined"}
              icon="heart"
              onPress={() => setShowFavoritesOnly(!showFavoritesOnly)}
              buttonColor={showFavoritesOnly ? brand.green[600] : undefined}
              textColor={showFavoritesOnly ? "#fff" : brand.green[700]}
              style={[buttonStyles.primary, { marginBottom: 12 }]}
            >
              {showFavoritesOnly ? "Show All" : "Show Favorites Only"}
            </Button>
          )}
          
          {/* Sort Options */}
          <View style={{ flexDirection: "row", gap: 8, flexWrap: "wrap" }}>
            <Chip
              selected={sortBy === "name"}
              onPress={() => setSortBy("name")}
              style={{ marginRight: 4 }}
            >
              Name
            </Chip>
            <Chip
              selected={sortBy === "price-low"}
              onPress={() => setSortBy("price-low")}
              style={{ marginRight: 4 }}
            >
              Price: Low
            </Chip>
            <Chip
              selected={sortBy === "price-high"}
              onPress={() => setSortBy("price-high")}
            >
              Price: High
            </Chip>
          </View>
        </View>

        {/* 🧱 Professional Grid layout */}
        <View style={layoutStyles.grid}>
          {!loading &&
            filteredSupplements.map((item) => (
              <ProductCard
                key={item.id}
                item={item}
                isFavorite={favorites.includes(item.id)}
                showFavorite={!!userId}
                onPress={() =>
                  navigation.navigate("SupplementDetails", {
                    item,
                    role,
                  })
                }
                onFavoritePress={() => toggleFavorite(item.id)}
                onBuyPress={() =>
                  Alert.alert(
                    "Added to Cart 🛒",
                    `${item.name} added to your plan.`
                  )
                }
              />
            ))}
        </View>

        {/* ⚠️ Empty fallback */}
        {!loading && filteredSupplements.length === 0 && (
          <View style={{ alignItems: "center", marginTop: 40 }}>
            <Text style={{ color: theme.colors.onSurface }}>No supplements found 😔</Text>
            {searchQuery && (
              <Button mode="text" onPress={() => setSearchQuery("")} style={{ marginTop: 8 }}>
                Clear Search
              </Button>
            )}
          </View>
        )}

      </ScrollView>
    </ScreenScaffold>
  );
}
