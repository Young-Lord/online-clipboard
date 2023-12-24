<template>
    <v-container>
        <div>TEST about by {{ author }} !!!</div>
        <div>Current API = {{ api_endpoint }}</div>
        <div>Backend version = {{ backend_version }}</div>
        <div>Metadata = {{ metadata }}</div>
    </v-container>
</template>

<script>
import { axios, api_endpoint } from "@/api";

export default {
    components: {},
    data() {
        return {
            author: "Author",
            api_endpoint: api_endpoint,
            backend_version: "loading...",
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
                this.backend_version = "failed.";
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
