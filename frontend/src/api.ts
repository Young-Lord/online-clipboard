import original_axios, { isAxiosError } from "axios"
import { $t, language } from "./plugins/i18n"
import { showDetailWarning } from "./plugins/swal"
import { API_URL } from "./config"

// https://xiets.gitee.io/json-to-any-web/
// [A-Z][a-z] -> _\L$0
export interface Response<T> {
    data: T
    error_id: string | null
    message: string | null
    status: number
}

export interface ClipData {
    all_file_size: number
    clip_version: number
    content: string
    file_count: number
    files: FileData[]
    is_readonly: boolean
    name: string
    readonly_name: string
    timeout_seconds: number
    user_property: string
}

export interface FileData {
    created_at: string
    download_url: string
    expire_at: string
    filename: string
    id: number
    preview_url: string
    size: number
    timeout_seconds: number
}

export interface MetaData {
    allow_chars: string
    allow_mail: boolean
    default_file_timeout: number
    default_note_timeout: number
    description: string
    email: string
    file_link_timeout: number
    logo: string
    max_all_file_size: number
    max_content_length: number
    max_file_count: number
    max_file_size: number
    max_name_length: number
    max_password_length: number
    max_timeout: number
    name: string
    owner: string
    repository: string
    timeout_selections: number[]
    url: string
    version: string
    metadata_hash: string
}

export interface UserProperty {
    encrypt_text_content: boolean | undefined
    encrypt_text_content_algo: string | undefined
    encrypt_file: boolean | undefined
}

export enum MailSubscriptionStatus {
    ACCEPT = 1,
    DENY = 2,
    PENDING = 3,
    NO_REQUESTED = 4,
}

export enum MailSubscriptionSetting {
    ACCEPT = "true",
    DENY = "false",
    RESET = "reset",
    DELETE = "delete",
}

export interface MailSubscriptionData {
    subscribe: MailSubscriptionStatus
}

export const axios = original_axios.create({
    withCredentials: true,
    baseURL: API_URL,
})
axios.defaults.headers.common["Content-Type"] = "application/json"

axios.interceptors.request.use(
    function (config) {
        if (config.url === "/mailto" || config.url?.startsWith("/mailto/")) {
            config.data = { language: language, ...config.data }
        }
        return config
    }
)

axios.interceptors.response.use(
    function (response) {
        return response
    },
    function (error) {
        if (isAxiosError(error)) {
            if (error.response?.status === 429) {
                showDetailWarning({
                    title: $t("clip.error"),
                    text: $t("error.rate_limit"),
                })
                return
            }
            return Promise.reject(error)
        }
    }
)
