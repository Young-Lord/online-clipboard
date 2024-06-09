<template>
    <v-app>
        <v-app-bar app>
            <v-btn icon @click="goToHome()">
                <v-icon>mdi-home</v-icon>
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
                icon
                href="https://github.com/Young-Lord/online-clipboard"
                target="_blank"
            >
                <v-icon>mdi-github</v-icon>
            </v-btn>
        </v-app-bar>
        <v-main>
            <v-container>
                <p>{{ $t("about.description") }}</p>
                <v-text-field
                    v-model="api_endpoint"
                    :label="$t('about.api_endpoint')"
                    outlined
                    dense
                    append-icon="mdi-check"
                    @click:append="updateEndpoint()"
                ></v-text-field>
                <!--expandable section for metadata prettified-->
                <v-expansion-panels>
                    <v-expansion-panel :title="$t('about.metadata')">
                        <v-expansion-panel-text>
                            <pre><code>{{ JSON.stringify(metadata, null, 4) }}</code></pre>
                        </v-expansion-panel-text>
                    </v-expansion-panel>
                </v-expansion-panels>
            </v-container>
        </v-main>
    </v-app>
</template>

<script lang="ts">
import { MetaData, axios } from "@/api"
import { useAppStore } from "@/store/app"
const appStore = useAppStore()

export default {
    data() {
        return {
            appStore: appStore,
            api_endpoint: appStore.api_endpoint,
            metadata: {} as MetaData,
        }
    },
    methods: {
        async updateEndpoint() {
            await appStore.updateEndpoint(axios, this.api_endpoint)
        },
        goToHome() {
            this.$router.push({ name: "Home" })
        },
    },
}
</script>
