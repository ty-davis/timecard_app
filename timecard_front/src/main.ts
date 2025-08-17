import { createApp } from 'vue';
import { createPinia } from 'pinia';
import PrimeVue from 'primevue/config';
import TheTheme from './presets/Theme.ts';
import 'primeicons/primeicons.css';
import App from './App.vue';
import router from './router/index.ts';

import Button from "primevue/button";
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';

const app = createApp(App);
const pinia = createPinia();

app.use(router);
app.use(pinia);
app.use(PrimeVue, {
  theme: {
    preset: TheTheme
  }
})

app.component('Button', Button);
app.component('InputText', InputText);
app.component('Message', Message);

app.mount('#app');
