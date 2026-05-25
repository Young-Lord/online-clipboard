<template>
    <v-app>
        <v-app-bar app>
            <app-bar-home-button />
            <v-toolbar-title>{{ $t("admin.title") }}</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn
                v-if="token_remembered"
                icon
                @click="forgetToken()"
                :aria-label="$t('admin.forget_token')"
            >
                <v-icon :icon="mdiLogout" />
            </v-btn>
        </v-app-bar>

        <v-main>
            <v-container>
                <!-- Token input -->
                <v-card v-if="!authed" class="mb-4">
                    <v-card-title>{{ $t("admin.signin_title") }}</v-card-title>
                    <v-card-text>
                        <v-text-field
                            v-model="token_input"
                            :label="$t('admin.admin_token')"
                            type="password"
                            @keydown.enter="checkToken(true)"
                            autocomplete="current-password"
                            :prepend-inner-icon="mdiKey"
                        ></v-text-field>
                        <v-checkbox
                            v-model="remember_token"
                            :label="$t('admin.remember_token')"
                            hide-details
                        ></v-checkbox>
                        <v-btn
                            color="primary"
                            block
                            class="mt-2"
                            :disabled="!token_input"
                            @click="checkToken(true)"
                        >
                            {{ $t("admin.signin") }}
                        </v-btn>
                    </v-card-text>
                </v-card>

                <template v-else>
                    <!-- Create -->
                    <v-card class="mb-4">
                        <v-card-title>{{
                            $t("admin.create_title")
                        }}</v-card-title>
                        <v-card-text>
                            <v-row dense>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model="create_form.code"
                                        :label="
                                            $t(
                                                'admin.code_optional_custom'
                                            )
                                        "
                                        :hint="$t('admin.code_hint')"
                                        persistent-hint
                                    ></v-text-field>
                                </v-col>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model="create_form.note"
                                        :label="$t('admin.code_note')"
                                    ></v-text-field>
                                </v-col>
                                <v-col cols="6" md="3">
                                    <v-text-field
                                        v-model.number="create_form.count"
                                        :label="$t('admin.count')"
                                        type="number"
                                        min="1"
                                        max="100"
                                    ></v-text-field>
                                </v-col>
                                <v-col cols="6" md="3">
                                    <v-text-field
                                        v-model.number="create_form.max_uses"
                                        :label="$t('admin.max_uses_label')"
                                        :hint="$t('admin.unlimited_hint')"
                                        persistent-hint
                                        type="number"
                                    ></v-text-field>
                                </v-col>
                                <v-col cols="6" md="3">
                                    <v-text-field
                                        v-model.number="
                                            create_form.effect_duration_days
                                        "
                                        :label="
                                            $t(
                                                'admin.effect_duration_days_label'
                                            )
                                        "
                                        :hint="
                                            $t(
                                                'admin.unlimited_negative_hint'
                                            )
                                        "
                                        persistent-hint
                                        type="number"
                                    ></v-text-field>
                                </v-col>
                                <v-col cols="6" md="3">
                                    <v-text-field
                                        v-model="create_form.valid_until"
                                        :label="$t('admin.valid_until_label')"
                                        :hint="$t('admin.iso_hint')"
                                        persistent-hint
                                        placeholder="2027-01-01"
                                    ></v-text-field>
                                </v-col>
                            </v-row>
                            <v-divider class="my-3"></v-divider>
                            <div class="text-subtitle-2 mb-2">
                                {{ $t("admin.benefits_section") }}
                            </div>
                            <v-row dense>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model.number="benefit_file_size_mib"
                                        :label="
                                            $t('admin.benefit_max_file_size_mib')
                                        "
                                        type="number"
                                        min="0"
                                    ></v-text-field>
                                </v-col>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model.number="
                                            create_form.benefits.max_file_count
                                        "
                                        :label="$t('admin.benefit_max_file_count')"
                                        type="number"
                                        min="0"
                                    ></v-text-field>
                                </v-col>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model.number="
                                            benefit_total_size_mib
                                        "
                                        :label="
                                            $t(
                                                'admin.benefit_max_all_file_size_mib'
                                            )
                                        "
                                        type="number"
                                        min="0"
                                    ></v-text-field>
                                </v-col>
                                <v-col cols="12" md="6">
                                    <v-text-field
                                        v-model.number="
                                            benefit_max_timeout_days
                                        "
                                        :label="
                                            $t('admin.benefit_max_timeout_days')
                                        "
                                        type="number"
                                        min="0"
                                    ></v-text-field>
                                </v-col>
                            </v-row>
                            <v-btn
                                color="primary"
                                class="mt-2"
                                :disabled="creating"
                                @click="submitCreate()"
                            >
                                {{ $t("admin.create_btn") }}
                            </v-btn>
                        </v-card-text>
                    </v-card>

                    <!-- List -->
                    <v-card>
                        <v-card-title>
                            <div class="d-flex align-center w-100">
                                <span>{{ $t("admin.list_title") }}</span>
                                <v-spacer></v-spacer>
                                <v-text-field
                                    v-model="search_query"
                                    :placeholder="$t('admin.search_placeholder')"
                                    density="compact"
                                    hide-details
                                    style="max-width: 220px"
                                    @keydown.enter="reload()"
                                    :prepend-inner-icon="mdiMagnify"
                                ></v-text-field>
                                <v-btn
                                    icon
                                    @click="reload()"
                                    :aria-label="$t('admin.reload')"
                                    class="ml-2"
                                >
                                    <v-icon :icon="mdiRefresh" />
                                </v-btn>
                            </div>
                        </v-card-title>
                        <v-card-text>
                            <v-table density="compact">
                                <thead>
                                    <tr>
                                        <th>{{ $t("admin.col.code") }}</th>
                                        <th>{{ $t("admin.col.note") }}</th>
                                        <th>{{ $t("admin.col.benefits") }}</th>
                                        <th>{{ $t("admin.col.usage") }}</th>
                                        <th>
                                            {{ $t("admin.col.effect_duration") }}
                                        </th>
                                        <th>{{ $t("admin.col.valid_until") }}</th>
                                        <th>{{ $t("admin.col.active") }}</th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr
                                        v-for="row in rows"
                                        :key="row.id"
                                    >
                                        <td>
                                            <div class="d-flex align-center">
                                                <code>{{ row.code }}</code>
                                                <v-btn
                                                    icon
                                                    size="x-small"
                                                    variant="text"
                                                    class="ml-1"
                                                    @click="copyText(row.code)"
                                                    :aria-label="
                                                        $t('admin.click_to_copy')
                                                    "
                                                >
                                                    <v-icon
                                                        :icon="mdiContentCopy"
                                                        size="small"
                                                    />
                                                </v-btn>
                                            </div>
                                        </td>
                                        <td>{{ row.note }}</td>
                                        <td style="white-space: pre-line">{{
                                            formatBenefitsForRow(row.benefits)
                                        }}</td>
                                        <td>
                                            {{ row.used_count }} /
                                            {{
                                                row.max_uses === -1
                                                    ? "∞"
                                                    : row.max_uses
                                            }}
                                        </td>
                                        <td>
                                            {{
                                                row.effect_duration_seconds === -1
                                                    ? $t("admin.unlimited")
                                                    : formatDuration(
                                                          row.effect_duration_seconds
                                                      )
                                            }}
                                        </td>
                                        <td>
                                            {{
                                                row.valid_until
                                                    ? new Date(
                                                          row.valid_until
                                                      ).toLocaleString()
                                                    : $t("admin.never_expires")
                                            }}
                                        </td>
                                        <td>
                                            <v-switch
                                                :model-value="row.is_active"
                                                density="compact"
                                                hide-details
                                                inset
                                                @update:model-value="
                                                    toggleActive(
                                                        row,
                                                        $event as unknown as boolean
                                                    )
                                                "
                                            ></v-switch>
                                        </td>
                                        <td>
                                            <v-btn
                                                icon
                                                size="small"
                                                variant="text"
                                                @click="deleteRow(row)"
                                                :aria-label="
                                                    $t('admin.delete_btn')
                                                "
                                            >
                                                <v-icon :icon="mdiDelete" />
                                            </v-btn>
                                        </td>
                                    </tr>
                                    <tr v-if="rows.length === 0">
                                        <td colspan="8" class="text-center">
                                            {{ $t("admin.empty") }}
                                        </td>
                                    </tr>
                                </tbody>
                            </v-table>
                            <div
                                v-if="total > rows.length || offset > 0"
                                class="d-flex justify-end pa-2"
                            >
                                <v-btn
                                    variant="text"
                                    :disabled="offset === 0"
                                    @click="changePage(-1)"
                                    >{{ $t("admin.prev") }}</v-btn
                                >
                                <span class="align-self-center mx-2"
                                    >{{ offset + 1 }} -
                                    {{ offset + rows.length }} / {{ total }}</span
                                >
                                <v-btn
                                    variant="text"
                                    :disabled="offset + rows.length >= total"
                                    @click="changePage(1)"
                                    >{{ $t("admin.next") }}</v-btn
                                >
                            </div>
                        </v-card-text>
                    </v-card>
                </template>
            </v-container>
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
defineOptions({ name: "PageAdmin" })

import { onMounted, onUnmounted, ref, watch } from "vue"
import { useI18n } from "vue-i18n"
import {
    mdiDelete,
    mdiKey,
    mdiLogout,
    mdiMagnify,
    mdiRefresh,
    mdiContentCopy,
} from "@mdi/js"
import AppBarHomeButton from "@/components/AppBarHomeButton.vue"
import { axios, EffectiveLimits, RedeemCodeData, Response } from "@/api"
import {
    showAutoCloseSuccess,
    showDetailWarning,
    dangerousConfirm,
} from "@/plugins/swal"
import { isAxiosError } from "axios"
import { timeDeltaToString } from "@/plugins/i18n"
import { humanFileSize } from "@/utils"

const { t: $t } = useI18n()

const STORAGE_KEY = "clip-admin-token"
const token_input = ref("")
const token = ref("")
const remember_token = ref(true)
const token_remembered = ref(false)
const authed = ref(false)

const rows = ref<RedeemCodeData[]>([])
const total = ref(0)
const offset = ref(0)
const page_size = 30
const search_query = ref("")

const creating = ref(false)

interface CreateForm {
    code: string
    note: string
    count: number
    max_uses: number
    effect_duration_days: number
    valid_until: string
    benefits: Partial<EffectiveLimits>
}

const create_form = ref<CreateForm>({
    code: "",
    note: "",
    count: 1,
    max_uses: -1,
    effect_duration_days: -1,
    valid_until: "",
    benefits: {},
})

const benefit_file_size_mib = ref<number | null>(null)
const benefit_total_size_mib = ref<number | null>(null)
const benefit_max_timeout_days = ref<number | null>(null)

function setAuthInterceptor() {
    axios.defaults.headers.common["X-Admin-Token"] = token.value
}
function clearAuthInterceptor() {
    delete axios.defaults.headers.common["X-Admin-Token"]
}

async function checkToken(via_submit: boolean) {
    const t = token_input.value.trim()
    if (!t) return
    token.value = t
    setAuthInterceptor()
    try {
        await axios.get("/admin/ping")
        authed.value = true
        if (remember_token.value) {
            localStorage.setItem(STORAGE_KEY, t)
            token_remembered.value = true
        } else {
            localStorage.removeItem(STORAGE_KEY)
            token_remembered.value = false
        }
        await reload()
    } catch (e: unknown) {
        if (via_submit) {
            showDetailWarning({
                title: $t("clip.error"),
                text: $t("admin.invalid_token"),
            })
        }
        token.value = ""
        clearAuthInterceptor()
    }
}

function forgetToken() {
    token.value = ""
    token_input.value = ""
    authed.value = false
    rows.value = []
    localStorage.removeItem(STORAGE_KEY)
    token_remembered.value = false
    clearAuthInterceptor()
}

onMounted(async () => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
        token_input.value = stored
        token_remembered.value = true
        await checkToken(false)
    }
})

onUnmounted(() => {
    clearAuthInterceptor()
})

async function reload() {
    if (!authed.value) return
    try {
        const resp = await axios.get<
            Response<{ items: RedeemCodeData[]; total: number }>
        >("/admin/redeem_codes", {
            params: {
                q: search_query.value,
                limit: page_size,
                offset: offset.value,
            },
        })
        rows.value = resp.data?.data?.items ?? []
        total.value = resp.data?.data?.total ?? 0
    } catch (e: unknown) {
        if (isAxiosError(e) && e.response?.status === 403) {
            forgetToken()
        }
    }
}

function changePage(delta: number) {
    offset.value = Math.max(0, offset.value + delta * page_size)
    reload()
}

function gatherBenefits(): Partial<EffectiveLimits> {
    const b: Partial<EffectiveLimits> = {}
    const MIB = 1024 * 1024
    if (
        benefit_file_size_mib.value !== null &&
        benefit_file_size_mib.value !== undefined &&
        !Number.isNaN(benefit_file_size_mib.value) &&
        benefit_file_size_mib.value > 0
    )
        b.max_file_size = Math.floor(benefit_file_size_mib.value * MIB)
    if (
        create_form.value.benefits.max_file_count !== undefined &&
        create_form.value.benefits.max_file_count !== null &&
        !Number.isNaN(create_form.value.benefits.max_file_count) &&
        create_form.value.benefits.max_file_count > 0
    )
        b.max_file_count = Math.floor(create_form.value.benefits.max_file_count)
    if (
        benefit_total_size_mib.value !== null &&
        benefit_total_size_mib.value !== undefined &&
        !Number.isNaN(benefit_total_size_mib.value) &&
        benefit_total_size_mib.value > 0
    )
        b.max_all_file_size = Math.floor(benefit_total_size_mib.value * MIB)
    if (
        benefit_max_timeout_days.value !== null &&
        benefit_max_timeout_days.value !== undefined &&
        !Number.isNaN(benefit_max_timeout_days.value) &&
        benefit_max_timeout_days.value > 0
    )
        b.max_timeout = Math.floor(
            benefit_max_timeout_days.value * 24 * 60 * 60
        )
    return b
}

async function submitCreate() {
    const benefits = gatherBenefits()
    if (Object.keys(benefits).length === 0) {
        showDetailWarning({
            title: $t("clip.error"),
            text: $t("admin.need_benefits"),
        })
        return
    }
    let valid_until: string | null = null
    if (create_form.value.valid_until) {
        const d = new Date(create_form.value.valid_until)
        if (Number.isNaN(d.getTime())) {
            showDetailWarning({
                title: $t("clip.error"),
                text: $t("admin.invalid_date"),
            })
            return
        }
        valid_until = d.toISOString()
    }
    const effect_duration_seconds =
        create_form.value.effect_duration_days < 0
            ? -1
            : Math.floor(create_form.value.effect_duration_days * 24 * 60 * 60)
    creating.value = true
    try {
        await axios.post("/admin/redeem_codes", {
            code: create_form.value.code || undefined,
            note: create_form.value.note,
            count: create_form.value.count,
            max_uses: create_form.value.max_uses,
            valid_until,
            effect_duration_seconds,
            benefits,
        })
        showAutoCloseSuccess({ title: $t("admin.created") })
        // reset code/note/count but keep benefits for batch-creates
        create_form.value.code = ""
        offset.value = 0
        await reload()
    } catch (e: unknown) {
        showDetailWarning({
            title: $t("clip.error"),
            text:
                isAxiosError(e) && e.response?.data?.message
                    ? e.response.data.message
                    : $t("admin.create_failed"),
        })
    } finally {
        creating.value = false
    }
}

async function toggleActive(row: RedeemCodeData, value: boolean) {
    try {
        await axios.put(`/admin/redeem_codes/${row.id}`, { is_active: value })
        row.is_active = value
    } catch {
        showDetailWarning({
            title: $t("clip.error"),
            text: $t("admin.update_failed"),
        })
    }
}

async function deleteRow(row: RedeemCodeData) {
    const result = await dangerousConfirm({
        title: $t("admin.delete_confirm_title"),
        text: $t("admin.delete_confirm_text", [row.code]),
    })
    if (!result.isConfirmed) return
    try {
        await axios.delete(`/admin/redeem_codes/${row.id}`)
        rows.value = rows.value.filter((r) => r.id !== row.id)
        total.value = Math.max(0, total.value - 1)
    } catch {
        showDetailWarning({
            title: $t("clip.error"),
            text: $t("admin.delete_failed"),
        })
    }
}

async function copyText(s: string) {
    try {
        await navigator.clipboard.writeText(s)
        showAutoCloseSuccess({ title: $t("admin.copied"), timer: 800 })
    } catch {
        // ignore
    }
}

function formatBenefitsForRow(b: Partial<EffectiveLimits>): string {
    const out: string[] = []
    if (b.max_file_size)
        out.push(
            $t("clip.redeem.benefit_max_file_size", [
                humanFileSize(b.max_file_size),
            ])
        )
    if (b.max_file_count)
        out.push($t("clip.redeem.benefit_max_file_count", [b.max_file_count]))
    if (b.max_all_file_size)
        out.push(
            $t("clip.redeem.benefit_max_all_file_size", [
                humanFileSize(b.max_all_file_size),
            ])
        )
    if (b.max_timeout)
        out.push(
            $t("clip.redeem.benefit_max_timeout", [
                timeDeltaToString(b.max_timeout),
            ])
        )
    return out.join("\n")
}
function formatDuration(seconds: number): string {
    return timeDeltaToString(seconds)
}

watch(search_query, () => {
    offset.value = 0
})
</script>
