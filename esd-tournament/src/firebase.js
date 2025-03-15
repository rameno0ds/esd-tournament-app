// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDvMk7Lu6FoU3efSISq-31IiQY0tIoW_lw",
  authDomain: "esd-app-e8c06.firebaseapp.com",
  projectId: "esd-app-e8c06",
  storageBucket: "esd-app-e8c06.firebasestorage.app",
  messagingSenderId: "871050237660",
  appId: "1:871050237660:web:85466f58c97dab87a48619",
  measurementId: "G-7R0XWEG69H",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
