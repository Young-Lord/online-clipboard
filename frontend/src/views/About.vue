<template>
    <v-container>
        <div>{{ $t('about.test-about-by-author', [author]) }}</div>
        <div>{{ $t('about.current-api-api_endpoint', [api_endpoint]) }}</div>
        <div>{{ $t('about.backend-version-backend_version', [backend_version]) }}</div>
        <div>{{ $t('about.metadata-metadata', [metadata]) }}</div>
    </v-container>
</template>

<script>
import { axios, api_endpoint } from "@/api";

export default {
    components: {},
    data() {
        return {
            author: this.$t('about.author'),
            api_endpoint: api_endpoint,
            backend_version: this.$t('loading...'),
            metadata: {},
        };
    },
    methods: {
        async getMetadata() {
            try {
                let response = await axios.get("/metadata");
                this.metadata = response.data.data;
                this.backend_version = this.metadata.version;
                this.author = this.metadata.owner;
            } catch (e) {
                this.backend_version = this.$t("failed.");
                console.log(e);
            }
        },
    },
    beforeMount() {
        this.getMetadata();
    },
};
</script>

<style></style>
