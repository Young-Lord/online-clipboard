<template>
    <v-app>
        <v-app-bar app>
            <v-btn icon @click="this.$router.push({ name: 'Home' })">
                <v-icon>mdi-home</v-icon>
            </v-btn>
            <!-- sync button if outdated-->
            <v-btn icon @click="fetchContent(false)" v-if="this.is_local_outdated">
                <v-icon>mdi-download</v-icon>
            </v-btn>
            <!-- sync button if outdated-->
            <v-btn icon @click="pushContent(true)" v-if="this.is_local_outdated">
                <v-icon>mdi-upload</v-icon>
            </v-btn>
            <!-- saved status in plaintext -->
            <v-toolbar-title>{{ save_status ? $t(`save_status.${save_status}`) : '' }}</v-toolbar-title>
            <v-spacer></v-spacer>
            <!--delete button-->
            <v-btn icon @click="deleteContent" v-if="!this.is_new && !this.is_readonly">
                <v-icon>mdi-delete</v-icon>
            </v-btn>
            <!-- password button-->
            <v-btn icon @click="changePassword" v-if="!this.is_new && !this.is_readonly">
                <v-icon>mdi-lock</v-icon>
            </v-btn>
            <!--save button-->
            <v-btn icon @click="pushContent" v-if="!this.is_readonly">
                <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <!-- copy button-->
            <v-btn icon @click="copyString(local_content)">
                <v-icon>mdi-content-copy</v-icon>
            </v-btn>
            <!-- download button-->
            <v-btn icon @click="downloadContent">
                <v-icon>mdi-download</v-icon>
            </v-btn>
        </v-app-bar>

        <v-main>
            <v-container>
                <v-row rows="12">
                    <v-col cols="12" md="8">
                        <!-- Larger Text Input Box -->
                        <v-textarea rows="15" variant="outlined" auto-grow v-model="local_content" @input="setEditingStatus"
                            @keydown.ctrl.s.exact="pushContentIfChanged" @keydown.ctrl.s.exact.prevent
                            @focusout="pushContentIfChanged">
                        </v-textarea>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card id="sidebar">
                            <!-- 下拉框，选择过期时间 -->
                            <v-select
                                v-bind:items="timeout_keys.map((key) => { return $t('clip.timeout_selections.' + key) })"
                                :label="$t('clip.expiration')" @update:model-value="setNoteTimeout"
                                v-model="selected_timeout" prepend-inner-icon="mdi-clock"
                                v-if="!this.is_new && !this.is_readonly">
                            </v-select>
                            <!-- current url, click to copy-->
                            <v-text-field :label="$t('clip.current_url_click_to_copy')" v-model="current_url" readonly
                                prepend-inner-icon="mdi-link" @click="copyString(current_url)" class="cursor-pointer"
                                v-if="!this.is_readonly">
                            </v-text-field>
                            <!-- readonly url, click to copy-->
                            <v-text-field :label="$t('clip.readonly_url_click_to_copy')" v-model="readonly_url" readonly
                                prepend-inner-icon="mdi-link" v-if="this.readonly_url" @click="copyString(readonly_url)"
                                class="cursor-pointer">
                            </v-text-field>
                            <!-- checkbox for auto fetch cloud version -->
                            <v-checkbox v-model="auto_fetch_remote_content" :label="$t('clip.auto_fetch_remote_content')"
                                v-if="!this.is_new">
                            </v-checkbox>
                        </v-card>
                    </v-col>
                    <v-col cols="12">
                        <v-card id="file-card">
                            <!-- Drag or click to upload file -->
                            <v-file-input :label="$t('clip.drag_or_click_to_upload_file')" prepend-icon="mdi-file-upload"
                                @change="uploadFile" v-if="!this.is_readonly && !this.is_new" :disabled="this.uploading"
                                v-model="file_to_upload">
                            </v-file-input>
                            <!--all files, with download and delete button-->
                            <v-list v-if="!this.is_new">
                                <v-list-item v-for="file in remote_files" :key="file.id">
                                    <v-list-item-title>{{ file.filename }}
                                    </v-list-item-title>
                                    <v-list-item-subtitle>{{ humanFileSize(file.size) }} {{
                                        $t('clip.file.expiration_date_is') }}{{ $d(new Date(file.expire_at), 'long')
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

<script>
import { axios } from "@/api"
import { useAppStore } from "@/store/app"
const appStore = useAppStore()
import { getKeyByValue, replaceLastPartOfUrl, humanFileSize } from "@/utils"
import { Buffer } from 'buffer'

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
            meta_data: {},
            password: "",
            timeout_keys: Object.keys(appStore.timeout_selections),
            current_timeout: -1,
            selected_timeout: "",
            current_url: window.location.href,
            readonly_url: "",
            is_readonly: false,
            uploading: false,
            file_to_upload: null,
            remote_files: [],
            is_local_outdated: false,
            auto_fetch_remote_content: false,
            auto_fetch_remote_content_min_idle_time: 5 * 1000,
            auto_fetch_remote_content_interval: 5 * 1000,
            last_edit_time: Date.now()
        }
    },
    methods: {
        humanFileSize: humanFileSize,
        async createIfNotExist() {
            if (!this.is_new) return
            try {
                let response = await axios.post(`/note/${this.name}`, {})
                await this.fetchContent(true)
                this.is_new = false
            } catch (e) {
                console.log(e)
            }
        },
        async uploadFile() {
            await this.createIfNotExist()
            this.uploading = true
            var formData = new window.FormData()
            formData.append("file", this.file_to_upload[0])
            try {
                let response = await axios.post(`/note/${this.name}/file/0`, formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                })
                this.fetchContent()
                this.$swal
                    .fire({
                        title: this.$t('clip.file.uploaded'),
                        text: this.$t('clip.file.your_file_has_been_uploaded'),
                        icon: "success",
                        timer: 1200,
                        confirmButtonText: this.$t('clip.ok'),
                    })
            } catch (e) {
                console.log(e)
                this.$swal.fire({
                    title: this.$t('clip.Error'),
                    text: this.$t('clip.file.failed_to_upload_file'),
                    icon: "error",
                    confirmButtonText: this.$t('clip.ok'),
                })
            } finally {
                this.file_to_upload = null
                this.uploading = false
            }
        },
        async downloadFile(file) {
            window.open(file.download_url, "_blank")
        },
        async previewFile(file) {
            window.open(file.preview_url, "_blank")
        },
        async deleteFile(file) {
            this.uploading = true
            try {
                let response = await axios.delete(`/note/${this.name}/file/${file.id}`)
                this.fetchContent()
                this.$swal
                    .fire({
                        title: this.$t('clip.file.deleted'),
                        text: this.$t('clip.file.your_file_has_been_deleted'),
                        icon: "success",
                        timer: 1200,
                        confirmButtonText: this.$t('clip.ok'),
                    })
            } catch (e) {
                console.log(e)
                this.$swal.fire({
                    title: this.$t('clip.Error'),
                    text: this.$t('clip.file.failed_to_delete_file'),
                    icon: "error",
                    confirmButtonText: this.$t('clip.ok'),
                })
            } finally {
                this.uploading = false
            }
        },
        async setEditingStatus() {
            this.last_edit_time = Date.now()
            if (this.is_readonly) return
            this.save_status = "editing"
        },
        async fetchContent(no_update_content = false) {
            try {
                let response
                try {
                    response = await axios.get(`/note/${this.name}`)
                } catch (e) {
                    if (e.response?.status == 400) {
                        this.$swal
                            .fire({
                                title: this.$t('clip.Error'),
                                text: this.$t('clip.invalid_note_name'),
                                icon: "error",
                                confirmButtonText: this.$t('clip.ok'),
                            })
                            .then(() => {
                                this.$router.push({ name: "Home" })
                            })
                    } else if (e.response?.status == 401) {
                        this.$swal
                            .fire({
                                title: this.$t('clip.password_question'),
                                input: "password",
                                showCancelButton: true,
                                cancelButtonText: this.$t('clip.cancel'),
                                confirmButtonText: this.$t('clip.ok'),
                            })
                            .then((result) => {
                                if (result.isConfirmed) {
                                    this.password = result.value
                                    this.fetchContent()
                                } else {
                                    this.$router.push({ name: "Home" })
                                }
                            })
                    } else throw e
                    return
                }
                if (response.status == 204) {
                    this.is_new = true
                    this.save_status = "new"
                    this.local_content = ""
                    this.remote_content = ""
                    this.remote_version = this.clip_version = 1
                    return
                } else {
                    if (!no_update_content) {
                        this.local_content = response.data.data.content
                    }
                    this.current_timeout = response.data.data.timeout_seconds
                    this.selected_timeout = this.getNoteTimeoutString()
                    this.remote_content = response.data.data.content
                    this.remote_version = this.clip_version = (response.data.data.clip_version ?? 1)
                    this.readonly_url = replaceLastPartOfUrl(
                        window.location.href,
                        response.data.data.readonly_name
                    )
                    this.is_readonly = response.data.data.is_readonly
                    this.remote_files = response.data.data.files
                    this.is_local_outdated = false
                    if (this.save_status == "local_outdated") {
                        this.save_status = "conflict_resolved"
                    }
                }
            } catch (e) {
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
            if (this.save_status == "saving") return
            if (!force && this.is_local_outdated) return
            if(force) this.clip_version = this.remote_version
            this.last_updated = Date.now()
            this.save_status = "saving"
            await this.createIfNotExist()
            try {
                let response = await axios.put(`/note/${this.name}`, {
                    content: this.local_content,
                    clip_version: this.clip_version,
                })
                this.clip_version = response.data.data.clip_version
                this.fetchContent()
                this.save_status = "saved"
            } catch (e) {
                if (e.response?.status == 409) {
                    this.remote_version = e.response.data.data.clip_version
                    this.is_local_outdated = true
                    this.save_status = "local_outdated"
                    return
                }
                console.log(e)
                this.save_status = "error"
            }
        },
        async deleteContent() {
            this.$swal
                .fire({
                    title: this.$t('clip.delete.are_you_sure'),
                    text: this.$t('clip.delete.you_wont_be_able_to_revert_this'),
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#d33",
                    cancelButtonColor: "#3085d6",
                    confirmButtonText: this.$t('clip.delete.yes_delete_it'),
                    cancelButtonText: this.$t('clip.cancel'),
                })
                .then(async (result) => {
                    if (result.isConfirmed) {
                        try {
                            let response = await axios.delete(`/note/${this.name}`)
                            this.$swal
                                .fire({
                                    title: this.$t('clip.delete.deleted'),
                                    text: this.$t('clip.delete.your_clip_has_been_deleted'),
                                    icon: "success",
                                    confirmButtonText: this.$t('clip.ok'),
                                })
                                .then(() => {
                                    this.$router.push({ name: "Home" })
                                })
                        } catch (e) {
                            console.log(e)
                        }
                    }
                })
        },
        async changePassword() {
            let password = (
                await this.$swal({
                    title: this.$t('clip.password_question'),
                    input: "password",
                    showCancelButton: true,
                    cancelButtonText: this.$t('clip.cancel'),
                })
            ).value
            if (password === undefined) return
            try {
                let response = await axios.put(`/note/${this.name}`, {
                    new_password: password,
                })
                this.$swal({
                    title: this.$t('clip.password_changed'),
                    icon: "success",
                    timer: 1200,
                })
                this.password = password
            } catch (e) {
                console.log(e)
            }
        },
        async setNoteTimeout(selected_timeout) {
            await this.createIfNotExist()
            try {
                let new_timeout_key = undefined
                this.timeout_keys.forEach((key) => {
                    if (this.$t('clip.timeout_selections.' + key) === selected_timeout) {
                        new_timeout_key = key
                    }
                })

                let new_timeout = appStore.timeout_selections[new_timeout_key]

                let invalid_timeout_toast = () => {
                    this.$swal({
                        title: this.$t('clip.invalid_timeout'),
                        icon: "error",
                    })
                }

                if (new_timeout_key === undefined || new_timeout === undefined) {
                    invalid_timeout_toast()
                    return
                }
                try {
                    let response = await axios.put(`/note/${this.name}`, {
                        timeout_seconds: new_timeout,
                    })
                    this.timeout_seconds = new_timeout
                } catch (e) {
                    console.log(e)
                    if (e.response?.status == 400) {
                        invalid_timeout_toast()
                        return
                    }
                }
            } catch (e) {
                console.log(e)
            }
        },
        getNoteTimeoutString() {
            let matched_key = getKeyByValue(
                appStore.timeout_selections,
                this.current_timeout
            )

            if (this.current_timeout == -1) return this.$t('clip.timeout_selections.never')
            if (matched_key !== undefined) return this.$t('clip.timeout_selections.' + matched_key)
            if (this.current_timeout <= 3600)
                return `${this.current_timeout / 60} minutes`
            return `${this.current_timeout / 3600} hours`
        },
        async copyString(content) {
            try {
                await navigator.clipboard.writeText(content)
            } catch (e) {
                console.log(e)
            }
        },
        async downloadContent() {
            // blob
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
    },
    computed: {
        name() {
            return this.$route.params.name
        },
    },
    mounted() {
        setInterval(() => {
            if (Date.now() - this.last_updated > this.save_interval) {
                this.pushContentIfChanged()
            }
        }, this.save_interval)

        setInterval(
            () => {
                if (this.auto_fetch_remote_content && Date.now() - this.last_edit_time > this.auto_fetch_remote_content_min_idle_time) {
                    this.fetchContent()
                }
            }, this.auto_fetch_remote_content_interval
        )

        axios.interceptors.request.use((config) => {
            config.headers["Authorization"] = `Bearer ${Buffer.from(this.password, 'utf8').toString('base64')}`
            return config
        })
    },
    beforeMount() {
        this.fetchContent()
    },
}
</script>

<style>
.cursor-pointer * {
    cursor: pointer;
}

#sidebar>.v-input>.v-input__details {
    display: none;
}
</style>
