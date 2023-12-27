import { useAppStore } from "@/store/app"
import original_axios from "axios"

const appStore = useAppStore()
export const api_endpoint = appStore.api_endpoint
export const axios = original_axios.create({
    withCredentials: true,
    baseURL: api_endpoint,
})
axios.defaults.headers.common["Content-Type"] = "application/json"
