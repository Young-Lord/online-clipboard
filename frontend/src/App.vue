<template>
    <v-app>
        <v-main>
            <router-view />
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import { useTheme } from "vuetify"
import { onMounted } from "vue"

const theme = useTheme()

onMounted(() => {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)")
    theme.global.name.value = prefersDark.matches ? "dark" : "light"
    prefersDark.addEventListener("change", (e) => {
        theme.global.name.value = e.matches ? "dark" : "light"
    })
})
</script>

<script lang="ts">
import { useAppStore } from "@/store/app"
export default {
    beforeMount() {
        const appStore = useAppStore()
        appStore.basicInit()
        appStore.initMetadata().then()
    },
}
</script>

<style>
/* Vuetify a11y issue: https://github.com/vuetifyjs/vuetify/issues/16928 */
.v-messages,
.v-label {
    opacity: var(--v-high-emphasis-opacity) !important;
}
</style>
