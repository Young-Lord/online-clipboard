<template>
    <v-app>
        <v-main>
            <div class="vl-parent" v-if="isLoading">
                <loading
                    v-model:active="isLoading"
                    loader="spinner"
                    :can-cancel="false"
                    :is-full-page="true"
                />
            </div>
            <router-view v-else />
        </v-main>
    </v-app>
</template>

<script lang="ts">
import Loading from "vue-loading-overlay"
import "vue-loading-overlay/dist/css/index.css"
import { useAppStore } from "./store/app"

export default {
    data() {
        return {
            isLoading: true,
        }
    },
    components: {
        Loading,
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
