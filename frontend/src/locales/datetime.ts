import { I18nOptions } from "vue-i18n"

export default {
    en: {
        short: {
            year: "numeric",
            month: "short",
            day: "numeric",
        },
        long: {
            year: "numeric",
            month: "short",
            day: "numeric",
            weekday: "short",
            hour: "numeric",
            minute: "numeric",
        },
    },
    "zh-CN": {
        short: {
            year: "numeric",
            month: "short",
            day: "numeric",
        },
        long: {
            year: "numeric",
            month: "short",
            day: "numeric",
            weekday: "short",
            hour: "numeric",
            minute: "numeric",
            hour12: true,
        },
    },
} as I18nOptions["datetimeFormats"]
