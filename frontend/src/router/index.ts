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
        path: "/:name",
        name: "Clip",
        component: () => import("@/views/Clip.vue"),
    },
]

const router = createRouter({
    history: createWebHistory(BASE_PATH),
    routes,
})

export default router
