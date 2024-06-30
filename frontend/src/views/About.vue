<template>
    <v-app>
        <v-app-bar app>
            <app-bar-home-button />
            <v-spacer></v-spacer>
            <v-btn
                icon
                href="https://github.com/Young-Lord/online-clipboard"
                target="_blank"
                :aria-label="$t('clip.a11y.appbar.github')"
            >
                <v-icon :icon="mdiGithub" />
            </v-btn>
        </v-app-bar>
        <v-main>
            <v-container>
                <p>{{ $t("about.long_description") }}</p>
                <v-text-field
                    v-model="api_endpoint"
                    :label="$t('about.api_endpoint')"
                    outlined
                    dense
                    :append-icon="mdiCheck"
                    @click:append="updateEndpoint()"
                ></v-text-field>
                <!--expandable section for metadata prettified-->
                <v-expansion-panels>
                    <v-expansion-panel :title="$t('about.metadata')">
                        <v-expansion-panel-text>
                            <pre><code>{{ JSON.stringify(appStore.metadata, null, 4) }}</code></pre>
                        </v-expansion-panel-text>
                    </v-expansion-panel>
                </v-expansion-panels>
            </v-container>
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import { mdiGithub, mdiCheck } from "@mdi/js"
import AppBarHomeButton from "@/components/AppBarHomeButton.vue"
import { axios } from "@/api"
import { useAppStore } from "@/store/app"
const appStore = useAppStore()
import { ref } from "vue"
const api_endpoint = ref(appStore.api_endpoint)
async function updateEndpoint() {
    await appStore.updateEndpoint(axios, api_endpoint.value)
}
</script>
