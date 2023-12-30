export const BASE_DOMAIN = import.meta.env.VITE_BASE_DOMAIN
export const BASE_PATH = import.meta.env.VITE_BASE_PATH
const API_SUFFIX = import.meta.env.VITE_API_SUFFIX
export const HOMEPAGE_BASEPATH =
    import.meta.env.VITE_HOMEPAGE_BASEPATH
export const API_BASE_PATH = BASE_PATH + API_SUFFIX
export const API_ENDPOINT = BASE_DOMAIN + API_BASE_PATH
