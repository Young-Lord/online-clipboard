import original_axios from "axios"
import { useAppStore } from "./store/app"
const appStore = useAppStore()

export const axios = original_axios.create({
    withCredentials: true,
    baseURL: appStore.api_endpoint,
})
axios.defaults.headers.common["Content-Type"] = "application/json"

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
    files: File[]
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
}

export interface UserProperty {
    encrypt_text_content: boolean | undefined
    encrypt_text_content_algo: string | undefined
    encrypt_file: boolean | undefined
}
