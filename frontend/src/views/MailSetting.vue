<template>
    <v-app>
        <v-app-bar app>
            <v-btn icon @click="goToHome()">
                <v-icon icon="$home" />
            </v-btn>
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
                                metadata.email,
                            ])
                        }}</v-card-text>
                    </div>
                </v-card>
            </v-container>
        </v-main>
    </v-app>
</template>

<script lang="ts">
import {
    MailSubscriptionData,
    MailSubscriptionSetting,
    MailSubscriptionStatus,
    Response,
    axios,
} from "@/api"
import { useAppStore } from "@/store/app"
const appStore = useAppStore()
import {
    showDetailWarning,
    showAutoCloseSuccess,
} from "@/plugins/swal"
import { isAxiosError } from "axios"
import { onBeforeRouteLeave } from "vue-router"

export default {
    data() {
        return {
            subscription_status: null as MailSubscriptionStatus | null,
            input_mail_address: "",
            metadata: appStore.metadata,
            MailSubscriptionStatus: MailSubscriptionStatus,
            MailSubscriptionSetting: MailSubscriptionSetting,
        }
    },
    methods: {
        goToHome() {
            this.$router.push({ name: "Home" })
        },
        async updateSubscriptionStatus(
            status: MailSubscriptionStatus | undefined = undefined
        ) {
            if (status === undefined) {
                const res = await axios.get<Response<MailSubscriptionData>>(
                    `/mail/${this.owned_mail_address}/settings`
                )
                status = res.data.data.subscribe
            }
            this.subscription_status = status
        },
        async setSubscriptionSetting(status: MailSubscriptionSetting) {
            try {
                const res = await axios.post(
                    `/mail/${this.owned_mail_address}/settings`,
                    {
                        subscribe: status,
                    }
                )
                this.updateSubscriptionStatus(res.data.data.subscribe)
                showAutoCloseSuccess({
                    text: this.$t("setting.mail.update_success"),
                })
            } catch (e) {
                showDetailWarning({
                    text: this.$t("setting.mail.update_failed"),
                })
            }
        },
        async resendVerificationMail() {
            try {
                const res = await axios.post(`/mailto/send_verification_mail`, {
                    address: this.input_mail_address,
                })
                showAutoCloseSuccess({
                    text: this.$t("setting.mail.resend_request_success"),
                })
            } catch (e) {
                if (isAxiosError(e) && e.response?.status === 400) {
                    showDetailWarning({
                        text: this.$t("clip.mail.INVALID_ADDRESS"),
                    })
                } else {
                    showDetailWarning({
                        text: this.$t("clip.error"),
                    })
                }
            }
        },
    },
    computed: {
        owned_mail_address(): string {
            return this.$route.params.address as string // empty if direct access this page (not from subscription link in email)
        },
        subscription_status_string(): string {
            switch (this.subscription_status) {
                // accept, deny, pending, no_requested, loading
                case MailSubscriptionStatus.ACCEPT:
                    return this.$t("setting.mail.accept")
                case MailSubscriptionStatus.DENY:
                    return this.$t("setting.mail.deny")
                case MailSubscriptionStatus.PENDING:
                    return this.$t("setting.mail.pending")
                case MailSubscriptionStatus.NO_REQUESTED:
                    return this.$t("setting.mail.no_requested")
                case null:
                    return this.$t("loading")
                default:
                    return this.$t("setting.mail.unknown")
            }
        },
    },
    mounted() {
        if (!appStore.metadata.allow_mail) {
            showDetailWarning({
                title: this.$t("clip.error"),
                text: this.$t("clip.mail.MAIL_NOT_ALLOWED"),
            })
            this.$router.push({ name: "Home" })
        }
        // add auth header
        const auth_interceptor = axios.interceptors.request.use((config) => {
            config.headers["Authorization"] = `Bearer ${this.$route.query.jwt}`
            return config
        })
        onBeforeRouteLeave(() => {
            axios.interceptors.request.eject(auth_interceptor)
        })
        if (this.owned_mail_address) {
            this.updateSubscriptionStatus()
            switch (this.$route.query.subscribe) {
                case "true":
                    this.setSubscriptionSetting(
                        MailSubscriptionSetting.ACCEPT
                    )
                    break
                case "false":
                    this.setSubscriptionSetting(MailSubscriptionSetting.DENY)
                    break
            }
        }
    },
}
</script>

<style></style>
