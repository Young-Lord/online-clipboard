import globals from "globals"
import pluginJs from "@eslint/js"
import tseslint from "typescript-eslint"
import pluginVue from "eslint-plugin-vue"

export default [
    {
        ignores: ["src/tools/diff_match_patch.js", "src/vite-env.d.ts"],
    },
    { files: ["**/*.{js,mjs,cjs,ts,vue}"] },
    { languageOptions: { globals: globals.browser } },
    pluginJs.configs.recommended,
    ...tseslint.configs.recommended,
    ...pluginVue.configs["flat/essential"],
    {
        rules: {
            "@typescript-eslint/no-unused-vars": "off",
            "vue/multi-word-component-names": "off",
        },
    }
]
