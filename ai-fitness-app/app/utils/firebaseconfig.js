// utils/firebaseConfig.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

// Firebase config from your console
const firebaseConfig = {
  apiKey: "AIzaSyDc8-Z4afGCSlXuJrwRLn9Me5VkuaLFJks",
  authDomain: "ai-fitness-app-d27e8.firebaseapp.com",
  projectId: "ai-fitness-app-d27e8",
  storageBucket: "ai-fitness-app-d27e8.appspot.com",
  messagingSenderId: "1028176192357",
  appId: "1:1028176192357:web:e3dcb744855279bf98778c",
};

// Initialize and export Firestore
const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
