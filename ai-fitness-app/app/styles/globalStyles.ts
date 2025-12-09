/**
 * globalStyles.ts - Unified Styles System
 * 
 * جميع الأنماط الموحدة للتطبيق
 * All unified styles for the app
 * 
 * استخدام: استورد الأنماط من هنا بدلاً من كتابتها في كل شاشة
 * Usage: Import styles from here instead of writing them in each screen
 */

import { StyleSheet, ViewStyle, TextStyle, ImageStyle } from 'react-native';
import { brand } from '../utils/themeManager';

// ========== Colors ==========
export const colors = {
  // Brand colors
  primary: brand.blue[600],
  secondary: brand.green[600],
  tertiary: brand.orange[600],
  
  // Text colors
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  textLight: '#9CA3AF',
  textWhite: '#FFFFFF',
  
  // Background colors
  background: '#FFFFFF',
  backgroundLight: '#F9FAFB',
  backgroundGray: '#F3F4F6',
  
  // Border colors
  border: '#E5E7EB',
  borderLight: '#F3F4F6',
  
  // Status colors
  success: brand.green[600],
  error: '#DC2626',
  warning: brand.orange[600],
  info: brand.blue[600],
  
  // Overlay
  overlay: 'rgba(255,255,255,0.9)',
  overlayDark: 'rgba(0,0,0,0.5)',
};

// ========== Spacing ==========
export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
};

// ========== Typography ==========
export const typography = {
  h1: {
    fontSize: 28,
    fontWeight: '800' as const,
    color: colors.textPrimary,
  },
  h2: {
    fontSize: 24,
    fontWeight: '700' as const,
    color: colors.textPrimary,
  },
  h3: {
    fontSize: 20,
    fontWeight: '700' as const,
    color: colors.textPrimary,
  },
  body: {
    fontSize: 16,
    fontWeight: '400' as const,
    color: colors.textPrimary,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400' as const,
    color: colors.textSecondary,
  },
  caption: {
    fontSize: 12,
    fontWeight: '400' as const,
    color: colors.textSecondary,
  },
  button: {
    fontSize: 16,
    fontWeight: '600' as const,
  },
};

// ========== Card Styles ==========
export const cardStyles = StyleSheet.create({
  // Standard card
  standard: {
    borderRadius: 16,
    backgroundColor: colors.background,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
    borderWidth: 1,
    borderColor: colors.border,
  },
  
  // Product/Supplement card
  product: {
    width: '47%',
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: colors.background,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.lg,
  },
  
  // Stat card (for HomeScreen)
  stat: {
    flex: 1,
    borderRadius: 16,
    paddingVertical: spacing.md,
    alignItems: 'center' as const,
    borderLeftWidth: 4,
  },
  
  // Surface card (colored background)
  surface: {
    borderRadius: 20,
    padding: spacing.xl,
    marginVertical: spacing.lg,
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 6,
  },
  
  // Content padding
  content: {
    paddingVertical: 14,
    paddingHorizontal: spacing.md,
  },
});

// ========== Button Styles ==========
export const buttonStyles = StyleSheet.create({
  primary: {
    borderRadius: 12,
    paddingVertical: spacing.sm,
  },
  secondary: {
    borderRadius: 12,
    paddingVertical: spacing.sm,
    borderWidth: 2,
  },
  fullWidth: {
    width: '100%',
  },
  mediumWidth: {
    width: '85%',
  },
});

// ========== Layout Styles ==========
export const layoutStyles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  
  centerContent: {
    flex: 1,
    justifyContent: 'center' as const,
    alignItems: 'center' as const,
    paddingHorizontal: spacing.xl,
  },
  
  row: {
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
  },
  
  rowBetween: {
    flexDirection: 'row' as const,
    justifyContent: 'space-between' as const,
    alignItems: 'center' as const,
  },
  
  rowWrap: {
    flexDirection: 'row' as const,
    flexWrap: 'wrap' as const,
    justifyContent: 'space-between' as const,
    gap: spacing.md,
  },
  
  grid: {
    flexDirection: 'row' as const,
    flexWrap: 'wrap' as const,
    justifyContent: 'space-between' as const,
    gap: spacing.md,
  },
});

// ========== Image Styles ==========
export const imageStyles = StyleSheet.create({
  productImage: {
    width: '100%',
    height: 160,
    resizeMode: 'cover' as const,
    backgroundColor: colors.backgroundGray,
  },
  
  largeImage: {
    width: '100%',
    height: 250,
    resizeMode: 'contain' as const,
  },
  
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    resizeMode: 'cover' as const,
  },
});

// ========== Badge/Price Tag Styles ==========
export const badgeStyles = StyleSheet.create({
  priceTag: {
    position: 'absolute' as const,
    top: spacing.sm,
    right: spacing.sm,
    backgroundColor: colors.overlay,
    borderRadius: 12,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  
  favoriteButton: {
    position: 'absolute' as const,
    top: spacing.sm,
    left: spacing.sm,
    backgroundColor: colors.overlay,
  },
});

// ========== Text Styles ==========
export const textStyles = StyleSheet.create({
  title: {
    ...typography.h2,
    marginBottom: spacing.sm,
  },
  
  subtitle: {
    ...typography.bodySmall,
    marginBottom: spacing.md,
    lineHeight: 20,
  },
  
  productName: {
    ...typography.h3,
    fontSize: 16,
    marginBottom: spacing.xs,
  },
  
  productDescription: {
    ...typography.caption,
    marginBottom: spacing.md,
    lineHeight: 16,
  },
  
  price: {
    ...typography.bodySmall,
    fontWeight: '700' as const,
    color: brand.green[700],
  },
  
  statLabel: {
    ...typography.bodySmall,
    fontWeight: '700' as const,
    marginTop: spacing.xs,
  },
  
  statValue: {
    ...typography.body,
    marginTop: spacing.xs,
  },
});

// ========== Helper Functions ==========
/**
 * Get stat card style with color
 */
export const getStatCardStyle = (color: 'blue' | 'green' | 'orange') => ({
  ...cardStyles.stat,
  backgroundColor: brand[color][50],
  borderLeftColor: brand[color][600],
});

/**
 * Get stat text color
 */
export const getStatTextColor = (color: 'blue' | 'green' | 'orange') => brand[color][600];

/**
 * Get surface card style with color
 */
export const getSurfaceCardStyle = (color: 'blue' | 'green' | 'orange') => ({
  ...cardStyles.surface,
  backgroundColor: brand[color][600],
});

// ========== Export All ==========
export default {
  colors,
  spacing,
  typography,
  cardStyles,
  buttonStyles,
  layoutStyles,
  imageStyles,
  badgeStyles,
  textStyles,
};

