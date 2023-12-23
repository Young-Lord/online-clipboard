// Utilities
import { defineStore } from "pinia";

export const useAppStore = defineStore("app", {
  state: () => ({
    api_http_prefix: "",
    api_path: "/api",
    timeout_selections: {
      "1 minute": 60,
      "10 minutes": 600,
      "30 minutes": 1800,
      "1 hour": 3600,
      "6 hours": 21600,
      "12 hours": 43200,
      "1 day": 86400,
      "7 days": 604800,
      "14 days": 1209600,
      "30 days": 2592000,
      "1 year": 31536000,
      "3 years": 94608000,
    },
  }),
  getters: {
    api_endpoint: (state) => {
      if (process.env.NODE_ENV === "development") {
        return "http://127.0.0.1:5000" + state.api_path;
      }
      return (
        (state.api_http_prefix ||
          `${window.location.protocol}//${window.location.host}`) +
        state.api_path
      );
    },
  },
});
