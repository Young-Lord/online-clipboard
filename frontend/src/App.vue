<template>
    <v-app>
        <v-main>
            <div class="vl-parent" v-if="isLoading">
                <v-overlay
                    :model-value="true"
                    class="align-center justify-center"
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
