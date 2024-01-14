// Utilities
import { MetaData, axios } from "@/api"
import { defineStore } from "pinia"

export const useAppStore = defineStore("app", {
    state: () => ({
        _metadata: {} as MetaData,
        isMetadataLoaded: false,
    }),
    actions: {
        async metadata(): Promise<MetaData> {
            if (!this.isMetadataLoaded) {
                console.debug("Loading metadata from server...")
                this._metadata = (await axios.get("/metadata")).data.data as MetaData
                this.isMetadataLoaded = true
            }
            return this._metadata
        },
    },
    persist: {
        paths: ["metadata"],
    },
})
