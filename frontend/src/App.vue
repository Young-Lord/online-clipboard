<template>
    <v-app>
        <v-main>
            <router-view />
        </v-main>
    </v-app>
</template>

<script setup lang="ts"></script>

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
