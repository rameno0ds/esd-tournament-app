<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Logo/Brand Placeholder -->
      <div class="auth-logo">A</div>
      <h2 class="auth-welcome">Welcome</h2>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="input-group">
          <input
            v-model="email"
            type="email"
            required
            placeholder="Email"
          />
        </div>

        <div class="input-group">
          <input
            v-model="password"
            type="password"
            required
            placeholder="Password"
          />
        </div>

        <button type="submit" class="btn-gradient">Login</button>
      </form>

      <p class="auth-footer">
        Don't have an account?
        <router-link to="/register" class="auth-link">Sign Up</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { signInWithEmailAndPassword } from 'firebase/auth'
import { auth } from '../firebase'

const email = ref('')
const password = ref('')
const router = useRouter()

const handleLogin = async () => {
  try {
    const userCredential = await signInWithEmailAndPassword(
      auth,
      email.value,
      password.value
    )
    console.log('User logged in:', userCredential.user)
    // Navigate to the home or dashboard page upon successful login
    router.push('/')
  } catch (error) {
    console.error('Login failed:', error)
    alert(error.message)
  }
}
</script>

<style scoped>
/* Container centers the card vertically/horizontally */
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f9f9f9;
  padding: 1rem;
}

/* Card styling */
.auth-card {
  background: #fff;
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  text-align: center;
}

/* Placeholder logo */
.auth-logo {
  font-size: 2.5rem;
  font-weight: 700;
  background: #eeeeee;
  width: 60px;
  height: 60px;
  margin: 0 auto 1rem auto;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Welcome text */
.auth-welcome {
  margin-bottom: 2rem;
  font-weight: 500;
}

/* Form styling */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Input groups */
.input-group {
  position: relative;
}

.input-group input {
  width: 100%;
  border: none;
  border-bottom: 1px solid #ccc;
  padding: 0.5rem 0;
  font-size: 1rem;
  outline: none;
}

/* Gradient button */
.btn-gradient {
  background: linear-gradient(90deg, #6a5af9, #9e6af8);
  border: none;
  border-radius: 9999px;
  padding: 0.75rem 1.5rem;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: filter 0.2s ease;
}

.btn-gradient:hover {
  filter: brightness(1.1);
}

/* Footer text */
.auth-footer {
  margin-top: 1.5rem;
  font-size: 0.9rem;
}

/* Link styling */
.auth-link {
  color: #6a5af9;
  text-decoration: none;
  font-weight: 500;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>

