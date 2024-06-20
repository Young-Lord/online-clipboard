/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import "vuetify/styles"

// Composables
import { createVuetify } from "vuetify"
import { aliases, mdi } from "vuetify/iconsets/mdi-svg"
import { mdiHome } from "@mdi/js"

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
})
