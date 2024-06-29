<template>
    <v-app>
        <v-main>
            <div class="vl-parent" v-if="isLoading">
                <v-overlay
                    :model-value="true"
                    class="fill-height justify-center align-center"
                >
                    <v-progress-circular
                        color="primary"
                        size="64"
                        indeterminate
                    ></v-progress-circular>
                </v-overlay>
            </div>
            <router-view v-else />
        </v-main>
    </v-app>
</template>

<script lang="ts">
import { useAppStore } from "./store/app"

export default {
    data() {
        return {
            isLoading: true,
        }
    },
    methods: {},
    async mounted() {
        const appStore = useAppStore()
        if (appStore._metadata === null) {
            await appStore.initMetadata()
        } else {
            appStore.initMetadata().then()
        }
        this.isLoading = false
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
