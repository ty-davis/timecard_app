import { createApp } from 'vue';
import { createPinia } from 'pinia';
import PrimeVue from 'primevue/config';
import TheTheme from './presets/Theme.ts';
import 'primeicons/primeicons.css';
import App from './App.vue';
import router from './router/index.ts';
import './styles.css';
import ConfirmationService from 'primevue/confirmationservice';


import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import Card from 'primevue/card';
import ConfirmDialog from 'primevue/confirmdialog';
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';
import Panel from 'primevue/panel';

const app = createApp(App);
const pinia = createPinia();

app.use(router);
app.use(pinia);
app.use(PrimeVue, {
  theme: {
    preset: TheTheme
  }
})
app.use(ConfirmationService);

app.component('AutoComplete', AutoComplete);
app.component('Button', Button);
app.component('Card', Card);
app.component('ConfirmDialog', ConfirmDialog);
app.component('InputText', InputText);
app.component('Message', Message);
app.component('Panel', Panel);

app.mount('#app');
