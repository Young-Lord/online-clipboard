<template>
  <v-container>
    <div> TEST about by {{ author }} !!! </div>
    <div> Current API = {{ api_endpoint }} </div>
      <div> Backend version = {{ backend_version }} </div>
  </v-container>
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
      author: "Author",
      api_endpoint: api_endpoint,
      backend_version: "loading..."
    }
  },
  methods: {
    async getBackendVersion() {
      try {
        let response = await axios.get(`${api_endpoint}/version`);
        this.backend_version = response.data.version;
      } catch (e) {
        this.backend_version = "failed."
        console.log(e);
      }
    },
  },
  beforeMount() {
    this.getBackendVersion();
  },
}
</script>

<style>
</style>

