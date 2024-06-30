import mime from "mime/lite"

interface Dictionary<T> {
    [Key: string]: T
}

export function getKeyByValue<T>(
    object: Dictionary<T>,
    value: T
): string | undefined {
    return Object.keys(object).find((key) => object[key] === value)
}

export function replaceLastPartOfUrl(href: string, new_part: string): string {
    // replaceLastPartOfUrl("https://a.com/a/old?aa=1&dd=3#hash", "new") -> "https://a.com/a/new?aa=1&dd=3#hash"
    const url = new URL(href)
    const segments = url.pathname.split("/")
    segments.pop()
    segments.push(new_part)
    url.pathname = segments.join("/")
    return url.href
}

/**
 * Format bytes as human-readable text.
 *
 * @param bytes Number of bytes.
 * @param si True to use metric (SI) units, aka powers of 1000. False to use
 *           binary (IEC), aka powers of 1024.
 * @param dp Number of decimal places to display.
 *
 * @return Formatted string.
 */
export function humanFileSize(
    bytes: number,
    si: boolean = false,
    dp: number = 1,
    remove_suffix_zero: boolean = true
): string {
    // https://stackoverflow.com/a/14919494
    const thresh = si ? 1000 : 1024

    if (Math.abs(bytes) < thresh) {
        return bytes + " B"
    }

    const units = si
        ? ["kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        : ["KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    let u = -1
    const r = 10 ** dp

    do {
        bytes /= thresh
        ++u
    } while (
        Math.round(Math.abs(bytes) * r) / r >= thresh &&
        u < units.length - 1
    )
    let result = bytes.toFixed(dp)
    if (remove_suffix_zero) {
        result = parseFloat(result).toString()
    }
    return result + " " + units[u]
}

export function assert(condition: boolean): asserts condition {
    if (!condition) {
        throw new Error()
    }
}
