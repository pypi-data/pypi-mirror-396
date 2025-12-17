const trimTrailingSlash = (value) => value.replace(/\/+$/, '')

const rawApiBase = import.meta.env.VITE_API_BASE_URL || '/api'
const normalizedBase = trimTrailingSlash(rawApiBase) || '/api'

export const API_BASE_URL = normalizedBase

