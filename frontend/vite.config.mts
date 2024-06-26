// Plugins
import vue from "@vitejs/plugin-vue"
import vuetify, { transformAssetUrls } from "vite-plugin-vuetify"
import path from "path"
import VueI18nPlugin from "@intlify/unplugin-vue-i18n/vite"

// Utilities
import { defineConfig, loadEnv } from "vite"
import { fileURLToPath, URL } from "node:url"
// import { visualizer } from "rollup-plugin-visualizer"

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
    const env = loadEnv(mode, path.resolve(__dirname, ".."))
    return {
        envDir: "..",
        base: env.VITE_BASE_PATH,
        build: {
            outDir: path.resolve(__dirname, "../server/app/templates"),
            assetsDir: "static",
        },
        plugins: [
            vue({
                template: { transformAssetUrls },
            }),
            // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
            vuetify({
                autoImport: true,
                styles: {
                    configFile: "src/styles/settings.scss",
                },
            }),
            VueI18nPlugin({
                include: ["src/locales/*.json"],
            }),
            // Visualize file sizes in build output
            // visualizer({
            //     open: false, // open browser to display stats.html on build complete
            //     filename: "stats.html",
            //     gzipSize: true,
            //     brotliSize: true,
            // }),
        ],
        define: { "process.env": {} },
        resolve: {
            alias: {
                "@": fileURLToPath(new URL("./src", import.meta.url)),
            },
            extensions: [".js", ".json", ".jsx", ".mjs", ".ts", ".tsx", ".vue"],
        },
        server: {
            port: 53000,
        },
    }
})
