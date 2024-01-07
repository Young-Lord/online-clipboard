import original_axios from "axios"
import { API_ENDPOINT } from "./config"

export const axios = original_axios.create({
    withCredentials: true,
    baseURL: API_ENDPOINT,
})
axios.defaults.headers.common["Content-Type"] = "application/json"
