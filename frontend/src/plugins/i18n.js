import { createI18n } from "vue-i18n"
import messages from "@intlify/unplugin-vue-i18n/messages"
import datetime from "../locales/datetime"

const userLanguage = window.navigator.language
const defaultLanguage = userLanguage in messages ? userLanguage : "en"

if (defaultLanguage !== userLanguage) {
    console.warn(
        `Language ${userLanguage} not found, falling back to ${defaultLanguage}`
    )
}

export default createI18n({
    legacy: false,
    globalInjection: true,
    fallbackLocale: "en",
    locale: defaultLanguage,
    datetimeFormats: datetime,
    messages,
})
