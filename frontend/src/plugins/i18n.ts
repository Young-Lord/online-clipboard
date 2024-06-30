import { createI18n } from "vue-i18n"
import messages from "@intlify/unplugin-vue-i18n/messages"
import { i18nOptions, dayjs } from "../locales/datetime"
import { assert } from "../utils"

const fallbackLanguage = "en"
const userLanguage = window.navigator.language
let selectedLanguage = userLanguage

assert(messages !== undefined)
if (!(userLanguage in messages)) {
    console.warn(
        `Language ${userLanguage} not found, falling back to ${fallbackLanguage}`
    )
    selectedLanguage = fallbackLanguage
}
export const language = selectedLanguage

const i18n = createI18n({
    legacy: false,
    globalInjection: true,
    fallbackLocale: fallbackLanguage,
    locale: selectedLanguage,
    datetimeFormats: i18nOptions,
    messages,
})

export default i18n
export const $t = i18n.global.t
dayjs.locale(selectedLanguage)

document.documentElement.setAttribute("lang", selectedLanguage)
function addHtmlMeta(name: string, content: string): void {
    const headElement = document.head
    let metaElement: Element = document.createElement("meta")
    for (const e of Array.from(headElement.children)) {
        if (e.getAttribute("name") === name) {
            metaElement = e
            break
        }
    }
    metaElement.setAttribute("name", name)
    metaElement.setAttribute("content", content)
    headElement.appendChild(metaElement)
}
addHtmlMeta("description", $t('about.short_description'))

export const timeDeltaToString = (seconds: number): string => {
    return dayjs.duration(seconds, "s").humanize()
}

export { dayjs }
