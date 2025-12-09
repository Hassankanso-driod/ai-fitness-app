/**
 * ProductCard.tsx - Reusable Product/Supplement Card Component
 * 
 * بطاقة منتج/مكمل قابلة لإعادة الاستخدام
 * Reusable product/supplement card component
 */

import React from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { Card, Text, Button, IconButton } from 'react-native-paper';
import { cardStyles, imageStyles, badgeStyles, textStyles, buttonStyles } from '../styles/globalStyles';
import { brand } from '../utils/themeManager';
import { BASE_URL } from '../config';

type ProductCardProps = {
  item: {
    id: number;
    name: string;
    description?: string;
    price: number;
    image_url?: string;
  };
  isFavorite?: boolean;
  onPress: () => void;
  onFavoritePress?: () => void;
  onBuyPress?: () => void;
  showFavorite?: boolean;
};

export default function ProductCard({
  item,
  isFavorite = false,
  onPress,
  onFavoritePress,
  onBuyPress,
  showFavorite = true,
}: ProductCardProps) {
  const imageUrl = item.image_url
    ? `${BASE_URL}/uploads/${item.image_url}`
    : 'https://via.placeholder.com/300x200?text=No+Image';

  return (
    <Card
      style={cardStyles.product}
      onPress={onPress}
    >
      <View style={{ position: 'relative' }}>
        <Image
          source={{ uri: imageUrl }}
          style={imageStyles.productImage}
          onError={() => console.log('Image load error')}
        />
        
        {/* Price Badge */}
        <View style={badgeStyles.priceTag}>
          <Text style={textStyles.price}>
            ${Number(item.price).toFixed(2)}
          </Text>
        </View>
        
        {/* Favorite Button */}
        {showFavorite && onFavoritePress && (
          <IconButton
            icon={isFavorite ? 'heart' : 'heart-outline'}
            iconColor={isFavorite ? '#FF1744' : '#666'}
            size={24}
            style={badgeStyles.favoriteButton}
            onPress={onFavoritePress}
          />
        )}
      </View>

      <Card.Content style={cardStyles.content}>
        <Text numberOfLines={1} style={textStyles.productName}>
          {item.name}
        </Text>
        
        {item.description && (
          <Text numberOfLines={2} style={textStyles.productDescription}>
            {item.description}
          </Text>
        )}

        {onBuyPress && (
          <Button
            mode="contained"
            buttonColor={brand.green[600]}
            textColor="#fff"
            style={buttonStyles.primary}
            contentStyle={{ paddingVertical: 4 }}
            labelStyle={{ fontSize: 12, fontWeight: '600' }}
            onPress={onBuyPress}
          >
            Buy Now
          </Button>
        )}
      </Card.Content>
    </Card>
  );
}

