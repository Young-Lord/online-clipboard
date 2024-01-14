// @ts-nocheck
export const BASE_DOMAIN: string = import.meta.env.VITE_BASE_DOMAIN
export const BASE_PATH: string = import.meta.env.VITE_BASE_PATH
const API_SUFFIX: string = import.meta.env.VITE_API_SUFFIX
export const HOMEPAGE_BASEPATH: string = import.meta.env.VITE_HOMEPAGE_BASEPATH
export const API_BASE_PATH: string = BASE_PATH + API_SUFFIX
export const API_ENDPOINT: string = BASE_DOMAIN + API_BASE_PATH
