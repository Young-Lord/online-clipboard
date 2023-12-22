<template>
    <div>Clip name: {{ name }}</div>
    <div>Clip content: {{ content }}</div>
    <div>
        <input type="text" v-model="content_new" />
        <button @click="setContent">Save</button>
    </div>
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
            "content_new": "",
        }
    },
    created() {
    },
    methods: {
        async updateContent() {
            try {
                let response = await axios.get(`${api_endpoint}/content/${this.name}`);
                this.content = response.data.data.content;
                this.clip_version = response.data.data.clip_version ?? 0;
            } catch (e) {
                console.log(e);
            }
        },
        async setContent() {
            try {
                let data = new FormData();
                data.append("content", this.content_new);
                data.append("clip_version", this.clip_version);
                let response = await axios({"method": "post", "url":`${api_endpoint}/update_content/${this.name}`, "data": data });
                this.clip_version = response.data.data.clip_version;
                this.updateContent();
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
        this.updateContent();
    },
}
</script>

<style>
</style>

