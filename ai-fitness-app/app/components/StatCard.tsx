/**
 * StatCard.tsx - Reusable Stat Card Component
 * 
 * بطاقة إحصائية قابلة لإعادة الاستخدام
 * Reusable stat card component for displaying metrics
 */

import React from 'react';
import { Card, Text, Icon } from 'react-native-paper';
import { cardStyles, textStyles, getStatCardStyle, getStatTextColor } from '../styles/globalStyles';
import { useTheme } from 'react-native-paper';

type StatCardProps = {
  icon: string;
  label: string;
  value: string | number;
  color: 'blue' | 'green' | 'orange';
};

export default function StatCard({ icon, label, value, color }: StatCardProps) {
  const theme = useTheme();
  const cardStyle = getStatCardStyle(color);
  const textColor = getStatTextColor(color);

  return (
    <Card style={cardStyle}>
      <Icon source={icon} size={22} color={textColor} />
      <Text style={[textStyles.statLabel, { color: textColor }]}>
        {label}
      </Text>
      <Text variant="titleMedium" style={[textStyles.statValue, { color: theme.colors.onSurface }]}>
        {value}
      </Text>
    </Card>
  );
}

