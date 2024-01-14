// Utilities
import { MetaData, axios } from "@/api"
import { API_ENDPOINT } from "@/config"
import { defineStore } from "pinia"
import { AxiosInstance } from "axios"

export const useAppStore = defineStore("app", {
    state: () => ({
        _metadata: {} as MetaData,
        isMetadataLoaded: false,
        api_endpoint: API_ENDPOINT,
    }),
    actions: {
        async metadata(): Promise<MetaData> {
            if (!this.isMetadataLoaded) {
                console.debug("Loading metadata from server...")
                this._metadata = (await axios.get("/metadata")).data
                    .data as MetaData
                this.isMetadataLoaded = true
            }
            return this._metadata
        },
        updateEndpoint(axios: AxiosInstance, endpoint: string) {
            this.api_endpoint = endpoint
            this.isMetadataLoaded = false
            axios.defaults.baseURL = endpoint
        },
    },
    persist: {
        paths: ["api_endpoint"],
    },
})
