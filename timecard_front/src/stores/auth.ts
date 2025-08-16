import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export const useAuthStore = defineStore('auth', () => {
    const token = ref(localStorage.getItem('jwt'));
    const router = useRouter();

    const isLoggedIn = computed(() => !!token.value);

    const login = (jwt: string) => {
        token.value = jwt;
        localStorage.setItem('jwt', jwt);
        axios.defaults.headers.common['Authorization'] = `Bearer ${jwt}`;
    }

    const logout = () => {
        token.value = null;
        localStorage.removeItem('jwt');
        delete axios.defaults.headers.common['Authorization'];
        router.push('/');
    }

    if (token.value) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
    }

    return { token, isLoggedIn, login, logout };
})
