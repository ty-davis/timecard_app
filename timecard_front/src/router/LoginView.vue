<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const errorMessage = ref('');

const router = useRouter();

const handleLogin = async() => {
  errorMessage.value = '';

  if (!username.value || !password.value) {
    errorMessage.value = 'Please enter both username and password.';
  }
  
  try {
    const response = await axios.post('/api/login', {
      username: username.value,
      password: password.value
    });

    console.log(response);

    const token = response.data.access_token;

    localStorage.setItem('jwt', token);

    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

    router.push('/');
  } catch (error) {
    console.log(error);
    if (error.response && error.response.status === 401) {
      errorMessage.value = 'Invalid username or password';
    } else {
      errorMessage.value = 'An error occurred. Please try again later.';
    }
    delete axios.defaults.headers.common['Authorization'];
  }
}
</script>

<template>
  <!-- ⚙️ THE FORM TEMPLATE -->
  <div class="login-container">
    <form @submit.prevent="handleLogin" class="login-form">
      <h2>Login to Your Account</h2>

      <!-- Username Input -->
      <div class="form-group">
        <label for="username">Username</label>
        <input
          type="text"
          id="username"
          v-model="username"
          placeholder="Enter your username"
          required
        />
      </div>

      <!-- Password Input -->
      <div class="form-group">
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          v-model="password"
          placeholder="Enter your password"
          required
        />
      </div>

      <!-- Submit Button -->
      <button type="submit">Login</button>

      <!-- Error Message Display -->
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<style scoped>
/* 🎨 THE STYLES */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f4f4f4;
}
.login-form {
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}
h2 {
  margin-bottom: 1.5rem;
  text-align: center;
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
}
input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  width: 100%;
  padding: 0.75rem;
  background-color: #28a745; /* Green color for login */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}
button:hover {
  background-color: #218838;
}
.error-message {
  color: #d9534f;
  margin-top: 1rem;
  text-align: center;
}
</style>
