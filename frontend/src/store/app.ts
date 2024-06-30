// Utilities
import { MetaData, axios } from "@/api"
import { API_URL } from "@/config"
import { defineStore } from "pinia"
import { AxiosInstance } from "axios"
import { assert } from "@/utils"
import { nanoid } from "nanoid/non-secure"
import local_metadata from "@/metadata.json"

export const useAppStore = defineStore("app", {
    state: () => ({
        _metadata: null as MetaData | null,
        api_endpoint: API_URL,
        is_metadata_fetched: false,
        client_id: nanoid(),
    }),
    actions: {
        async basicInit() {
            axios.defaults.baseURL = this.api_endpoint
            this._metadata = local_metadata
        },
        async initMetadata() {
            if (this.is_metadata_fetched) return
            await this.basicInit()
            const remote_metadata = (await axios.get("/metadata")).data
                .data as MetaData
            // console.log("metadata fetched!")
            if (
                this._metadata === null ||
                remote_metadata.metadata_hash !== this._metadata.metadata_hash
            ) {
                // console.log("hash set fetched!")
                this._metadata = remote_metadata
            }
            this.is_metadata_fetched = true
        },
        async updateEndpoint(axios: AxiosInstance, endpoint: string) {
            this.api_endpoint = endpoint
            this.is_metadata_fetched = false
            await this.initMetadata()
            axios.defaults.baseURL = endpoint
        },
    },
    persist: {
        paths: ["api_endpoint", "_metadata"],
    },
    getters: {
        metadata(): MetaData {
            assert(this._metadata !== null)
            return this._metadata
        },
    },
})
