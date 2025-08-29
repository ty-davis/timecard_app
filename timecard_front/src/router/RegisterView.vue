<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';


const username = ref('');
const password = ref('');
const errorMessage = ref('');
const successMessage = ref('');

const router = useRouter();

const handleRegister = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!username.value || !password.value) {
    errorMessage.value = 'Username and Password are required';
    return;
  }

  try {
    const response = await axios.post('api/register', {
      username: username.value,
      password: password.value
    })
    
    successMessage.value = `${response.data.message}. Redirecting to login...`;

    setTimeout(() => {
      router.push('/login')
    }, 2000);
  } catch (error: any) {
    if (error.response && error.response.data.message) {
      errorMessage.value = error.response.data.message;
    } else {
      errorMessage.value = 'Registration failed. Please try again later.';
    }
  }
}

</script>

<template>
  <div class="register-container">
    <form @submit.prevent="handleRegister" class="register-form">
      <h2>Create an Account</h2>

      <div class="form-group">
        <InputText type="text" id="username" v-model="username" placeholder="Username" required style="width: 100%;"/>
      </div>

      <div class="form-group">
        <InputText type="password" id="password" v-model="password" placeholder="Password" required style="width: 100%;"/>
      </div>

      <div class="form-group">
        <Button type="submit">Register</Button>
      </div>

      <Message v-if="errorMessage" severity="error">{{ errorMessage }}</Message>
      <Message v-if="successMessage" class="success-message">{{ successMessage }}</Message>
    </form>
  </div>
</template>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100dvh - 70px);
  margin-left: auto;
  margin-right: auto;
  width: 400px;
  max-width: 90%;
}
.register-form {
  width: 100%;
}
.form-group {
  margin: 10px 0px;
}
</style>
