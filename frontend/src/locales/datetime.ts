import { I18nOptions } from "vue-i18n"

export const i18nOptions = {
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

import dayjs from "dayjs"
import "dayjs/locale/zh-cn"
import "dayjs/locale/en"
import duration from "dayjs/plugin/duration"
import relativeTime from "dayjs/plugin/relativeTime"
dayjs.extend(duration)
dayjs.extend(relativeTime)

export { dayjs }
