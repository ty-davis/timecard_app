import { createApp } from 'vue';
import { createPinia } from 'pinia';
import PrimeVue from 'primevue/config';
import TheTheme from './presets/Theme.ts';
import 'primeicons/primeicons.css';
import App from './App.vue';
import router from './router/index.ts';
import './styles.css';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';


import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Checkbox from 'primevue/checkbox';
import ColorPicker from 'primevue/colorpicker';
import ConfirmDialog from 'primevue/confirmdialog';
import DatePicker from 'primevue/datepicker';
import Dialog from 'primevue/dialog';
import Divider from 'primevue/divider';
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';
import Panel from 'primevue/panel';
import Password from 'primevue/password';
import Toast from 'primevue/toast';

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
app.use(ToastService);

app.component('AutoComplete', AutoComplete);
app.component('Button', Button);
app.component('Card', Card);
app.component('Checkbox', Checkbox);
app.component('ColorPicker', ColorPicker);
app.component('ConfirmDialog', ConfirmDialog);
app.component('DatePicker', DatePicker);
app.component('Dialog', Dialog);
app.component('Divider', Divider);
app.component('InputText', InputText);
app.component('Message', Message);
app.component('Panel', Panel);
app.component('Password', Password);
app.component('Toast', Toast);

app.mount('#app');
