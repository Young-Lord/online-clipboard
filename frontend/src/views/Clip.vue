<template>
    <v-app @drop="onAttachFile" @dragover.prevent>
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
            <v-toolbar-title>{{
                save_status ? $t(`save_status.${save_status}`) : ""
            }}</v-toolbar-title>
            <!--Vue issue: https://github.com/vuejs/core/issues/5312-->
            <template v-slot:[should_wrap_appbar_to_slot]>
                <v-spacer></v-spacer>
                <!--delete button-->
                <v-btn
                    icon
                    @click="deleteContent()"
                    v-if="!is_new && !is_readonly"
                >
                    <v-icon>mdi-delete</v-icon>
                </v-btn>
                <!-- password button-->
                <v-btn
                    icon
                    @click="changePassword()"
                    v-if="!is_new && !is_readonly"
                >
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
            </template>
        </v-app-bar>

        <v-main>
            <v-container>
                <v-row rows="12">
                    <v-col cols="12" md="8">
                        <!-- Larger Text Input Box -->
                        <v-textarea
                            rows="15"
                            variant="outlined"
                            auto-grow
                            v-model="local_content"
                            @input="setEditingStatusOnEdit()"
                            @keydown.ctrl.s.exact="pushContentIfChanged()"
                            @keydown.ctrl.s.exact.prevent
                            @focusout="pushContentIfChanged()"
                            @paste="onAttachFile"
                        >
                        </v-textarea>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-card id="sidebar">
                            <!-- 下拉框，选择过期时间 -->
                            <v-select
                                v-bind:items="
                                    timeout_selections.map((key) => {
                                        return timeDeltaToString(key)
                                    })
                                "
                                :label="$t('clip.expiration')"
                                @update:model-value="setNoteTimeout"
                                v-model="selected_timeout"
                                prepend-inner-icon="mdi-clock"
                                v-if="!is_new && !is_readonly"
                            >
                            </v-select>
                            <!-- current url, click to copy-->
                            <v-text-field
                                :label="$t('clip.current_url_click_to_copy')"
                                v-model="current_url"
                                readonly
                                prepend-inner-icon="mdi-link"
                                @click="copyString(current_url)"
                                class="cursor-pointer"
                                v-if="!is_readonly"
                            >
                            </v-text-field>
                            <!-- readonly url, click to copy-->
                            <v-text-field
                                v-if="!is_new"
                                :label="
                                    hasReadonlyName
                                        ? $t('clip.readonly_url_click_to_copy')
                                        : $t('clip.readonly_url_is_disabled')
                                "
                                v-model="readonly_url_check_empty"
                                readonly
                                prepend-inner-icon="mdi-link"
                                @click="
                                    hasReadonlyName && copyString(readonly_url)
                                "
                                class="cursor-pointer"
                                :append-inner-icon="
                                    is_readonly
                                        ? undefined
                                        : hasReadonlyName
                                        ? 'mdi-delete'
                                        : 'mdi-plus-circle-outline'
                                "
                                @click:append-inner.stop="toggleReadonlyUrl()"
                            >
                            </v-text-field>
                            <v-list
                                v-model:opened="sidebar_list_opened"
                                v-if="!is_new"
                            >
                                <v-list-group>
                                    <template v-slot:activator="{ props }">
                                        <v-list-item
                                            v-bind="props"
                                            prepend-icon="mdi-cog"
                                            :title="
                                                $t('clip.advanced_settings')
                                            "
                                        ></v-list-item>
                                    </template>
                                    <!--prepend single line message-->
                                    <v-text-field
                                        v-model="combine_content"
                                        :label="$t('clip.prepend_message')"
                                        :disabled="
                                            user_property.encrypt_text_content ===
                                            true
                                        "
                                        outlined
                                        dense
                                        @keydown.enter.exact="
                                            combinePushContent()
                                        "
                                        append-inner-icon="mdi-comment-arrow-right"
                                        @click:append-inner="
                                            combinePushContent()
                                        "
                                        v-if="!is_readonly"
                                    >
                                    </v-text-field>
                                    <!-- save interval -->
                                    <v-text-field
                                        v-model="save_interval"
                                        :label="$t('clip.auto_save_interval')"
                                        outlined
                                        dense
                                        type="number"
                                        @keyup="onUpdateSaveInterval()"
                                        v-if="!is_readonly"
                                    >
                                    </v-text-field>
                                    <!-- auto fetch remote content interval -->
                                    <v-text-field
                                        v-model="fetch_interval"
                                        :label="$t('clip.auto_fetch_interval')"
                                        outlined
                                        dense
                                        type="number"
                                        @keyup="onUpdateFetchInterval()"
                                    >
                                    </v-text-field>
                                    <!-- checkbox for encrypt text content / file -->
                                    <v-checkbox
                                        v-model="encrypt_text_content"
                                        :label="$t('clip.encrypt_content')"
                                        v-if="!is_readonly"
                                        @change="updateEncryptText()"
                                    >
                                    </v-checkbox>
                                    <v-checkbox
                                        v-model="encrypt_file"
                                        :label="$t('clip.encrypt_file')"
                                        v-if="!is_readonly"
                                        :disabled="uploading"
                                        @change="updateEncryptFile()"
                                    >
                                    </v-checkbox>
                                    <!--send by mail-->
                                    <v-text-field
                                        v-model="mail_address"
                                        :label="$t('clip.mail.send_to_mail')"
                                        outlined
                                        dense
                                        @keydown.enter.exact="sendToMail()"
                                        append-inner-icon="mdi-email-fast"
                                        @click:append-inner="sendToMail()"
                                        v-if="allow_mail"
                                    >
                                    </v-text-field>
                                    <!--report clip-->
                                    <v-list-item
                                        prepend-icon="mdi-alert-octagon"
                                        @click="reportClip()"
                                    >
                                        <v-list-item-title>{{
                                            $t("clip.report.report_clip")
                                        }}</v-list-item-title>
                                    </v-list-item>
                                </v-list-group>
                            </v-list>
                        </v-card>
                    </v-col>
                    <v-col cols="12">
                        <v-card
                            id="file-card"
                            v-if="!is_readonly || remote_files.length"
                        >
                            <!-- Drag or click to upload file -->
                            <v-file-input
                                :label="$t('clip.drag_or_click_to_upload_file')"
                                :messages="
                                    $t('clip.file_limits', [
                                        humanFileSize(metadata.max_file_size),
                                        remote_files.length,
                                        metadata.max_file_count,
                                        humanFileSize(
                                            getTotalSize(remote_files)
                                        ),
                                        humanFileSize(
                                            metadata.max_all_file_size
                                        ),
                                    ])
                                "
                                prepend-icon="mdi-file-upload"
                                @change="uploadFile()"
                                v-if="
                                    !is_readonly &&
                                    metadata.max_file_count > 0 &&
                                    metadata.max_all_file_size > 0
                                "
                                :disabled="
                                    uploading ||
                                    metadata.max_file_count <=
                                        remote_files.length ||
                                    metadata.max_all_file_size <=
                                        getTotalSize(remote_files)
                                "
                                v-model="file_to_upload"
                                multiple
                            >
                            </v-file-input>
                            <!--all files, with download and delete button-->
                            <v-list>
                                <v-list-item
                                    v-for="file in remote_files"
                                    :key="file.id"
                                >
                                    <v-list-item-title
                                        >{{ mayDecryptFilename(file.filename) }}
                                    </v-list-item-title>
                                    <v-list-item-subtitle
                                        >{{ humanFileSize(file.size) }}
                                        {{
                                            $t("clip.file.expiration_date_is", [
                                                $d(
                                                    new Date(file.expire_at),
                                                    "long"
                                                ),
                                            ])
                                        }}</v-list-item-subtitle
                                    >
                                    <template v-slot:append>
                                        <v-list-item-action end>
                                            <!--tabindex=-1 make it not focusable-->
                                            <a
                                                :href="file.download_url"
                                                target="_self"
                                                style="
                                                    color: inherit;
                                                    text-decoration: none;
                                                "
                                                tabindex="-1"
                                                v-if="!encrypt_file"
                                            >
                                                <v-btn icon variant="text">
                                                    <v-icon
                                                        >mdi-download</v-icon
                                                    >
                                                </v-btn>
                                            </a>
                                            <v-btn
                                                icon
                                                variant="text"
                                                @click="
                                                    downloadEncryptedFile(file)
                                                "
                                                v-else
                                            >
                                                <v-icon>mdi-download</v-icon>
                                            </v-btn>
                                            <a
                                                :href="file.preview_url"
                                                target="_blank"
                                                style="
                                                    color: inherit;
                                                    text-decoration: none;
                                                "
                                                tabindex="-1"
                                                v-if="!encrypt_file"
                                            >
                                                <v-btn icon variant="text">
                                                    <v-icon>mdi-eye</v-icon>
                                                </v-btn>
                                            </a>
                                            <v-btn
                                                icon
                                                variant="text"
                                                @click="deleteFile(file)"
                                                v-if="!is_readonly"
                                            >
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
import {
    MetaData,
    FileData,
    axios,
    UserProperty,
    Response,
    ClipData,
} from "@/api"
import { useAppStore } from "@/store/app"
const appStore = useAppStore()
import { replaceLastPartOfUrl, humanFileSize, assert } from "@/utils"
import { Buffer } from "buffer"
import { timeDeltaToString } from "@/plugins/i18n"
import AES from "crypto-js/aes"
import SHA256 from "crypto-js/sha256"
import SHA512 from "crypto-js/sha512"
import utf8 from "crypto-js/enc-utf8"
import WordArray from "crypto-js/lib-typedarrays"
import {
    showDetailWarning,
    showAutoCloseSuccess,
    cancelableInput,
    dangerousConfirm,
} from "@/plugins/swal"
import { AxiosResponse, isAxiosError } from "axios"
import { SweetAlertResult } from "sweetalert2"
import { onBeforeRouteLeave } from "vue-router"

enum SaveStatus {
    // Current status displayed on top left. The values are used to get i18n string.
    empty = "",
    new = "new",
    error = "error",
    saving = "saving",
    saved = "saved",
    editing = "editing",
    local_outdated = "local_outdated",
    conflict_resolved = "conflict_resolved",
}
const UnsavedSaveStatus = new Set([
    SaveStatus.error,
    SaveStatus.saving,
    SaveStatus.editing,
    SaveStatus.local_outdated,
])

export default {
    data() {
        return {
            first_fetched: false,
            clip_version: 1,
            remote_version: 1,
            local_content: "",
            remote_content: "",
            last_saved: Date.now(),
            save_status: SaveStatus.empty,
            is_new: false,
            metadata: appStore.metadata,
            password: "",
            current_timeout: -1,
            selected_timeout: "",
            current_url: window.location.href,
            readonly_name: "",
            is_readonly: false,
            uploading: false,
            file_to_upload: [] as File[],
            remote_files: [] as FileData[],
            save_interval: 3 as number | string,
            fetch_min_idle_time: 1,
            fetch_interval: 0 as number | string,
            save_timer: null as ReturnType<typeof setTimeout> | null,
            fetch_timer: null as ReturnType<typeof setTimeout> | null,
            last_edit_time: Date.now(),
            user_property: {} as UserProperty,
            sidebar_list_opened: [],
            encrypt_text_content: false,
            encrypt_file: false,
            max_interval: 1e10,
            combine_content: "",
            mail_address: "",
        }
    },
    methods: {
        // UI / UX
        humanFileSize: humanFileSize,
        timeDeltaToString: timeDeltaToString,
        goToHome() {
            this.$router.push({ name: "Home" })
        },
        beforeUnloadHandler(event: BeforeUnloadEvent) {
            event.preventDefault()
            event.returnValue = true
        },
        setUnloadWarning(enable: boolean) {
            const event_name = "beforeunload"
            if (enable)
                window.addEventListener(event_name, this.beforeUnloadHandler)
            else
                window.removeEventListener(event_name, this.beforeUnloadHandler)
        },
        setSaveStatus(save_status: SaveStatus) {
            if (this.save_status === save_status) return
            this.save_status = save_status
            if (UnsavedSaveStatus.has(save_status)) this.setUnloadWarning(true)
            else this.setUnloadWarning(false)
        },
        async setEditingStatusOnEdit() {
            this.last_edit_time = Date.now()
            if (this.is_readonly) return
            this.setSaveStatus(SaveStatus.editing)
        },
        // create / fetch / push / delete
        async requestPassword(): Promise<SweetAlertResult<any>> {
            return cancelableInput({
                title: this.$t("clip.password_question"),
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
                    response = await axios.get<Response<ClipData>>(
                        `/note/${this.name}`
                    )
                } catch (e: any) {
                    if (isAxiosError(e)) {
                        if (e.response?.status === 400) {
                            showDetailWarning({
                                title: this.$t("clip.error"),
                                text: this.$t("clip.invalid_clip_name"),
                            }).then(this.goToHome)
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
                        } else if (e.response?.status === 451) {
                            showDetailWarning({
                                title: this.$t("clip.error"),
                                text: this.$t(
                                    "clip.report.clip_has_been_banned"
                                ),
                            }).then(this.goToHome)
                            return
                        }
                    }
                    throw e
                }
                if (response.status === 204) {
                    this.is_new = true
                    this.setSaveStatus(SaveStatus.new)
                    this.local_content = ""
                    this.remote_content = ""
                    this.remote_version = this.clip_version = 1
                    return
                } else {
                    try {
                        this.user_property = JSON.parse(
                            response.data.data.user_property
                        ) as UserProperty
                    } catch {
                        this.user_property = {} as UserProperty
                        console.log(response.data.data.user_property)
                        showDetailWarning({
                            title: this.$t("clip.error"),
                            text: this.$t("clip.failed_to_parse_user_property"),
                        })
                    }
                    this.encrypt_text_content =
                        this.user_property.encrypt_text_content ?? false
                    this.encrypt_file = this.user_property.encrypt_file ?? false
                    let content = response.data.data.content
                    if (this.user_property.encrypt_text_content) {
                        if (
                            this.user_property.encrypt_text_content_algo ===
                            "aes"
                        ) {
                            content = AES.decrypt(
                                content,
                                this.encryptPassword
                            ).toString(utf8)
                        } else {
                            showDetailWarning({
                                title: this.$t("clip.error"),
                                text: this.$t(
                                    "clip.encrypt_text_content_algo_not_supported"
                                ),
                            })
                        }
                    }
                    this.remote_version = response.data.data.clip_version ?? 1
                    if (
                        !no_update_content &&
                        (this.remote_version > this.clip_version ||
                            this.first_fetched === false)
                    ) {
                        this.local_content = content
                    }
                    this.first_fetched = true
                    this.current_timeout = response.data.data.timeout_seconds
                    this.selected_timeout = timeDeltaToString(
                        this.current_timeout
                    )
                    this.remote_content = content
                    this.clip_version = this.remote_version
                    this.readonly_name = response.data.data.readonly_name
                    this.is_readonly = response.data.data.is_readonly
                    this.remote_files = response.data.data.files
                    if (this.save_status === SaveStatus.local_outdated) {
                        this.setSaveStatus(SaveStatus.conflict_resolved)
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
        async combinePushContent() {
            if (
                this.is_readonly ||
                this.combine_content === "" ||
                this.encrypt_text_content
            )
                return
            let combine_mode = "prepend"
            let response = await axios.put(`/note/${this.name}`, {
                content: this.combine_content + "\n",
                combine_mode: combine_mode,
            })
            this.clip_version = response.data.data.clip_version
            this.combine_content = ""
            this.local_content = this.remote_content =
                response.data.data.content
            this.clip_version = this.remote_version =
                response.data.data.clip_version
        },
        async pushContent(force = false) {
            if (this.is_readonly) return
            if (this.save_status === SaveStatus.saving) return
            if (!force && this.is_local_outdated) return
            if (force) this.clip_version = this.remote_version
            this.last_saved = Date.now()
            this.setSaveStatus(SaveStatus.saving)
            await this.createIfNotExist()
            let content = this.local_content
            if (this.encrypt_text_content) {
                if (this.user_property.encrypt_text_content_algo === "aes") {
                    content = AES.encrypt(
                        content,
                        this.encryptPassword
                    ).toString()
                } else {
                    showDetailWarning({
                        title: this.$t("clip.error"),
                        text: this.$t(
                            "clip.encrypt_text_content_algo_not_supported"
                        ),
                    })
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
                this.setSaveStatus(SaveStatus.saved)
            } catch (e: any) {
                if (isAxiosError(e)) {
                    if (e.response?.status === 409) {
                        this.remote_version = e.response.data.data.clip_version
                        this.setSaveStatus(SaveStatus.local_outdated)
                        return
                    }
                }
                console.log(e)
                this.setSaveStatus(SaveStatus.error)
            }
        },
        async deleteContent() {
            dangerousConfirm({
                title: this.$t("clip.delete.are_you_sure"),
                text: this.$t("clip.delete.you_wont_be_able_to_revert_this"),
                confirmButtonText: this.$t("clip.delete.yes_delete_it"),
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        let response = await axios.delete(`/note/${this.name}`)
                        showAutoCloseSuccess({
                            title: this.$t("clip.delete.deleted"),
                            text: this.$t(
                                "clip.delete.your_clip_has_been_deleted"
                            ),
                            timer: undefined,
                        }).then(this.goToHome)
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
        arrayBufferToWordArray(ab: ArrayBuffer): WordArray {
            // https://stackoverflow.com/questions/33914764/how-to-read-a-binary-file-with-filereader-in-order-to-hash-it-with-sha-256-in-cr
            var i8a = new Uint8Array(ab)
            var a = []
            for (var i = 0; i < i8a.length; i += 4) {
                a.push(
                    (i8a[i] << 24) |
                        (i8a[i + 1] << 16) |
                        (i8a[i + 2] << 8) |
                        i8a[i + 3]
                )
            }
            return WordArray.create(a, i8a.length)
        },
        wordArrayToArrayBuffer(wordArray: WordArray): ArrayBuffer {
            const { words } = wordArray
            const { sigBytes } = wordArray
            const u8 = new Uint8Array(sigBytes)
            for (let i = 0; i < sigBytes; i += 1) {
                u8[i] = (words[i >>> 2] >>> (24 - (i % 4) * 8)) & 0xff
            }
            return u8
        },
        onAttachFile(event: ClipboardEvent | DragEvent) {
            if (this.is_readonly || this.uploading) return
            let items: FileList | undefined = undefined
            if (event instanceof DragEvent) {
                // file drag & drop
                items = event.dataTransfer?.files
            } else {
                // clipboard
                items = event.clipboardData?.files
            }
            if (items === undefined || items.length === 0) return
            event.preventDefault()
            this.file_to_upload = Array.from(items)
            this.uploadFile()
        },
        async uploadSingleFile(file: File) {
            var formData = new window.FormData()
            if (this.encrypt_file) {
                // encrypt file
                let reader = new FileReader()
                let file_data = await new Promise<ArrayBuffer>(
                    (resolve, reject) => {
                        reader.onload = () => {
                            resolve(reader.result as ArrayBuffer)
                        }
                        reader.onerror = () => {
                            reject(reader.error)
                        }
                        reader.readAsArrayBuffer(file)
                    }
                )
                let encrypted_file_data = AES.encrypt(
                    this.arrayBufferToWordArray(file_data),
                    this.encryptPassword
                ).toString()
                let encrypted_file = new File(
                    [encrypted_file_data],
                    this.encryptFilename(file.name),
                    { type: file.type }
                )
                file = encrypted_file
            }
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
            let file_count =
                this.file_to_upload.length + this.remote_files.length
            if (
                this.metadata.max_file_count &&
                file_count > this.metadata.max_file_count
            ) {
                error_string = this.$t(
                    "clip.file.error.TOTAL_FILES_COUNT_LIMIT_HIT"
                )
            }
            this.file_to_upload.forEach((file) => {
                if (
                    this.metadata.max_file_size &&
                    file.size > this.metadata.max_file_size
                ) {
                    error_string = this.$t(
                        "clip.file.error.SINGLE_FILE_SIZE_LIMIT_HIT"
                    )
                }
            })
            let total_size = this.getTotalSize(
                this.file_to_upload,
                this.remote_files
            )

            if (
                this.metadata.max_all_file_size &&
                total_size > this.metadata.max_all_file_size
            ) {
                error_string = this.$t(
                    "clip.file.error.TOTAL_FILES_SIZE_LIMIT_HIT"
                )
            }
            if (error_string !== null) {
                showDetailWarning({
                    title: this.$t("clip.error"),
                    text: error_string,
                })
                this.file_to_upload = []
                this.uploading = false
                return
            }
            try {
                await Promise.all(
                    this.file_to_upload.map(this.uploadSingleFile)
                )
                this.fetchContent(true)
                /* showAutoCloseSuccess({
                    title: this.$t('clip.file.uploaded'),
                    text: this.$t('clip.file.your_file_has_been_uploaded'),
                }) */
            } catch (e: any) {
                console.log(e)
                error_string = this.$t("clip.file.failed_to_upload_file")
                if (isAxiosError(e)) {
                    if (
                        e.response?.status === 400 &&
                        e.response?.data?.error_id !== null
                    ) {
                        error_string = this.$t(
                            "clip.file.error." + e.response.data.error_id
                        )
                    }
                }
                showDetailWarning({
                    title: this.$t("clip.error"),
                    text: error_string,
                })
            } finally {
                this.file_to_upload = []
                this.uploading = false
                this.fetchContent(true)
            }
        },
        async deleteFile(file: FileData) {
            this.uploading = true
            try {
                let response = await axios.delete(
                    `/note/${this.name}/file/${file.id}`
                )
                this.fetchContent(true)
                /* showAutoCloseSuccess({
                    title: this.$t('clip.file.deleted'),
                    text: this.$t('clip.file.your_file_has_been_deleted'),
                }) */
            } catch (e: any) {
                console.log(e)
                showDetailWarning({
                    title: this.$t("clip.error"),
                    text: this.$t("clip.file.failed_to_delete_file"),
                })
            } finally {
                this.uploading = false
            }
        },
        // password
        async changePassword() {
            let password = (
                await cancelableInput({
                    title: this.$t("clip.new_password_question"),
                    input: "password",
                })
            ).value
            if (password === undefined) return
            try {
                await axios.put(`/note/${this.name}`, {
                    new_password:
                        password === "" ? "" : SHA512(password).toString(),
                })
                this.password = password
                await this.updateEncryptText()
                showAutoCloseSuccess({
                    title: this.$t("clip.password_changed"),
                })
            } catch (e: any) {
                console.log(e)
            }
        },
        async updateEncryptText() {
            if (this.encrypt_text_content) {
                this.user_property.encrypt_text_content = true
                this.user_property.encrypt_text_content_algo = "aes"
            } else {
                this.user_property.encrypt_text_content = false
                this.user_property.encrypt_text_content_algo = ""
            }
            this.pushContent()
        },
        async updateEncryptFile() {
            this.user_property.encrypt_file = this.encrypt_file
            this.pushContent()
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
                    showDetailWarning({
                        title: this.$t("clip.error"),
                        text: this.$t("clip.invalid_timeout"),
                    })
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
                // https://stackoverflow.com/questions/400212/how-do-i-copy-to-the-clipboard-in-javascript
                let textArea = document.createElement("textarea")
                // Avoid scrolling to bottom
                textArea.style.top = "0"
                textArea.style.left = "0"
                textArea.style.position = "fixed"
                textArea.value = content
                document.body.appendChild(textArea)
                textArea.focus()
                textArea.select()
                return new Promise((res, rej) => {
                    document.execCommand("copy") ? res(null) : rej()
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
            this.saveBlob(blob, `${this.name}.txt`)
        },
        saveBlob(blob: Blob, filename: string) {
            const link = document.createElement("a")
            link.href = URL.createObjectURL(blob)
            link.download = filename
            link.click()
            URL.revokeObjectURL(link.href)
        },
        // readonly url
        async toggleReadonlyUrl() {
            try {
                let response = await axios.put(`/note/${this.name}`, {
                    enable_readonly: !this.hasReadonlyName,
                })
                this.fetchContent()
            } catch (e: any) {
                console.log(e)
            }
        },
        // auto save & fetch
        onAutoSave() {
            assert(typeof this.save_interval === "number")
            if (Date.now() - this.last_saved > this.save_interval * 1000) {
                this.pushContentIfChanged()
            }
        },
        onAutoFetch() {
            if (Date.now() - this.last_edit_time > this.fetch_min_idle_time) {
                this.fetchContent()
            }
        },
        onUpdateSaveInterval() {
            this.save_interval = parseInt(this.save_interval.toString())
            if (Number.isNaN(this.save_interval) || this.save_interval < 0)
                this.save_interval = 0
            if (this.save_interval > this.max_interval)
                this.save_interval = this.max_interval
            if (this.save_timer !== null) clearInterval(this.save_timer)
            this.save_timer = null
            if (this.save_interval > 0)
                this.save_timer = setInterval(
                    this.onAutoSave,
                    this.save_interval * 1000
                )
            if (this.save_interval === 0) this.save_interval = ""
        },
        onUpdateFetchInterval() {
            this.fetch_interval = parseInt(this.fetch_interval.toString())
            if (Number.isNaN(this.fetch_interval) || this.fetch_interval < 0)
                this.fetch_interval = 0
            if (this.fetch_interval > this.max_interval)
                this.fetch_interval = this.max_interval
            if (this.fetch_timer !== null) clearInterval(this.fetch_timer)
            this.fetch_timer = null
            if (this.fetch_interval > 0)
                this.fetch_timer = setInterval(
                    this.onAutoFetch,
                    this.fetch_interval * 1000
                )
            if (this.fetch_interval === 0) this.fetch_interval = ""
        },
        async reportClip() {
            try {
                dangerousConfirm({
                    title: this.$t("clip.report.report_clip_confirm"),
                    text: this.$t("clip.report.clip_will_be_banned"),
                }).then(async (result) => {
                    if (result.isConfirmed) {
                        let response = await axios.put(`/note/${this.name}`, {
                            report: true,
                        })
                        showAutoCloseSuccess({
                            title: this.$t("clip.report.reported"),
                            text: this.$t("clip.report.clip_has_been_reported"),
                        }).then(this.goToHome)
                    }
                })
            } catch (e: any) {
                console.log(e)
            }
        },
        async sendToMail() {
            try {
                let response = await axios.post(`/mailto`, {
                    address: this.mail_address,
                    content: this.local_content,
                })
                if (response.status === 202) {
                    await showDetailWarning({
                        title: this.$t("clip.error"),
                        text: this.$t("clip.mail.MAIL_NOT_VERIFIED"),
                    })
                    return
                } else {
                    await showAutoCloseSuccess({
                        title: this.$t("clip.mail.sent"),
                    })
                }
            } catch (e: any) {
                if (isAxiosError(e)) {
                    showDetailWarning({
                        title: this.$t("clip.error"),
                        text: this.$t(
                            "clip.mail." + e.response?.data?.error_id
                        ),
                    })
                    return
                }
                console.log(e)
            }
        },
        mayDecryptFilename(filename: string): string {
            if (!this.encrypt_file) return filename
            return AES.decrypt(filename, this.encryptPassword).toString(utf8)
        },
        encryptFilename(filename: string): string {
            return AES.encrypt(filename, this.encryptPassword).toString()
        },
        async downloadEncryptedFile(file: FileData) {
            // https://blog.csdn.net/qq_38916811/article/details/127515455
            // fetch file from remote url and decrypt
            const response = await axios.get(file.download_url, {
                responseType: "arraybuffer",
            })
            const enc = new TextDecoder("utf-8")
            const str = enc.decode(response.data)
            const decrypted_file_data = this.wordArrayToArrayBuffer(
                AES.decrypt(str, this.encryptPassword)
            )
            // save as blob
            const blob = new Blob([decrypted_file_data])
            this.saveBlob(blob, this.mayDecryptFilename(file.filename))
        },
    },
    computed: {
        name(): string {
            return this.$route.params.name as string
        },
        encryptPassword(): string {
            return SHA256(this.password).toString()
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
        allow_mail(): boolean {
            return this.metadata.allow_mail ?? false
        },
        should_wrap_appbar_to_slot(): string {
            return this.$vuetify.display.smAndUp ? "append" : "extension"
        },
        is_local_outdated(): boolean {
            return this.save_status === SaveStatus.local_outdated
        },
    },
    mounted() {
        // get password from url in hash part
        // example: https://example.com/name#password
        if (window.location.hash) {
            this.password = window.location.hash.slice(1) // remove #
        }

        // disable unload warning on leave
        onBeforeRouteLeave(() => {
            this.setUnloadWarning(false)
        })

        // add auth header
        const auth_interceptor = axios.interceptors.request.use((config) => {
            config.headers["Authorization"] = `Bearer ${Buffer.from(
                SHA512(this.password).toString(),
                "utf8"
            ).toString("base64")}`
            return config
        })
        onBeforeRouteLeave(() => {
            axios.interceptors.request.eject(auth_interceptor)
        })

        // register auto save & fetch
        this.onUpdateSaveInterval()
        this.onUpdateFetchInterval()

        // first fetch
        this.fetchContent()
    },
}
</script>

<style>
/* show pointer cursor for `click to copy`*/
.cursor-pointer * {
    cursor: pointer;
}

/* remove useless padding in sidebar */
#sidebar .v-input__details {
    display: none;
}

#sidebar .v-list {
    padding: 0;
}

#sidebar .v-list-group__items .v-list-item {
    padding-inline-start: 16px !important;
}

/* add better padding in file card */
#file-card div.v-input__prepend {
    margin-inline-start: 16px !important;
    margin-inline-end: 16px !important;
}
</style>
