<template>
    <v-app>
        <v-app-bar app>
            <app-bar-home-button />
        </v-app-bar>

        <v-main>
            <v-container>
                <!-- An title showing current static mail address, with a text showing current mail subscription status -->
                <v-card>
                    <div v-if="owned_mail_address">
                        <v-card-title>
                            <span>{{ owned_mail_address }}</span>
                        </v-card-title>
                        <v-card-subtitle>
                            <span>{{
                                $t("setting.mail.status", [
                                    subscription_status_string,
                                ])
                            }}</span>
                        </v-card-subtitle>
                        <!-- Unsubscribe, subscribe, delete account info -->
                        <v-card-actions>
                            <v-btn
                                variant="tonal"
                                :disabled="
                                    subscription_status ===
                                    MailSubscriptionStatus.DENY
                                "
                                @click="
                                    setSubscriptionSetting(
                                        MailSubscriptionSetting.DENY
                                    )
                                "
                            >
                                {{ $t("setting.mail.deny_button") }}
                            </v-btn>
                            <v-btn
                                variant="tonal"
                                :disabled="
                                    subscription_status ===
                                    MailSubscriptionStatus.ACCEPT
                                "
                                @click="
                                    setSubscriptionSetting(
                                        MailSubscriptionSetting.ACCEPT
                                    )
                                "
                            >
                                {{ $t("setting.mail.accept_button") }}
                            </v-btn>
                            <v-btn
                                variant="tonal"
                                @click="
                                    setSubscriptionSetting(
                                        MailSubscriptionSetting.RESET
                                    )
                                "
                            >
                                {{ $t("setting.mail.reset_button") }}
                            </v-btn>
                            <v-btn
                                variant="tonal"
                                @click="
                                    () => {
                                        input_mail_address = owned_mail_address
                                        resendVerificationMail()
                                    }
                                "
                            >
                                {{ $t("setting.mail.resend_request_title") }}
                            </v-btn>
                        </v-card-actions>
                    </div>
                    <div v-else>
                        <v-card-title>
                            {{ $t("setting.mail.resend_request_title") }}
                        </v-card-title>
                        <v-card-text>
                            <v-form @submit.native.prevent>
                                <v-text-field
                                    v-model="input_mail_address"
                                    :label="$t('setting.mail.your_mail')"
                                    required
                                    type="email"
                                    @keydown.enter="resendVerificationMail()"
                                ></v-text-field>
                                <v-btn
                                    color="primary"
                                    block
                                    @click="resendVerificationMail()"
                                    :disabled="!input_mail_address"
                                >
                                    {{ $t("setting.mail.do_request") }}
                                </v-btn>
                            </v-form>
                        </v-card-text>
                        <v-card-text>{{
                            $t("setting.mail.not_received_hint", [
                                appStore.metadata.email,
                            ])
                        }}</v-card-text>
                    </div>
                </v-card>
            </v-container>
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import AppBarHomeButton from "@/components/AppBarHomeButton.vue"
import {
    MailSubscriptionData,
    MailSubscriptionSetting,
    MailSubscriptionStatus,
    Response,
    axios,
} from "@/api"
import { showDetailWarning, showAutoCloseSuccess } from "@/plugins/swal"
import { isAxiosError } from "axios"
import { onBeforeRouteLeave } from "vue-router"
import { onMounted, ref, computed } from "vue"

import { useAppStore } from "@/store/app"
const appStore = useAppStore()

import { useRouter, useRoute } from "vue-router"
const router = useRouter()
const route = useRoute()

import { useI18n } from "vue-i18n"
const { t: $t } = useI18n()

const subscription_status = ref<MailSubscriptionStatus | null>(null)
const input_mail_address = ref("")
const owned_mail_address = route.params.address as string // empty if direct access this page (not from subscription link in email)

const subscription_status_string = computed(() => {
    switch (subscription_status.value) {
        // accept, deny, pending, no_requested, loading
        case MailSubscriptionStatus.ACCEPT:
            return $t("setting.mail.accept")
        case MailSubscriptionStatus.DENY:
            return $t("setting.mail.deny")
        case MailSubscriptionStatus.PENDING:
            return $t("setting.mail.pending")
        case MailSubscriptionStatus.NO_REQUESTED:
            return $t("setting.mail.no_requested")
        case null:
            return $t("loading")
        default:
            return $t("setting.mail.unknown")
    }
})

onMounted(() => {
    if (!appStore.metadata.allow_mail) {
        showDetailWarning({
            title: $t("clip.error"),
            text: $t("clip.mail.MAIL_NOT_ALLOWED"),
        })
        router.push({ name: "Home" })
    }
    // add auth header
    const auth_interceptor = axios.interceptors.request.use((config) => {
        config.headers["Authorization"] = `Bearer ${route.query.jwt}`
        return config
    })
    onBeforeRouteLeave(() => {
        axios.interceptors.request.eject(auth_interceptor)
    })
    if (owned_mail_address) {
        updateSubscriptionStatus()
        switch (route.query.subscribe) {
            case "true":
                setSubscriptionSetting(MailSubscriptionSetting.ACCEPT)
                break
            case "false":
                setSubscriptionSetting(MailSubscriptionSetting.DENY)
                break
        }
    }
})

async function updateSubscriptionStatus(
    status: MailSubscriptionStatus | undefined = undefined
) {
    if (status === undefined) {
        const res = await axios.get<Response<MailSubscriptionData>>(
            `/mail/${owned_mail_address}/settings`
        )
        status = res.data.data.subscribe
    }
    subscription_status.value = status
}
async function setSubscriptionSetting(status: MailSubscriptionSetting) {
    try {
        const res = await axios.post(
            `/mail/${owned_mail_address}/settings`,
            {
                subscribe: status,
            }
        )
        updateSubscriptionStatus(res.data.data.subscribe)
        showAutoCloseSuccess({
            text: $t("setting.mail.update_success"),
        })
    } catch (e) {
        showDetailWarning({
            text: $t("setting.mail.update_failed"),
        })
    }
}
async function resendVerificationMail() {
    try {
        await axios.post(`/mailto/send_verification_mail`, {
            address: input_mail_address.value,
        })
        showAutoCloseSuccess({
            text: $t("setting.mail.resend_request_success"),
        })
    } catch (e) {
        if (isAxiosError(e) && e.response?.status === 400) {
            showDetailWarning({
                text: $t("clip.mail.INVALID_ADDRESS"),
            })
        } else {
            showDetailWarning({
                text: $t("clip.error"),
            })
        }
    }
}
</script>
