import './assets/styles/main.scss'; 
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-vue-3/dist/bootstrap-vue-3.css'; 
import 'vue-toastification/dist/index.css';

import { createApp } from 'vue';
import { createPinia } from 'pinia';

import BootstrapVue3 from 'bootstrap-vue-3'; 
import App from './App.vue';
import router from './router';
import Toast from 'vue-toastification';

import NavBar from "@/components/global/NavBar.vue";


const options = {
    
    position: 'top-right',
    timeout: 3000,
    closeOnClick: true,
    pauseOnHover: true,
  };
const app = createApp(App);

app.use(BootstrapVue3);
app.use(createPinia());
app.use(router);
app.use(Toast,options);

app.component("NavBar", NavBar);

app.mount('#app');
