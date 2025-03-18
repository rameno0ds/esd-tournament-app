<template>
  <div class="register-container">
    <h2>Player Sign Up</h2>
    <form @submit.prevent="register">
      <input type="text" v-model="username" placeholder="Username" required />
      <input type="email" v-model="email" placeholder="Email" required />
      <input type="password" v-model="password" placeholder="Password" required />
      <button type="submit">Sign Up</button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script>
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

export default {
  setup() {
    const username = ref("");
    const email = ref("");
    const password = ref("");
    const errorMessage = ref("");
    const router = useRouter();

    const register = async () => {
      try {
        // Send registration request to backend
        const response = await axios.post("http://127.0.0.1:5001/register", {
          email: email.value,
          username: username.value,
          password: password.value
        });

        // Handle successful response
        if (response.status === 201) {
          alert("Registration successful!");
          router.push({ name: "login" });
        } else {
          // Handle unexpected response codes
          errorMessage.value = "Registration failed. Please try again.";
        }
      } catch (error) {
        // Handle error if request fails
        if (error.response && error.response.data) {
          errorMessage.value = error.response.data.error || "Registration failed: " + error.message;
        } else {
          errorMessage.value = "Network error. Please try again later.";
        }
      }
    };

    return { username, email, password, register, errorMessage };
  }
};
</script>

<style scoped>
.register-container {
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
