<template>
    <v-app>
        <v-app-bar app>
            <v-btn icon @click="goToHome()">
                <v-icon>mdi-home</v-icon>
            </v-btn>
            <!-- sync button if outdated-->
            <v-btn icon @click="fetchContent(false)" v-if="is_local_outdated">
                <v-icon>mdi-download</v-icon>
            </v-btn>
            <!-- sync button if outdated-->
            <v-btn icon @click="pushContent(true)" v-if="is_local_outdated">
                <v-icon>mdi-upload</v-icon>
            </v-btn>
            <!-- saved status in plaintext -->
            <v-toolbar-title>{{ save_status ? $t(`save_status.${save_status}`) : '' }}</v-toolbar-title>
            <v-spacer></v-spacer>
            <!--delete button-->
            <v-btn icon @click="deleteContent()" v-if="!is_new && !is_readonly">
                <v-icon>mdi-delete</v-icon>
            </v-btn>
            <!-- password button-->
            <v-btn icon @click="changePassword()" v-if="!is_new && !is_readonly">
                <v-icon>mdi-lock</v-icon>
            </v-btn>
            <!--save button-->
            <v-btn icon @click="pushContent()" v-if="!is_readonly">
                <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <!-- copy button-->
            <v-btn icon @click="copyString(local_content)">
                <v-icon>mdi-content-copy</v-icon>
            </v-btn>
            <!-- download button-->
            <v-btn icon @click="downloadContent()">
                <v-icon>mdi-download</v-icon>
            </v-btn>
        </v-app-bar>

        <v-main>
            <v-container>
                <v-row rows="12">
                    <v-col cols="12" md="8">
                        <!-- Larger Text Input Box -->
                        <v-textarea rows="15" variant="outlined" auto-grow v-model="local_content"
                            @input="setEditingStatus()" @keydown.ctrl.s.exact="pushContentIfChanged()"
                            @keydown.ctrl.s.exact.prevent @focusout="pushContentIfChanged()" :disabled="uploading">
                        </v-textarea>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card id="sidebar">
                            <!-- 下拉框，选择过期时间 -->
                            <v-select v-bind:items="timeout_selections.map((key) => { return timeDeltaToString(key) })"
                                :label="$t('clip.expiration')" @update:model-value="setNoteTimeout"
                                v-model="selected_timeout" prepend-inner-icon="mdi-clock" v-if="!is_new && !is_readonly">
                            </v-select>
                            <!-- current url, click to copy-->
                            <v-text-field :label="$t('clip.current_url_click_to_copy')" v-model="current_url" readonly
                                prepend-inner-icon="mdi-link" @click="copyString(current_url)" class="cursor-pointer"
                                v-if="!is_readonly">
                            </v-text-field>
                            <!-- readonly url, click to copy-->
                            <v-text-field
                                :label="hasReadonlyName ? $t('clip.readonly_url_click_to_copy') : $t('clip.readonly_url_is_disabled')"
                                v-model="readonly_url_check_empty" readonly prepend-inner-icon="mdi-link"
                                @click="hasReadonlyName && copyString(readonly_url)" class="cursor-pointer"
                                :append-inner-icon="hasReadonlyName ? 'mdi-delete' : 'mdi-plus-circle-outline'"
                                @click:append-inner="toggleReadonlyUrl()" v-if="hasReadonlyName">
                            </v-text-field>
                            <v-list v-model:opened="sidebar_list_opened" v-if="!is_new">
                                <v-list-group value="Advanced Settings">
                                    <template v-slot:activator="{ props }">
                                        <v-list-item v-bind="props" prepend-icon="mdi-cog"
                                            :title="$t('clip.advanced_settings')"></v-list-item>
                                    </template>

                                    <!-- checkbox for auto fetch cloud version -->
                                    <v-checkbox v-model="auto_fetch_remote_content"
                                        :label="$t('clip.auto_fetch_remote_content')">
                                    </v-checkbox>
                                    <!-- checkbox for auto fetch cloud version -->
                                    <v-checkbox v-model="encrypt_text_content" :label="$t('clip.encrypt_content')"
                                        v-if="!is_readonly" @change="updateEncryptText()">
                                    </v-checkbox>
                                </v-list-group>
                            </v-list>
                        </v-card>
                    </v-col>
                    <v-col cols="12">
                        <v-card id="file-card">
                            <!-- Drag or click to upload file -->
                            <v-file-input
                                :label="$t('clip.drag_or_click_to_upload_file') + ' ' + $t('clip.file_limits', [humanFileSize(metadata.max_file_size), remote_files.length, metadata.max_file_count, humanFileSize(getTotalSize(remote_files)), humanFileSize(metadata.max_all_file_size)])"
                                prepend-icon="mdi-file-upload" @change="uploadFile()"
                                v-if="!is_readonly && !is_new && metadata.max_file_count > 0 && metadata.max_all_file_size > 0"
                                :disabled="uploading || metadata.max_file_count <= remote_files.length || metadata.max_all_file_size <= getTotalSize(remote_files)"
                                v-model="file_to_upload" multiple>
                            </v-file-input>
                            <!--all files, with download and delete button-->
                            <v-list v-if="!is_new">
                                <v-list-item v-for="file in remote_files" :key="file.id">
                                    <v-list-item-title>{{ file.filename }}
                                    </v-list-item-title>
                                    <v-list-item-subtitle>{{ humanFileSize(file.size) }} {{
                                        $t('clip.file.expiration_date_is', [$d(new Date(file.expire_at), 'long')])
                                    }}</v-list-item-subtitle>
                                    <template v-slot:append>
                                        <v-list-item-action end>
                                            <v-btn icon variant="text" @click="downloadFile(file)">
                                                <v-icon>mdi-download</v-icon>
                                            </v-btn>
                                            <v-btn icon variant="text" @click="previewFile(file)">
                                                <v-icon>mdi-eye</v-icon>
                                            </v-btn>
                                            <v-btn icon variant="text" @click="deleteFile(file)">
                                                <v-icon>mdi-delete</v-icon>
                                            </v-btn>
                                        </v-list-item-action>
                                    </template>
                                </v-list-item>
                            </v-list>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-main>
    </v-app>
</template>

<script lang="ts">
import { MetaData, FileData, axios, UserProperty } from "@/api"
import { useAppStore } from "@/store/app"
const appStore = useAppStore()
import { replaceLastPartOfUrl, humanFileSize } from "@/utils"
import { Buffer } from 'buffer'
import { timeDeltaToString } from "@/plugins/i18n"
import CryptoJS from 'crypto-js'
import { showDetailWarning, showAutoCloseSuccess, cancelableInput, dangerousConfirm } from "@/plugins/swal"
import { isAxiosError } from 'axios'
import { SweetAlertResult } from "sweetalert2"

export default {
    data() {
        return {
            clip_version: 1,
            remote_version: 1,
            local_content: "",
            remote_content: "",
            last_updated: Date.now(),
            save_status: "",
            save_interval: 3 * 1000,
            is_new: false,
            metadata: {} as MetaData,
            password: "",
            current_timeout: -1,
            selected_timeout: "",
            current_url: window.location.href,
            readonly_name: "",
            is_readonly: false,
            uploading: false,
            file_to_upload: [] as File[],
            remote_files: [] as FileData[],
            is_local_outdated: false,
            auto_fetch_remote_content: false,
            auto_fetch_remote_content_min_idle_time: 5 * 1000,
            auto_fetch_remote_content_interval: 5 * 1000,
            last_edit_time: Date.now(),
            user_property: {} as UserProperty,
            sidebar_list_opened: [],
            encrypt_text_content: false,
        }
    },
    methods: {
        // UI / UX
        humanFileSize: humanFileSize,
        timeDeltaToString: timeDeltaToString,
        goToHome() {
            this.$router.push({ name: "Home" })
        },
        async setEditingStatus() {
            this.last_edit_time = Date.now()
            if (this.is_readonly) return
            this.save_status = "editing"
        },
        // create / fetch / push / delete
        async requestPassword(): Promise<SweetAlertResult<any>> {
            return cancelableInput({
                title: this.$t('clip.password_question'),
                input: "password",
            })
        },
        async createIfNotExist() {
            if (!this.is_new) return
            try {
                let response = await axios.post(`/note/${this.name}`, {})
                await this.fetchContent(true)
                this.is_new = false
            } catch (e: any) {
                console.log(e)
            }
        },
        async fetchContent(no_update_content = false) {
            try {
                let response
                try {
                    response = await axios.get(`/note/${this.name}`)
                } catch (e: any) {
                    if (isAxiosError(e)) {
                        if (e.response?.status === 400) {
                            showDetailWarning({ title: this.$t('clip.Error'), text: this.$t('clip.invalid_note_name') })
                                .then(this.goToHome)
                            return
                        } else if (e.response?.status === 401) {
                            this.requestPassword().then((result) => {
                                if (result.isConfirmed) {
                                    this.password = result.value as string
                                    this.fetchContent()
                                } else {
                                    this.goToHome()
                                }
                            })
                            return
                        }
                    }
                    throw e
                }
                if (response.status === 204) {
                    this.is_new = true
                    this.save_status = "new"
                    this.local_content = ""
                    this.remote_content = ""
                    this.remote_version = this.clip_version = 1
                    return
                } else {
                    try {
                        this.user_property = JSON.parse(response.data.data.user_property) as UserProperty
                    }
                    catch {
                        this.user_property = {} as UserProperty
                        console.log(response.data.data.user_property)
                        showDetailWarning({
                            title: this.$t('clip.Error'),
                            text: this.$t('clip.failed_to_parse_user_property')
                        })
                    }
                    this.encrypt_text_content = this.user_property.encrypt_text_content ?? false
                    let content = response.data.data.content
                    if (this.user_property.encrypt_text_content) {
                        if (this.user_property.encrypt_text_content_algo === "aes") {
                            content = CryptoJS.AES.decrypt(content, this.encryptPassword).toString(CryptoJS.enc.Utf8)
                        }
                        else {
                            showDetailWarning({
                                title: this.$t('clip.Error'),
                                text: this.$t('clip.encrypt_text_content_algo_not_supported')
                            })
                        }
                    }
                    if (!no_update_content) {
                        this.local_content = content
                    }
                    this.current_timeout = response.data.data.timeout_seconds
                    this.selected_timeout = timeDeltaToString(this.current_timeout)
                    this.remote_content = content
                    this.remote_version = this.clip_version = (response.data.data.clip_version ?? 1)
                    this.readonly_name = response.data.data.readonly_name
                    this.is_readonly = response.data.data.is_readonly
                    this.remote_files = response.data.data.files
                    this.is_local_outdated = false
                    if (this.save_status === "local_outdated") {
                        this.save_status = "conflict_resolved"
                    }
                }
            } catch (e: any) {
                console.log(e)
            }
        },
        async pushContentIfChanged() {
            if (this.local_content != this.remote_content) {
                this.pushContent()
            }
        },
        async pushContent(force = false) {
            if (this.is_readonly) return
            if (this.save_status === "saving") return
            if (!force && this.is_local_outdated) return
            if (force) this.clip_version = this.remote_version
            this.last_updated = Date.now()
            this.save_status = "saving"
            await this.createIfNotExist()
            let content = this.local_content
            if (this.encrypt_text_content) {
                if (this.user_property.encrypt_text_content_algo === "aes") {
                    content = CryptoJS.AES.encrypt(content, this.encryptPassword).toString()
                }
                else {
                    showDetailWarning(
                        {
                            title: this.$t('clip.Error'),
                            text: this.$t('clip.encrypt_text_content_algo_not_supported')
                        }
                    )
                    return
                }
            }
            try {
                let response = await axios.put(`/note/${this.name}`, {
                    user_property: JSON.stringify(this.user_property),
                    content: content,
                    clip_version: this.clip_version,
                })
                this.clip_version = response.data.data.clip_version
                this.fetchContent(true)
                this.save_status = "saved"
            } catch (e: any) {
                if (isAxiosError(e)) {
                    if (e.response?.status === 409) {
                        this.remote_version = e.response.data.data.clip_version
                        this.is_local_outdated = true
                        this.save_status = "local_outdated"
                        return
                    }
                }
                console.log(e)
                this.save_status = "error"
            }
        },
        async deleteContent() {
            dangerousConfirm({
                title: this.$t('clip.delete.are_you_sure'),
                text: this.$t('clip.delete.you_wont_be_able_to_revert_this'),
                confirmButtonText: this.$t('clip.delete.yes_delete_it'),
            })
                .then(async (result) => {
                    if (result.isConfirmed) {
                        try {
                            let response = await axios.delete(`/note/${this.name}`)
                            showAutoCloseSuccess({
                                title: this.$t('clip.delete.deleted'),
                                text: this.$t('clip.delete.your_clip_has_been_deleted'),
                                timer: undefined
                            })
                                .then(this.goToHome)
                        } catch (e: any) {
                            console.log(e)
                        }
                    }
                })
        },
        // file
        getTotalSize(...file_arrays: (File[] | FileData[])[]): number {
            let total_size = 0
            file_arrays.forEach((files) => {
                files.forEach((file) => {
                    total_size += file.size
                })
            })
            return total_size
        },
        async uploadSingleFile(file: File) {
            var formData = new window.FormData()
            formData.append("file", file)
            await axios.post(`/note/${this.name}/file/0`, formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            })
        },
        async uploadFile() {
            await this.createIfNotExist()
            if (this.file_to_upload.length === 0) return
            this.uploading = true
            let error_string = null
            let file_count = this.file_to_upload.length + this.remote_files.length
            if (this.metadata.max_file_count && file_count > this.metadata.max_file_count) {
                error_string = this.$t('clip.file.error.TOTAL_FILES_COUNT_LIMIT_HIT')
            }
            this.file_to_upload.forEach((file) => {
                if (this.metadata.max_file_size && file.size > this.metadata.max_file_size) {
                    error_string = this.$t('clip.file.error.SINGLE_FILE_SIZE_LIMIT_HIT')
                }
            })
            let total_size = this.getTotalSize(this.file_to_upload, this.remote_files)

            if (this.metadata.max_all_file_size && total_size > this.metadata.max_all_file_size) {
                error_string = this.$t('clip.file.error.TOTAL_FILES_SIZE_LIMIT_HIT')
            }
            if (error_string !== null) {
                showDetailWarning({
                    title: this.$t('clip.Error'), text: error_string
                })
                this.file_to_upload = []
                this.uploading = false
                return
            }
            try {
                await Promise.all(this.file_to_upload.map(this.uploadSingleFile))
                this.fetchContent(true)
                showAutoCloseSuccess({
                    title: this.$t('clip.file.uploaded'),
                    text: this.$t('clip.file.your_file_has_been_uploaded'),
                })
            }
            catch (e: any) {
                console.log(e)
                error_string = this.$t('clip.file.failed_to_upload_file')
                if (isAxiosError(e)) {
                    if (e.response?.status === 400 && e.response?.data?.error_id !== null) {
                        error_string = this.$t('clip.file.error.' + e.response.data.error_id)
                    }
                }
                showDetailWarning(
                    {
                        title: this.$t('clip.Error'),
                        text: error_string
                    }
                )
            } finally {
                this.file_to_upload = []
                this.uploading = false
                this.fetchContent(true)
            }
        },
        async downloadFile(file: FileData) {
            window.open(file.download_url, "_self")
        },
        async previewFile(file: FileData) {
            window.open(file.preview_url, "_blank")
        },
        async deleteFile(file: FileData) {
            this.uploading = true
            try {
                let response = await axios.delete(`/note/${this.name}/file/${file.id}`)
                this.fetchContent(true)
                showAutoCloseSuccess({
                    title: this.$t('clip.file.deleted'),
                    text: this.$t('clip.file.your_file_has_been_deleted'),
                })
            } catch (e: any) {
                console.log(e)
                showDetailWarning({ title: this.$t('clip.Error'), text: this.$t('clip.file.failed_to_delete_file') })
            } finally {
                this.uploading = false
            }
        },
        // password
        async changePassword() {
            let password = (
                await cancelableInput({
                    title: this.$t('clip.new_password_question'),
                    input: "password",
                })
            ).value
            if (password === undefined) return
            try {
                await axios.put(`/note/${this.name}`, {
                    new_password: password === "" ? "" : CryptoJS.SHA512(password).toString(),
                })
                this.password = password
                await this.updateEncryptText()
                showAutoCloseSuccess({
                    title: this.$t('clip.password_changed'),
                })
            } catch (e: any) {
                console.log(e)
            }
        },
        async updateEncryptText() {
            if (this.encrypt_text_content) {
                this.user_property.encrypt_text_content = true
                this.user_property.encrypt_text_content_algo = "aes"
            }
            else {
                this.user_property.encrypt_text_content = false
                this.user_property.encrypt_text_content_algo = ""
            }
            await this.pushContent()
        },
        async setNoteTimeout(selected_timeout: string) {
            await this.createIfNotExist()
            try {
                let new_timeout = undefined
                this.timeout_selections.forEach((timeout) => {
                    if (timeDeltaToString(timeout) === selected_timeout) {
                        new_timeout = timeout
                    }
                })


                let invalid_timeout_toast = () => {
                    showDetailWarning({ title: this.$t('clip.Error'), text: this.$t('clip.invalid_timeout') })
                }

                if (new_timeout === undefined) {
                    invalid_timeout_toast()
                    return
                }
                try {
                    let response = await axios.put(`/note/${this.name}`, {
                        timeout_seconds: new_timeout,
                    })
                    this.current_timeout = new_timeout
                } catch (e: any) {
                    if (isAxiosError(e)) {
                        if (e.response?.status === 400) {
                            invalid_timeout_toast()
                            return
                        }
                    }
                    console.log(e)
                }
            } catch (e: any) {
                console.log(e)
            }
        },
        // useful features
        async copyString(content: string) {
            if (!content) return
            if (navigator?.clipboard?.writeText === undefined) {
                // http fallback
                // https://blog.csdn.net/qq_58340302/article/details/124480086
                let textArea = document.createElement('textarea')
                textArea.value = content
                document.body.appendChild(textArea)
                textArea.focus()
                textArea.select()
                return new Promise((res, rej) => {
                    document.execCommand('copy') ? res(null) : rej()
                    textArea.remove()
                })
            }
            try {
                await navigator.clipboard.writeText(content)
            } catch (e: any) {
                console.log(e)
            }
        },
        async downloadContent() {
            // save as blob
            const blob = new Blob([this.local_content], { type: "text/plain" })
            const url = window.URL.createObjectURL(blob)
            const tmpLink = document.createElement("a")
            tmpLink.href = url
            tmpLink.download = `${this.name}.txt`
            document.body.appendChild(tmpLink)
            tmpLink.click()
            document.body.removeChild(tmpLink)
            URL.revokeObjectURL(url)
        },
        // readonly url
        async toggleReadonlyUrl() {
            try {
                let response = await axios.put(`/note/${this.name}`, {
                    enable_readonly: !this.hasReadonlyName
                })
                this.fetchContent()
            } catch (e: any) {
                console.log(e)
            }
        }
    },
    computed: {
        name(): string {
            return this.$route.params.name as string
        },
        encryptPassword(): string {
            return CryptoJS.SHA256(this.password).toString()
        },
        timeout_selections(): number[] {
            return this.metadata.timeout_selections || []
        },
        hasReadonlyName(): boolean {
            return this.readonly_name !== ""
        },
        readonly_url(): string {
            return replaceLastPartOfUrl(
                window.location.href,
                this.readonly_name
            )
        },
        readonly_url_check_empty(): string {
            return this.hasReadonlyName ? this.readonly_url : " "
        },
    },
    mounted() {
        // add auth header
        axios.interceptors.request.use((config) => {
            config.headers["Authorization"] = `Bearer ${Buffer.from(CryptoJS.SHA512(this.password).toString(), 'utf8').toString('base64')}`
            return config
        })

        // fetch metadata
        appStore.metadata().then((metadata) => {
            this.metadata = metadata as MetaData
        }).catch((e) => {
            console.log(e)
            showDetailWarning(
                {
                    title: this.$t('clip.Error'),
                    text: this.$t('clip.failed_to_fetch_metadata')
                }
            ).then(this.goToHome)
        })

        // auto save
        setInterval(() => {
            if (Date.now() - this.last_updated > this.save_interval) {
                this.pushContentIfChanged()
            }
        }, this.save_interval)

        // auto update
        setInterval(
            () => {
                if (this.auto_fetch_remote_content && Date.now() - this.last_edit_time > this.auto_fetch_remote_content_min_idle_time) {
                    this.fetchContent()
                }
            }, this.auto_fetch_remote_content_interval
        )

        // first fetch
        this.fetchContent()
    }
}
</script>

<style>
/* show pointer cursor for `click to copy`*/
.cursor-pointer * {
    cursor: pointer;
}

/*remove useless padding in sidebar*/
#sidebar .v-input__details {
    display: none;
}

#sidebar .v-list {
    padding: 0;
}
</style>
