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
document.documentElement.setAttribute("lang", selectedLanguage)
dayjs.locale(selectedLanguage)

const rtf = new Intl.RelativeTimeFormat(selectedLanguage, {
    style: "short",
})

// https://stackoverflow.com/a/67374710
const NameToMillis = {
    year: 1e3 * 60 * 60 * 24 * 365,
    // month: 1e3 * 60 * 60 * 24 * 30,
    // week: 1e3 * 60 * 60 * 24 * 7,
    day: 1e3 * 60 * 60 * 24,
    hour: 1e3 * 60 * 60,
    minute: 1e3 * 60,
    second: 1e3,
}

export const timeDeltaToString = (seconds: number): string => {
    return dayjs.duration(seconds, "s").humanize()
}

export { dayjs }
