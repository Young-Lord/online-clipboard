// Utilities
import { defineStore } from "pinia";

export const useAppStore = defineStore("app", {
  state: () => ({
    api_http_prefix: "",
    api_path: "/api",
  }),
  getters: {
    api_endpoint: (state) => {
      return (
        (state.api_http_prefix ||
          `${window.location.protocol}//${window.location.host}`) +
        state.api_path
      );
    }
  },
});
