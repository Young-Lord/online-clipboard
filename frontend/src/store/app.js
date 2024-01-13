// Utilities
import { axios } from "@/api"
import { defineStore } from "pinia"

export const useAppStore = defineStore("app", {
    state: () => ({
        _metadata: {},
        isMetadataLoaded: false,
    }),
    actions: {
        async metadata() {
            if (!this.isMetadataLoaded) {
                console.debug("Loading metadata from server...")
                this._metadata = (await axios.get("/metadata")).data.data
                this.isMetadataLoaded = true
            }
            return this._metadata
        },
    },
    persist: {
        paths: ["metadata"],
    },
})
