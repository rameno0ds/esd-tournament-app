<template>
  <div class="login-container">
    <h2>Player Login</h2>
    <form @submit.prevent="login">
      <input type="email" v-model="email" placeholder="Email" required />
      <input type="password" v-model="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <p>Don't have an account? <router-link to="/register">Sign Up</router-link></p>  <!-- Using <router-link> -->
  </div>
</template>

<script>
import { ref } from "vue";
import { auth } from "../firebase"; // firebase.js
import { signInWithEmailAndPassword } from "firebase/auth";
import axios from "axios";
import { useRouter } from "vue-router";

export default {
  setup() {
    const email = ref("");
    const password = ref("");
    const errorMessage = ref("");
    const router = useRouter();

    const login = async () => {
      try {
        // Firebase authentication
        const userCredential = await signInWithEmailAndPassword(auth, email.value, password.value);
        const user = userCredential.user;

        // Fetch player data from backend
        const response = await axios.post("http://127.0.0.1:5001/login", {
          email: email.value,
          password: password.value
        });

        // Redirect to home page
        if (response.data) {
          alert("Login successful!");
          router.push({ name: "home" });
        }
      } catch (error) {
        if (error.response && error.response.status === 404) {
          errorMessage.value = "User does not exist. Please sign up.";
        } else {
          errorMessage.value = "Login failed: " + error.message;
        }
      }
    };


    return { email, password, login, errorMessage };
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  text-align: center;
}
input {
  display: block;
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
}
.error {
  color: red;
  margin-top: 10px;
}
</style>
