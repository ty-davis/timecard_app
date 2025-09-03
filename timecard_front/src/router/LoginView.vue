<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api/axios';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const auth = useAuthStore();

const username = ref('');
const password = ref('');
const errorMessage = ref('');

const handleLogin = async() => {
  errorMessage.value = '';

  if (!username.value || !password.value) {
    errorMessage.value = 'Please enter both username and password.';
    return;
  }
  
  try {
    const response = await api.post('/login', {
      username: username.value,
      password: password.value
    });

    console.log(response);

    const accessToken = response.data.access_token;
    const requestToken = response.data.request_token;

    auth.setTokens(accessToken, requestToken);
    router.push('/')
  } catch (error) {
    console.log(error);
    if (error.response && error.response.status === 401) {
      errorMessage.value = 'Invalid username or password';
    } else {
      errorMessage.value = 'An error occurred. Please try again later.';
    }
  }
}
</script>

<template>
  <div class="login-container">
    <form @submit.prevent="handleLogin" class="login-form">
      <h2>Login to Your Account</h2>

      <div class="form-group">
        <InputText type="text" id="username" v-model="username" placeholder="Username" required style="width: 100%;"/>
      </div>

      <div class="form-group">
        <InputText type="password" id="password" v-model="password" placeholder="Password" required style="width: 100%;"/>
      </div>

      <div class="form-group">
        <Button type="submit">Login</Button>
      </div>

      <Message v-if="errorMessage" severity="error">{{ errorMessage }}</Message>
    </form>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100dvh - 60px);
  margin-left: auto;
  margin-right: auto;
  width: 400px;
  max-width: 90%;
}
.login-form {
  width: 100%;
}
.form-group {
  margin: 10px 0px;
}
</style>
