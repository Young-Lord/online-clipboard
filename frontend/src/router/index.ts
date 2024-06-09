import { BASE_PATH } from "@/config"
import { createRouter, createWebHistory } from "vue-router"

const routes = [
    {
        name: "Home",
        path: "/",
        component: () => import("@/views/Home.vue"),
    },
    {
        name: "About",
        path: "/about",
        component: () => import("@/views/About.vue"),
    },
    {
        name: "Clip",
        path: "/:name",
        component: () => import("@/views/Clip.vue"),
    },
    {
        name: "Mail Setting",
        path: "/mail/:address?",
        component: () => import("@/views/MailSetting.vue"),
    },
]

const router = createRouter({
    history: createWebHistory(BASE_PATH),
    routes,
})

export default router
