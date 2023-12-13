<template>
    <div>Clip name: {{ name }}</div>
    <div>Clip content: {{ content }}</div>
</template>

<script>
import { useAppStore } from '../store/app.js';
import axios from 'axios';

const appStore = useAppStore();
const api_endpoint = appStore.api_endpoint;

export default {
    components: {
    },
    data() {
        return {
            "clip_version": 0,
            "content": "",
        }
    },
    created() {
    },
    methods: {
        async setContent() {
            try {
                let response = await axios.get(`${api_endpoint}/content/${this.name}`);
                this.content = response.data.data.content;
                this.clip_version = response.data.data.clip_version ?? 0;
            } catch (e) {
                console.log(e);
            }
        },
    },
    computed: {
        name() {
            return this.$route.params.name
        },
    },
    beforeMount() {
        this.setContent();
    },
}
</script>

<style>
</style>

