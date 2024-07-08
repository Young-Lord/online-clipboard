/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import "vuetify/styles"

// Composables
import { createVuetify } from "vuetify"

// Icons
import { aliases, mdi } from "vuetify/iconsets/mdi-svg"
import { mdiHome } from "@mdi/js"

// i18n
import { createVueI18nAdapter } from "vuetify/locale/adapters/vue-i18n"
import i18n from "@/plugins/i18n"
import { useI18n } from "vue-i18n"

// Labs
import { VSnackbarQueue } from "vuetify/labs/VSnackbarQueue"

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
    theme: {
        themes: {
            light: {
                colors: {
                    primary: "#1867C0",
                    secondary: "#5CBBF6",
                },
            },
        },
    },
    icons: {
        defaultSet: "mdi",
        aliases: {
            ...aliases,
            home: mdiHome,
        },
        sets: {
            mdi,
        },
    },
    components: {
        VSnackbarQueue,
    },
    locale: {
        adapter: createVueI18nAdapter({ i18n, useI18n }),
    },
})
