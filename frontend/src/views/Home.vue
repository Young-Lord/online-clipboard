<template>
    <!--vuetify 3, horizonally + vertically centered-->
    <v-container fluid class="fill-height justify-center">
        <v-col cols="12" md="8">
            <v-card elevation="16" variant="tonal">
                <v-card-title>
                    <span class="headline">{{
                        $t("home.welcome_to_clip")
                    }}</span>
                </v-card-title>
                <v-card-subtitle
                    ><!--about button--><a
                        @click="goToAboutPage"
                        style="cursor: pointer"
                        >{{ $t("home.about") }}</a
                    ></v-card-subtitle
                >
                <v-card-text>
                    <v-form @submit.prevent>
                        <v-text-field
                            v-model="name"
                            :label="$t('home.name')"
                            required
                            @keydown.enter="goToClipPage"
                        ></v-text-field>
                        <v-btn
                            color="primary"
                            @click="goToClipPage"
                            :disabled="!name"
                            block
                        >
                            {{ $t("home.go_to_clip") }}
                        </v-btn>
                    </v-form>
                </v-card-text>
            </v-card>
        </v-col>
    </v-container>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
const router = useRouter()

const name = ref("")
function goToClipPage() {
    router.push({
        name: "Clip",
        params: {
            name: name.value,
        },
    })
}
function goToAboutPage() {
    router.push({
        name: "About",
    })
}
</script>
