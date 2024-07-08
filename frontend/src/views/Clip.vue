<template>
    <v-app @drop="onAttachFile" @dragover.prevent>
        <v-app-bar app>
            <app-bar-home-button />
            <!-- sync button if outdated-->
            <v-btn
                icon
                @click="fetchContent()"
                v-if="is_local_outdated"
                :aria-label="$t('clip.a11y.appbar.conflict_drop_local')"
            >
                <v-icon :icon="mdiDownload" />
            </v-btn>
            <!-- sync button if outdated-->
            <v-btn
                icon
                @click="pushContent(true)"
                v-if="is_local_outdated"
                :aria-label="$t('clip.a11y.appbar.conflict_drop_local')"
            >
                <v-icon :icon="mdiUpload" />
            </v-btn>
            <!-- saved status in plaintext -->
            <v-toolbar-title>{{
                save_status ? $t(`save_status.${save_status}`) : ""
            }}</v-toolbar-title>
            <!--Vue issue: https://github.com/vuejs/core/issues/5312-->
            <!-- @vue-ignore -->
            <template v-slot:[should_wrap_appbar_to_slot]>
                <v-spacer></v-spacer>
                <!--delete button-->
                <v-btn
                    icon
                    @click="deleteContent()"
                    v-if="!is_new && !is_readonly"
                    :aria-label="$t('clip.a11y.appbar.delete')"
                >
                    <v-icon :icon="mdiDelete" />
                </v-btn>
                <!-- password button-->
                <v-btn
                    icon
                    @click="changePassword()"
                    v-if="!is_new && !is_readonly"
                    :aria-label="$t('clip.a11y.appbar.password')"
                >
                    <v-icon :icon="mdiLock" />
                </v-btn>
                <!--save button-->
                <v-btn
                    icon
                    @click="pushContent()"
                    v-if="!is_readonly"
                    :aria-label="$t('clip.a11y.appbar.save')"
                >
                    <v-icon :icon="mdiContentSave" />
                </v-btn>
                <!-- copy button-->
                <v-btn
                    icon
                    @click="copyString(local_content)"
                    :aria-label="$t('clip.a11y.appbar.copy')"
                >
                    <v-icon :icon="mdiContentCopy" />
                </v-btn>
                <!-- download button-->
                <v-btn
                    icon
                    @click="downloadContent()"
                    :aria-label="$t('clip.a11y.appbar.download')"
                >
                    <v-icon :icon="mdiDownload" />
                </v-btn>
            </template>
        </v-app-bar>

        <v-main>
            <v-container>
                <v-snackbar-queue
                    v-model="snackbar"
                    location="top end"
                    closable
                />
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
                            @compositionstart="setComposing(true)"
                            @compositionend="setComposing(false)"
                            ref="editor"
                            :aria-label="$t('clip.a11y.input_box')"
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
                                :prepend-inner-icon="mdiClock"
                                v-if="!is_new && !is_readonly"
                            >
                            </v-select>
                            <!-- current url, click to copy-->
                            <v-text-field
                                :label="$t('clip.current_url_click_to_copy')"
                                v-model="current_url"
                                readonly
                                :prepend-inner-icon="mdiLink"
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
                                :prepend-inner-icon="mdiLink"
                                @click="
                                    hasReadonlyName && copyString(readonly_url)
                                "
                                class="cursor-pointer"
                                :append-inner-icon="
                                    is_readonly
                                        ? undefined
                                        : hasReadonlyName
                                        ? mdiDelete
                                        : mdiPlusCircleOutline
                                "
                                @click:append-inner.stop="toggleReadonlyUrl()"
                            >
                            </v-text-field>
                            <v-list
                                v-model:opened="sidebar_list_opened"
                                v-if="!is_new"
                                :role="
                                    sidebar_list_opened.includes(
                                        'more_options_list'
                                    )
                                        ? 'listbox'
                                        : null
                                "
                            >
                                <v-list-group value="more_options_list">
                                    <template v-slot:activator="{ props }">
                                        <v-list-item
                                            v-bind="props"
                                            :prepend-icon="mdiCog"
                                            :title="
                                                $t('clip.advanced_settings')
                                            "
                                            :aria-label="
                                                $t(
                                                    'clip.a11y.toggle_more_options'
                                                )
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
                                        :append-inner-icon="
                                            mdiCommentArrowRight
                                        "
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
                                        v-if="!is_readonly && allow_file"
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
                                        :append-inner-icon="mdiEmailFast"
                                        @click:append-inner="sendToMail()"
                                        v-if="allow_mail"
                                    >
                                    </v-text-field>
                                    <!--report clip-->
                                    <v-list-item
                                        :prepend-icon="mdiAlertOctagon"
                                        @click="reportClip()"
                                    >
                                        <v-list-item-title>{{
                                            $t("clip.report.report_clip")
                                        }}</v-list-item-title>
                                    </v-list-item>
                                    <!--Instant sync (WebSocket)-->
                                    <v-checkbox
                                        v-model="instant_sync"
                                        :label="
                                            $t('clip.websocket.instant_sync')
                                        "
                                        @change="onInstantSyncChange()"
                                        v-if="
                                            !is_readonly && allow_instant_sync
                                        "
                                        :disabled="!instant_sync_code_ready"
                                    ></v-checkbox>
                                </v-list-group>
                            </v-list>
                        </v-card>
                    </v-col>
                    <v-col cols="12">
                        <v-card
                            id="file-card"
                            v-if="
                                (!is_readonly && allow_file) ||
                                remote_files.length
                            "
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
                                :prepend-icon="mdiFileUpload"
                                @change="uploadFile()"
                                v-if="!is_readonly && allow_file"
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
                            <v-list
                                :aria-label="$t('clip.a11y.file.file_list')"
                                role="list"
                            >
                                <v-list-item
                                    v-for="file in remote_files"
                                    :key="file.id"
                                    role="listitem"
                                >
                                    <v-list-item-title
                                        >{{ mayDecryptFilename(file.filename) }}
                                    </v-list-item-title>
                                    <v-list-item-subtitle
                                        >{{ humanFileSize(file.size) }};
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
                                            <!--tabindex=-1 make anchor not focusable, i.e., focus only button-->
                                            <!--preview file-->
                                            <a
                                                :href="file.preview_url"
                                                target="_blank"
                                                style="
                                                    color: inherit;
                                                    text-decoration: none;
                                                "
                                                tabindex="-1"
                                                v-if="canPreviewFile(file)"
                                                :aria-label="
                                                    $t(
                                                        'clip.a11y.file.preview_file',
                                                        [file.filename]
                                                    )
                                                "
                                            >
                                                <v-btn
                                                    icon
                                                    variant="text"
                                                    :aria-label="
                                                        $t(
                                                            'clip.a11y.file.preview_file',
                                                            [file.filename]
                                                        )
                                                    "
                                                >
                                                    <v-icon :icon="mdiEye" />
                                                </v-btn>
                                            </a>
                                            <!--download file (non-encrypted)-->
                                            <a
                                                download
                                                :filename="file.filename"
                                                :href="file.download_url"
                                                target="_self"
                                                style="
                                                    color: inherit;
                                                    text-decoration: none;
                                                "
                                                tabindex="-1"
                                                v-if="!encrypt_file"
                                                :aria-label="
                                                    $t(
                                                        'clip.a11y.file.download_file',
                                                        [file.filename]
                                                    )
                                                "
                                            >
                                                <v-btn
                                                    icon
                                                    variant="text"
                                                    :aria-label="
                                                        $t(
                                                            'clip.a11y.file.download_file',
                                                            [file.filename]
                                                        )
                                                    "
                                                >
                                                    <v-icon
                                                        :icon="mdiDownload"
                                                    />
                                                </v-btn>
                                            </a>
                                            <!--download file (encrypted)-->
                                            <v-btn
                                                icon
                                                variant="text"
                                                @click="
                                                    downloadEncryptedFile(file)
                                                "
                                                v-else
                                                :aria-label="
                                                    $t(
                                                        'clip.a11y.file.download_file',
                                                        [file.filename]
                                                    )
                                                "
                                            >
                                                <v-icon :icon="mdiDownload" />
                                            </v-btn>
                                            <!--delete file-->
                                            <v-btn
                                                icon
                                                variant="text"
                                                @click="deleteFile(file)"
                                                v-if="!is_readonly"
                                                :aria-label="
                                                    $t(
                                                        'clip.a11y.file.delete_file',
                                                        [file.filename]
                                                    )
                                                "
                                            >
                                                <v-icon :icon="mdiDelete" />
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

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue"

import { useAppStore } from "@/store/app"
const appStore = useAppStore()

import { useRouter, useRoute } from "vue-router"
const router = useRouter()
const route = useRoute()

import { useI18n } from "vue-i18n"
const { t: $t } = useI18n()

import { replaceLastPartOfUrl, humanFileSize, assert } from "@/utils"

import {
    FileData,
    axios,
    UserProperty,
    Response,
    ClipData,
    WebSocketBaseData,
} from "@/api"
import { AxiosResponse, isAxiosError } from "axios"

// UI / UX
import { timeDeltaToString } from "@/plugins/i18n"
import {
    showDetailWarning,
    showAutoCloseSuccess,
    cancelableInput,
    dangerousConfirm,
} from "@/plugins/swal"
import { SweetAlertResult } from "sweetalert2"
import {
    mdiDownload,
    mdiUpload,
    mdiDelete,
    mdiLock,
    mdiContentSave,
    mdiContentCopy,
    mdiClock,
    mdiLink,
    mdiPlusCircleOutline,
    mdiCog,
    mdiCommentArrowRight,
    mdiEmailFast,
    mdiAlertOctagon,
    mdiFileUpload,
    mdiEye,
} from "@mdi/js"
import AppBarHomeButton from "@/components/AppBarHomeButton.vue"
import { useDisplay } from "vuetify"
const { smAndUp } = useDisplay()
const should_wrap_appbar_to_slot = computed(() => {
    return smAndUp.value ? "append" : "extension"
})
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
const save_status = ref(SaveStatus.empty)
const is_new = ref(true)
const sidebar_list_opened = ref<string[]>([])
function goToHome() {
    router.push({ name: "Home" })
}
function beforeUnloadHandler(event: BeforeUnloadEvent) {
    event.preventDefault()
    event.returnValue = true
}
function setUnloadWarning(enable: boolean) {
    const event_name = "beforeunload"
    if (enable) window.addEventListener(event_name, beforeUnloadHandler)
    else window.removeEventListener(event_name, beforeUnloadHandler)
}
function setSaveStatus(new_save_status: SaveStatus) {
    if (save_status.value === new_save_status) return
    save_status.value = new_save_status
    if (UnsavedSaveStatus.has(new_save_status)) setUnloadWarning(true)
    else setUnloadWarning(false)
}
async function setEditingStatusOnEdit() {
    last_edit_time.value = Date.now()
    if (is_readonly.value) return
    setSaveStatus(SaveStatus.editing)
}
async function requestPassword(): Promise<SweetAlertResult<any>> {
    return cancelableInput({
        title: $t("clip.password_question"),
        input: "password",
    })
}
const snackbar = ref<object[]>([])

// Base
const editor = ref<any | null>(null)
const metadata = appStore.metadata
const current_url = window.location.href
const name = route.params.name as string
const default_save_interval = 3
const websocket_save_interval = 1
const max_interval = 1e10
const first_fetched = ref(false)
const clip_version = ref(1)
const remote_version = ref(1)
const local_content = ref("")
const remote_content = ref("")
const last_saved = ref(Date.now())
const current_timeout = ref(-1)
const selected_timeout = ref("")
const is_readonly = ref(false)
const save_interval = ref<number | string>(default_save_interval)
const fetch_min_idle_time = ref(1)
const fetch_interval = ref<number | string>(0)
const save_timer = ref<ReturnType<typeof setTimeout> | null>(null)
const fetch_timer = ref<ReturnType<typeof setTimeout> | null>(null)
const last_edit_time = ref(Date.now())
const user_property = ref<UserProperty>({})
const combine_content = ref("")

// Init
onMounted(() => {
    // get password from url in hash part
    // example: https://example.com/name#password
    if (window.location.hash) {
        password.value = window.location.hash.slice(1) // remove #
    }

    // disable unload warning on leave
    onBeforeRouteLeave(() => {
        setUnloadWarning(false)
        disconnectWebSocket()
    })

    // add auth header
    const auth_interceptor = axios.interceptors.request.use((config) => {
        config.headers[
            "Authorization"
        ] = `Bearer ${server_authoirzation_password.value}`
        return config
    })
    onBeforeRouteLeave(() => {
        axios.interceptors.request.eject(auth_interceptor)
    })

    // register auto save & fetch
    onUpdateSaveInterval()
    onUpdateFetchInterval()

    // first fetch
    fetchContent()
})

// create / fetch / push / delete
async function createIfNotExist() {
    if (!is_new.value) return
    try {
        await axios
            .post<Response<ClipData>>(`/note/${name}`, {})
            .then(processFetchedContent)
        is_new.value = false
    } catch (e: any) {
        console.log(e)
    }
}
async function processFetchedContent(
    axios_response: AxiosResponse<Response<ClipData>>,
    options: { include_slots?: ("content" | "file" | "version")[] } = {}
) {
    const response_data = axios_response.data
    if (axios_response.status === 204) {
        is_new.value = true
        setSaveStatus(SaveStatus.new)
        return
    }
    is_new.value = false
    try {
        user_property.value = JSON.parse(
            response_data.data.user_property
        ) as UserProperty
    } catch {
        user_property.value = {} as UserProperty
        console.log(response_data.data.user_property)
        showDetailWarning({
            title: $t("clip.error"),
            text: $t("clip.failed_to_parse_user_property"),
        })
    }
    encrypt_text_content.value =
        user_property.value.encrypt_text_content ?? false
    encrypt_file.value = user_property.value.encrypt_file ?? false
    let content = response_data.data.content
    if (user_property.value.encrypt_text_content) {
        if (user_property.value.encrypt_text_content_algo === "aes") {
            const decrypt = AES.decrypt(
                content,
                encryptPassword.value
            ).toString(utf8)
            if (content !== "" && decrypt === "") {
                content = content + $t("error.decrypt_error")
            } else {
                content = decrypt
            }
        } else {
            showDetailWarning({
                title: $t("clip.error"),
                text: $t("clip.encrypt_text_content_algo_not_supported"),
            })
        }
    }
    remote_version.value = response_data.data.clip_version ?? 1
    if (
        remote_version.value > clip_version.value ||
        first_fetched.value === false
    ) {
        if (
            options.include_slots === undefined ||
            options.include_slots.includes("content") ||
            options.include_slots.includes("version")
        ) {
            clip_version.value = remote_version.value
        }
        if (
            options.include_slots === undefined ||
            options.include_slots.includes("content")
        ) {
            local_content.value = content
        }
    }
    if (
        options.include_slots === undefined ||
        options.include_slots.includes("file")
    ) {
        remote_files.value = response_data.data.files
    }
    if (first_fetched.value === false) {
        first_fetched.value = true
    }
    current_timeout.value = response_data.data.timeout_seconds
    selected_timeout.value = timeDeltaToString(current_timeout.value)
    remote_content.value = content
    readonly_name.value = response_data.data.readonly_name
    is_readonly.value = response_data.data.is_readonly
    if (save_status.value === SaveStatus.local_outdated) {
        setSaveStatus(SaveStatus.conflict_resolved)
    }
}
async function fetchContent(
    options: Parameters<typeof processFetchedContent>[1] = {}
) {
    try {
        let response
        try {
            response = await axios.get<Response<ClipData>>(`/note/${name}`)
        } catch (e: any) {
            if (isAxiosError(e)) {
                if (e.response?.status === 400) {
                    showDetailWarning({
                        title: $t("clip.error"),
                        text: $t("clip.invalid_clip_name"),
                    }).then(goToHome)
                    return
                } else if (e.response?.status === 401) {
                    requestPassword().then((result) => {
                        if (result.isConfirmed) {
                            password.value = result.value as string
                            return fetchContent(options)
                        } else {
                            return goToHome()
                        }
                    })
                    return
                } else if (e.response?.status === 451) {
                    showDetailWarning({
                        title: $t("clip.error"),
                        text: $t("clip.report.clip_has_been_banned"),
                    }).then(goToHome)
                    return
                }
            }
            throw e
        }
        processFetchedContent(response)
    } catch (e: any) {
        console.log(e)
    }
}
function onAutoFetch() {
    if (
        Date.now() - last_edit_time.value > fetch_min_idle_time.value &&
        !is_ime_composing.value
    ) {
        fetchContent()
    }
}
function onUpdateFetchInterval() {
    fetch_interval.value = parseInt(fetch_interval.value.toString())
    if (Number.isNaN(fetch_interval.value) || fetch_interval.value < 0)
        fetch_interval.value = 0
    if (fetch_interval.value > max_interval) fetch_interval.value = max_interval
    if (fetch_timer.value !== null) clearInterval(fetch_timer.value)
    fetch_timer.value = null
    if (fetch_interval.value > 0)
        fetch_timer.value = setInterval(
            onAutoFetch,
            fetch_interval.value * 1000
        )
    if (fetch_interval.value === 0) fetch_interval.value = ""
}
async function pushContentIfChanged() {
    if (local_content.value != remote_content.value) {
        if (instant_sync.value) {
            doInstantSync()
            if (autosave_while_instant_sync.value) {
                pushContent()
            }
        } else {
            pushContent()
        }
    }
}
function onAutoSave() {
    assert(typeof save_interval.value === "number")
    if (Date.now() - last_saved.value > save_interval.value * 1000) {
        pushContentIfChanged()
    }
}
function onUpdateSaveInterval() {
    save_interval.value = parseInt(save_interval.value.toString())
    if (Number.isNaN(save_interval.value) || save_interval.value < 0)
        save_interval.value = 0
    if (save_interval.value > max_interval) save_interval.value = max_interval
    if (save_timer.value !== null) clearInterval(save_timer.value)
    save_timer.value = null
    if (save_interval.value > 0)
        save_timer.value = setInterval(onAutoSave, save_interval.value * 1000)
    if (save_interval.value === 0) save_interval.value = ""
}
async function combinePushContent() {
    if (
        is_readonly.value ||
        combine_content.value === "" ||
        encrypt_text_content.value
    )
        return
    let combine_mode = "prepend"
    let response = await axios.put(`/note/${name}`, {
        content: combine_content.value + "\n",
        combine_mode: combine_mode,
    })
    clip_version.value = response.data.data.clip_version
    combine_content.value = ""
    local_content.value = remote_content.value = response.data.data.content
    clip_version.value = remote_version.value = response.data.data.clip_version
}
async function pushContent(force = false) {
    if (is_readonly.value) return
    if (save_status.value === SaveStatus.saving) return
    if (!force && is_local_outdated.value) return
    if (force) clip_version.value = remote_version.value
    last_saved.value = Date.now()
    setSaveStatus(SaveStatus.saving)
    await createIfNotExist()
    let content = local_content.value
    if (encrypt_text_content.value) {
        if (user_property.value.encrypt_text_content_algo === "aes") {
            if (content !== "")
                content = AES.encrypt(content, encryptPassword.value).toString()
        } else {
            showDetailWarning({
                title: $t("clip.error"),
                text: $t("clip.encrypt_text_content_algo_not_supported"),
            })
            return
        }
    }
    try {
        await axios
            .put<Response<ClipData>>(`/note/${name}`, {
                user_property: JSON.stringify(user_property.value),
                content: content,
                clip_version: clip_version.value,
            })
            .then((resp) => {
                processFetchedContent(resp, { include_slots: ["version"] })
            })
        setSaveStatus(SaveStatus.saved)
    } catch (e: any) {
        if (isAxiosError(e)) {
            if (e.response?.status === 409) {
                remote_version.value = e.response.data.data.clip_version
                setSaveStatus(SaveStatus.local_outdated)
                return
            }
        }
        console.log(e)
        setSaveStatus(SaveStatus.error)
    }
}
async function deleteContent() {
    const result = await dangerousConfirm({
        title: $t("clip.delete.are_you_sure"),
        text: $t("clip.delete.you_wont_be_able_to_revert_this"),
        confirmButtonText: $t("clip.delete.yes_delete_it"),
    })

    if (result.isConfirmed) {
        try {
            await axios.delete(`/note/${name}`)
            showAutoCloseSuccess({
                title: $t("clip.delete.deleted"),
                text: $t("clip.delete.your_clip_has_been_deleted"),
                timer: undefined,
            }).then(goToHome)
            return
        } catch (e: any) {
            console.log(e)
        }
    }
}

// File
import { Buffer } from "buffer"
import AES from "crypto-js/aes"
import SHA256 from "crypto-js/sha256"
import SHA512 from "crypto-js/sha512"
import utf8 from "crypto-js/enc-utf8"
import WordArray from "crypto-js/lib-typedarrays"
const uploading = ref(false)
const file_to_upload = ref<File[]>([])
const remote_files = ref<FileData[]>([])
const encrypt_file = ref(false)
const allow_file = computed(() => {
    return (
        metadata.max_all_file_size !== 0 &&
        metadata.max_file_count !== 0 &&
        metadata.max_file_size !== 0
    )
})
function getTotalSize(...file_arrays: (File[] | FileData[])[]): number {
    let total_size = 0
    file_arrays.forEach((files) => {
        files.forEach((file) => {
            total_size += file.size
        })
    })
    return total_size
}
function arrayBufferToWordArray(ab: ArrayBuffer): WordArray {
    // https://stackoverflow.com/questions/33914764/how-to-read-a-binary-file-with-filereader-in-order-to-hash-it-with-sha-256-in-cr
    var i8a = new Uint8Array(ab)
    var a = []
    for (var i = 0; i < i8a.length; i += 4) {
        a.push(
            (i8a[i] << 24) | (i8a[i + 1] << 16) | (i8a[i + 2] << 8) | i8a[i + 3]
        )
    }
    return WordArray.create(a, i8a.length)
}
function wordArrayToArrayBuffer(wordArray: WordArray): ArrayBuffer {
    const { words } = wordArray
    const { sigBytes } = wordArray
    const u8 = new Uint8Array(sigBytes)
    for (let i = 0; i < sigBytes; i += 1) {
        u8[i] = (words[i >>> 2] >>> (24 - (i % 4) * 8)) & 0xff
    }
    return u8
}
function onAttachFile(event: ClipboardEvent | DragEvent) {
    if (is_readonly.value || uploading.value || !allow_file.value) return
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
    file_to_upload.value = Array.from(items)
    uploadFile()
}
async function uploadSingleFile(file: File) {
    var formData = new FormData()
    if (encrypt_file.value) {
        // encrypt file
        let reader = new FileReader()
        let file_data = await new Promise<ArrayBuffer>((resolve, reject) => {
            reader.onload = () => {
                resolve(reader.result as ArrayBuffer)
            }
            reader.onerror = () => {
                reject(reader.error)
            }
            reader.readAsArrayBuffer(file)
        })
        let encrypted_file_data = AES.encrypt(
            arrayBufferToWordArray(file_data),
            encryptPassword.value
        ).toString()
        let encrypted_file = new File(
            [encrypted_file_data],
            encryptFilename(file.name),
            { type: file.type }
        )
        file = encrypted_file
    }
    formData.append("file", file)
    await axios.post(`/note/${name}/file/0`, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    })
}
async function uploadFile() {
    await createIfNotExist()
    if (file_to_upload.value.length === 0) return
    uploading.value = true
    let error_string = null
    let file_count = file_to_upload.value.length + remote_files.value.length
    if (metadata.max_file_count && file_count > metadata.max_file_count) {
        error_string = $t("clip.file.error.TOTAL_FILES_COUNT_LIMIT_HIT")
    }
    file_to_upload.value.forEach((file) => {
        if (metadata.max_file_size && file.size > metadata.max_file_size) {
            error_string = $t("clip.file.error.SINGLE_FILE_SIZE_LIMIT_HIT")
        }
    })
    let total_size = getTotalSize(file_to_upload.value, remote_files.value)

    if (metadata.max_all_file_size && total_size > metadata.max_all_file_size) {
        error_string = $t("clip.file.error.TOTAL_FILES_SIZE_LIMIT_HIT")
    }
    if (error_string !== null) {
        showDetailWarning({
            title: $t("clip.error"),
            text: error_string,
        })
        file_to_upload.value = []
        uploading.value = false
        return
    }
    try {
        await Promise.all(file_to_upload.value.map(uploadSingleFile))
    } catch (e: any) {
        console.log(e)
        error_string = $t("clip.file.failed_to_upload_file")
        if (isAxiosError(e)) {
            if (
                e.response?.status === 400 &&
                e.response?.data?.error_id !== null
            ) {
                error_string = $t("clip.file.error." + e.response.data.error_id)
            }
        }
        showDetailWarning({
            title: $t("clip.error"),
            text: error_string,
        })
    } finally {
        file_to_upload.value = []
        uploading.value = false
        fetchContent({
            include_slots: ["file"],
        })
    }
}
async function deleteFile(file: FileData) {
    if (uploading.value) return
    uploading.value = true
    const result = await dangerousConfirm({
        title: $t("clip.delete.are_you_sure"),
        text: $t("clip.delete.you_wont_be_able_to_revert_this"),
        confirmButtonText: $t("clip.delete.yes_delete_it"),
    })

    if (!result.isConfirmed) {
        uploading.value = false
        return
    }

    try {
        await axios
            .delete<Response<ClipData>>(`/note/${name}/file/${file.id}`)
            .then((resp) =>
                processFetchedContent(resp, {
                    include_slots: ["file"],
                })
            )
        /* showAutoCloseSuccess({
                    title: $t('clip.file.deleted'),
                    text: $t('clip.file.your_file_has_been_deleted'),
                }) */
    } catch (e: any) {
        console.log(e)
        showDetailWarning({
            title: $t("clip.error"),
            text: $t("clip.file.failed_to_delete_file"),
        })
    } finally {
        uploading.value = false
    }
}
function canPreviewFile(file: FileData): boolean {
    if (encrypt_file.value) return false
    return true
}

// Instant Sync
import { onBeforeRouteLeave } from "vue-router"
import type { io as ioType } from "socket.io-client"
var io: null | typeof ioType = null
import type { diff_match_patch as DiffMatchPatchType } from "@dmsnell/diff-match-patch"
type patch_obj = DiffMatchPatchType.patch_obj
var diff_match_patch: null | DiffMatchPatchType = null
const instant_sync_code_ready = ref(false)
watch(first_fetched, async (new_first_fetched, old_first_fetched) => {
    if (new_first_fetched && !old_first_fetched) {
        const DiffMatchPatch = (await import("@dmsnell/diff-match-patch"))
            .diff_match_patch
        diff_match_patch = new DiffMatchPatch()
        io = (await import("socket.io-client")).io
        instant_sync_code_ready.value = true
    }
})
const allow_instant_sync = computed(() => {
    return metadata.websocket_endpoint !== ""
})
const instant_sync = ref(false)
const autosave_while_instant_sync = ref(false)
const instant_sync_socket = ref<ReturnType<typeof ioType> | null>(null)
const is_ime_composing = ref(false)
const instant_sync_patches_queue = ref<patch_obj[][]>([])

const is_local_outdated = computed(() => {
    return save_status.value === SaveStatus.local_outdated
})
const websocket_base_data = computed(() => {
    return {
        name: name,
        client_id: appStore.client_id,
        authorization: server_authoirzation_password.value,
        data: {},
    }
})

function connectWebSocket() {
    autosave_while_instant_sync.value = true
    assert(io !== null)
    instant_sync_socket.value = io(
        appStore.metadata.websocket_endpoint + "/instant_sync",
        { path: appStore.metadata.websocket_path }
    )

    instant_sync_socket.value.on("connect", () => {
        autosave_while_instant_sync.value = false
        if (instant_sync_socket.value !== null)
            instant_sync_socket.value.emit("join", websocket_base_data.value)
    })

    instant_sync_socket.value.on("enable_save", (data: WebSocketBaseData) => {
        autosave_while_instant_sync.value = true
    })

    instant_sync_socket.value.on("diff", (data: WebSocketBaseData) => {
        if (data.client_id === websocket_base_data.value.client_id) return
        const patches = data.data as patch_obj[]
        handleInstantSyncPatchesQueue(patches)
    })
}
function disconnectWebSocket() {
    if (instant_sync_socket.value !== null) {
        instant_sync_socket.value.disconnect()
        instant_sync_socket.value = null
        autosave_while_instant_sync.value = false
    }
}
function onInstantSyncChange() {
    if (instant_sync.value) {
        save_interval.value = websocket_save_interval
        connectWebSocket()
    } else {
        save_interval.value = default_save_interval
        disconnectWebSocket()
    }
}
function setComposing(status: boolean) {
    is_ime_composing.value = status
    handleInstantSyncPatchesQueue()
}
function handleInstantSyncPatchesQueue(
    patches: patch_obj[] | undefined = undefined
) {
    if (patches !== undefined) {
        instant_sync_patches_queue.value.push(patches)
    }
    if (!is_ime_composing.value) {
        instant_sync_patches_queue.value.forEach((patches) => {
            handleInstantSyncPatches(patches)
        })
        instant_sync_patches_queue.value = []
    }
}
function calculateCursorPositionAfterMergeDiff(
    cursor_position: number,
    diff: patch_obj[]
): number {
    let new_cursor_position = cursor_position
    diff.forEach((d) => {
        // if start of the diff is before the cursor
        if (d.start1 !== null && d.start1 < cursor_position) {
            // move the cursor by the length of the diff
            new_cursor_position += d.length2 - d.length1
        }
    })
    return new_cursor_position
}
function onInstantSyncPatchFailed() {
    instant_sync.value = false
    onInstantSyncChange()
    snackbar.value.push({
        text: $t("clip.websocket.apply_patch_failed_stopped"),
        timeout: -1,
    })
}
function handleInstantSyncPatches(patches: patch_obj[]) {
    assert(diff_match_patch !== null)
    const [result, successes] = diff_match_patch.patch_apply(
        patches,
        local_content.value
    ) as [string, boolean[]]
    if (successes.every((v) => v === true)) {
        // cursor position
        const bodyTextArea = editor?.value?.$el.querySelector(
            "textarea"
        ) as HTMLTextAreaElement
        const selectionStart = calculateCursorPositionAfterMergeDiff(
            bodyTextArea.selectionStart,
            patches
        )
        const selectionEnd = calculateCursorPositionAfterMergeDiff(
            bodyTextArea.selectionEnd,
            patches
        )
        remote_content.value = local_content.value = result
        setTimeout(() => {
            // Set selection with 1ms delay, ref: https://stackoverflow.com/a/52333799
            bodyTextArea.selectionStart = selectionStart
            bodyTextArea.selectionEnd = selectionEnd
        })
        if (autosave_while_instant_sync.value) {
            pushContent()
        }
    } else onInstantSyncPatchFailed()
}
function doInstantSync() {
    assert(diff_match_patch !== null)
    assert(instant_sync_socket.value !== null)
    instant_sync_socket.value.emit("diff", {
        ...websocket_base_data.value,
        data: diff_match_patch.patch_make(
            remote_content.value,
            local_content.value
        ),
    })
    remote_content.value = local_content.value
}

// Mail
const allow_mail = computed(() => {
    return metadata.allow_mail
})
const mail_address = ref("")
async function sendToMail() {
    try {
        let response = await axios.post(`/mailto`, {
            address: mail_address.value,
            content: local_content.value,
        })
        if (response.status === 202) {
            await showDetailWarning({
                title: $t("clip.error"),
                text: $t("clip.mail.MAIL_NOT_VERIFIED"),
            })
            return
        } else {
            await showAutoCloseSuccess({
                title: $t("clip.mail.sent"),
            })
        }
    } catch (e: any) {
        if (isAxiosError(e)) {
            showDetailWarning({
                title: $t("clip.error"),
                text: $t("clip.mail." + e.response?.data?.error_id),
            })
            return
        }
        console.log(e)
    }
}

// password & encryption
const password = ref("")
const server_authoirzation_password = computed(() => {
    return Buffer.from(SHA512(password.value).toString(), "utf8").toString(
        "base64"
    )
})
async function changePassword() {
    let new_password = (
        await cancelableInput({
            title: $t("clip.new_password_question"),
            input: "password",
        })
    ).value
    if (new_password === undefined) return
    try {
        await axios.put(`/note/${name}`, {
            new_password: new_password === "" ? "" : SHA512(new_password).toString(),
        })
        password.value = new_password
        await updateEncryptText()
        showAutoCloseSuccess({
            title: $t("clip.password_changed"),
        })
    } catch (e: any) {
        console.log(e)
    }
}

const encryptPassword = computed(() => {
    return SHA256(password.value).toString()
})
const encrypt_text_content = ref(false)
async function updateEncryptText() {
    if (encrypt_text_content.value) {
        user_property.value.encrypt_text_content = true
        user_property.value.encrypt_text_content_algo = "aes"
    } else {
        user_property.value.encrypt_text_content = false
        user_property.value.encrypt_text_content_algo = ""
    }
    pushContent()
}
async function updateEncryptFile() {
    user_property.value.encrypt_file = encrypt_file.value
    pushContent()
}
function mayDecryptFilename(filename: string): string {
    if (!encrypt_file.value) return filename
    const decrypt = AES.decrypt(filename, encryptPassword.value).toString(utf8)
    if (filename !== "" && decrypt === "")
        return filename + $t("error.decrypt_error")
    else return decrypt
}
function encryptFilename(filename: string): string {
    if (filename !== "")
        return AES.encrypt(filename, encryptPassword.value).toString()
    else return ""
}
async function downloadEncryptedFile(file: FileData) {
    // https://blog.csdn.net/qq_38916811/article/details/127515455
    // fetch file from remote url and decrypt
    const response = await axios.get(file.download_url, {
        responseType: "arraybuffer",
    })
    const enc = new TextDecoder("utf-8")
    const str = enc.decode(response.data)
    const decrypted_file_data = wordArrayToArrayBuffer(
        AES.decrypt(str, encryptPassword.value)
    )
    // save as blob
    const blob = new Blob([decrypted_file_data])
    saveBlob(blob, mayDecryptFilename(file.filename))
}

// useful features
async function copyString(content: string) {
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
}
async function downloadContent() {
    // save as blob
    const blob = new Blob([local_content.value], { type: "text/plain" })
    saveBlob(blob, `${name}.txt`)
}
function saveBlob(blob: Blob, filename: string) {
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
}

// readonly url
const readonly_name = ref("")
const hasReadonlyName = computed(() => {
    return readonly_name.value !== ""
})
const readonly_url = computed(() => {
    return replaceLastPartOfUrl(current_url, readonly_name.value)
})
const readonly_url_check_empty = computed(() => {
    return hasReadonlyName.value ? readonly_url.value : " "
})
async function toggleReadonlyUrl() {
    try {
        await axios
            .put<Response<ClipData>>(`/note/${name}`, {
                enable_readonly: !hasReadonlyName.value,
            })
            .then(processFetchedContent)
    } catch (e: any) {
        console.log(e)
    }
}

// user actions
const timeout_selections = metadata.timeout_selections || []
async function setNoteTimeout(selected_timeout: string) {
    await createIfNotExist()
    try {
        let new_timeout = undefined
        timeout_selections.forEach((timeout) => {
            if (timeDeltaToString(timeout) === selected_timeout) {
                new_timeout = timeout
            }
        })

        let invalid_timeout_toast = () => {
            showDetailWarning({
                title: $t("clip.error"),
                text: $t("clip.invalid_timeout"),
            })
        }

        if (new_timeout === undefined) {
            invalid_timeout_toast()
            return
        }
        try {
            let response = await axios.put(`/note/${name}`, {
                timeout_seconds: new_timeout,
            })
            current_timeout.value = new_timeout
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
}
async function reportClip() {
    try {
        dangerousConfirm({
            title: $t("clip.report.report_clip_confirm"),
            text: $t("clip.report.clip_will_be_banned"),
        }).then(async (result) => {
            if (result.isConfirmed) {
                let response = await axios.put(`/note/${name}`, {
                    report: true,
                })
                showAutoCloseSuccess({
                    title: $t("clip.report.reported"),
                    text: $t("clip.report.clip_has_been_reported"),
                }).then(goToHome)
                return
            }
        })
    } catch (e: any) {
        console.log(e)
    }
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
