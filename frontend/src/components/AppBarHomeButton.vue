<template>
    <v-btn icon @click="goToHome()" :aria-label="$t('clip.a11y.appbar.home')">
        <v-icon icon="$home" />
    </v-btn>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router"
const router = useRouter()

function goToHome() {
    router.push({ name: "Home" })
}
</script>
