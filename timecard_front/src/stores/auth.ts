import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

export const useAuthStore = defineStore('auth', () => {
    const accessToken = ref(localStorage.getItem('access_token'));
    const refreshToken = ref(localStorage.getItem('refresh_token'));
    const router = useRouter();

    const isLoggedIn = computed(() => !!accessToken.value);


    function setTokens(access: string, refresh: string) {
        accessToken.value = access;
        refreshToken.value = refresh;
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
    }

    function setNewAccessToken(access: string) {
        accessToken.value = access;
        localStorage.setItem('access_token', access);
    }

    const logout = () => {
        accessToken.value = null;
        refreshToken.value = null
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/');
    }

    return { accessToken, refreshToken, isLoggedIn, setTokens, setNewAccessToken, logout };
})
