/**
 * config.ts - Backend API Configuration
 * 
 * This file contains the base URL for your backend API server.
 * 
 * IMPORTANT: Change the IP address below to match your computer's IP address
 * when testing on a physical device or emulator.
 * 
 * How to find your IP:
 * - Windows: Open Command Prompt, type "ipconfig", look for "IPv4 Address"
 * - Mac/Linux: Open Terminal, type "ifconfig" or "ip addr", look for inet address
 * 
 * Testing options:
 * - Android emulator: Use http://10.0.2.2:8000 (special IP for Android emulator)
 * - iOS simulator: Use http://localhost:8000
 * - Physical device: Use http://YOUR_COMPUTER_IP:8000 (e.g., http://192.168.1.107:8000)
 * 
 * Make sure your backend server is running on port 8000!
 */

export const BASE_URL =
  process.env.BASE_URL || "http://192.168.1.103:8000";
