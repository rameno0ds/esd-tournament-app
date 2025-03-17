import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from "axios";

axios
  .get("http://127.0.0.1:5000/")
  .then((response) => console.log(response.data))
  .catch((error) => console.error("Error:", error));

const app = createApp(App);
app.use(router);
app.mount("#app");

