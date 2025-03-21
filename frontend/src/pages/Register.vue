<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-logo">A</div>
      <h2 class="auth-welcome">Create Account</h2>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="input-group">
          <input
            v-model="username"
            type="text"
            required
            placeholder="Username"
          />
        </div>

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

        <div class="input-group">
          <input
            v-model="confirmPassword"
            type="password"
            required
            placeholder="Confirm Password"
          />
        </div>

        <button type="submit" class="btn-gradient">Sign Up</button>
      </form>

      <p class="auth-footer">
        Already have an account?
        <router-link to="/login" class="auth-link">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createUserWithEmailAndPassword, updateProfile } from 'firebase/auth'
import { doc, setDoc, serverTimestamp } from 'firebase/firestore'
import { auth, db } from '../firebase'

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const router = useRouter()

const handleRegister = async () => {
  if (password.value !== confirmPassword.value) {
    alert('Passwords do not match!')
    return
  }
  try {
    // 1. Create user in Firebase Auth
    const userCredential = await createUserWithEmailAndPassword(
      auth,
      email.value,
      password.value
    )
    const user = userCredential.user

    // 2. Optionally update the user's display name in Firebase Auth
    await updateProfile(user, { displayName: username.value })

    // 3. Store additional user info in Firestore
    //    Use a "players" or "users" collection—your choice
    await setDoc(doc(db, 'players', user.uid), {
      username: username.value,
      email: email.value,
      createdAt: serverTimestamp()
    })

    console.log('User registered:', user)
    // Redirect to login after successful registration
    router.push('/login')
  } catch (error) {
    console.error('Registration failed:', error)
    alert(error.message)
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f9f9f9;
  padding: 1rem;
}

.auth-card {
  background: #fff;
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  text-align: center;
}

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

.auth-welcome {
  margin-bottom: 2rem;
  font-weight: 500;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

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

.auth-footer {
  margin-top: 1.5rem;
  font-size: 0.9rem;
}

.auth-link {
  color: #6a5af9;
  text-decoration: none;
  font-weight: 500;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
