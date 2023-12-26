/**
 * plugins/index.js
 *
 * Automatically included in `./src/main.js`
 */

// Plugins
import vuetify from "./vuetify";
import pinia from "../store";
import router from "../router";
import VueSweetalert2 from "vue-sweetalert2";
import "sweetalert2/dist/sweetalert2.min.css";
import i18n from "./i18n";

const swal_options = {
    showClass: { popup: "animate__animated animate__fadeIn animate__faster" },
};

export function registerPlugins(app) {
    app.use(vuetify)
        .use(router)
        .use(pinia)
        .use(VueSweetalert2, swal_options)
        .use(i18n);
}
