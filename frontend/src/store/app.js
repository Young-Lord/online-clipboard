// Utilities
import { API_BASE_PATH } from "@/config"
import { defineStore } from "pinia"

export const useAppStore = defineStore("app", {
    state: () => ({
        timeout_selections: {
            "1_minute": 60,
            "10_minutes": 600,
            "30_minutes": 1800,
            "1_hour": 3600,
            "6_hours": 21600,
            "12_hours": 43200,
            "1_day": 86400,
            "7_days": 604800,
            "14_days": 1209600,
            "30_days": 2592000,
            "1_year": 31536000,
            "3_years": 94608000,
        },
    }),
    getters: {},
})
