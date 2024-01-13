import { createI18n } from "vue-i18n"
import messages from "@intlify/unplugin-vue-i18n/messages"
import datetime from "../locales/datetime"

const userLanguage = window.navigator.language
const selectedLanguage = userLanguage in messages ? userLanguage : "en"

if (selectedLanguage !== userLanguage) {
    console.warn(
        `Language ${userLanguage} not found, falling back to ${selectedLanguage}`
    )
}

export default createI18n({
    legacy: false,
    globalInjection: true,
    fallbackLocale: "en",
    locale: selectedLanguage,
    datetimeFormats: datetime,
    messages,
})

export const rtf = new Intl.RelativeTimeFormat(selectedLanguage, {
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

export const timeDeltaToString = (seconds) => {
    const millis = seconds * NameToMillis.second
    var ret = undefined
    for (const [name, ms] of Object.entries(NameToMillis)) {
        if (Math.abs(millis) >= ms) {
            ret = rtf.format(Math.trunc(millis / ms), name)
            break
        }
    }
    if (ret === undefined) {
        ret = rtf.format(millis, "second")
    }
    if (userLanguage === "zh-CN") {
        ret = ret.replace(/后$/, "")
    } else if (userLanguage.startsWith("en-")) {
        ret = ret.replace(/^in /, "")
    }
    return ret
}
