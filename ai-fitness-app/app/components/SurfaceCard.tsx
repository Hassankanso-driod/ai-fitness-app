/**
 * SurfaceCard.tsx - Reusable Surface Card Component
 * 
 * بطاقة سطحية قابلة لإعادة الاستخدام (للعنواين والبطاقات الملونة)
 * Reusable surface card component (for headers and colored cards)
 */

import React from 'react';
import { View } from 'react-native';
import { Surface, Text, IconButton } from 'react-native-paper';
import { cardStyles, getSurfaceCardStyle, textStyles } from '../styles/globalStyles';
import { brand } from '../utils/themeManager';

type SurfaceCardProps = {
  title: string;
  subtitle?: string;
  icon?: string;
  color?: 'blue' | 'green' | 'orange';
  children?: React.ReactNode;
};

export default function SurfaceCard({
  title,
  subtitle,
  icon,
  color = 'blue',
  children,
}: SurfaceCardProps) {
  const cardStyle = getSurfaceCardStyle(color);

  return (
    <Surface style={cardStyle}>
      <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
        <View style={{ flex: 1 }}>
          <Text
            variant="headlineSmall"
            style={{
              fontWeight: '700',
              color: '#fff',
              marginBottom: 4,
            }}
          >
            {title}
          </Text>
          {subtitle && (
            <Text
              style={{
                color: '#E0E7FF',
                fontSize: 14,
              }}
            >
              {subtitle}
            </Text>
          )}
        </View>
        {icon && (
          <IconButton
            icon={icon}
            size={40}
            iconColor="#fff"
            style={{ backgroundColor: 'rgba(255,255,255,0.2)' }}
          />
        )}
      </View>
      {children}
    </Surface>
  );
}

