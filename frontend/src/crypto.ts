const PBKDF2_ITERATIONS = 600000
const SALT_LENGTH = 16
const IV_LENGTH = 12

function b64encode(buf: Uint8Array): string {
    let binary = ""
    const chunk = 0x8000
    for (let i = 0; i < buf.length; i += chunk) {
        binary += String.fromCharCode(...buf.subarray(i, i + chunk))
    }
    return btoa(binary)
}

function b64decode(s: string): Uint8Array {
    return Uint8Array.from(atob(s), c => c.charCodeAt(0))
}

async function deriveKey(password: string, salt: Uint8Array, usage: KeyUsage[]): Promise<CryptoKey> {
    const enc = new TextEncoder()
    const keyMaterial = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveKey"])
    return crypto.subtle.deriveKey(
        { name: "PBKDF2", salt, iterations: PBKDF2_ITERATIONS, hash: "SHA-256" },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        false,
        usage,
    )
}

export interface EncryptedData {
    salt: string
    iv: string
    ciphertext: string
}

export async function encrypt(plaintext: string, password: string): Promise<EncryptedData> {
    const salt = crypto.getRandomValues(new Uint8Array(SALT_LENGTH))
    const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH))
    const key = await deriveKey(password, salt, ["encrypt"])
    const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(plaintext))
    return { salt: b64encode(salt), iv: b64encode(iv), ciphertext: b64encode(new Uint8Array(ct)) }
}

export async function decrypt(data: EncryptedData, password: string): Promise<string> {
    const key = await deriveKey(password, b64decode(data.salt), ["decrypt"])
    const pt = await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64decode(data.iv) }, key, b64decode(data.ciphertext))
    return new TextDecoder().decode(pt)
}

export async function encryptFileData(data: ArrayBuffer, password: string): Promise<EncryptedData> {
    const salt = crypto.getRandomValues(new Uint8Array(SALT_LENGTH))
    const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH))
    const key = await deriveKey(password, salt, ["encrypt"])
    const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, data)
    return { salt: b64encode(salt), iv: b64encode(iv), ciphertext: b64encode(new Uint8Array(ct)) }
}

export async function decryptFileData(data: EncryptedData, password: string): Promise<ArrayBuffer> {
    const key = await deriveKey(password, b64decode(data.salt), ["decrypt"])
    return crypto.subtle.decrypt({ name: "AES-GCM", iv: b64decode(data.iv) }, key, b64decode(data.ciphertext))
}

export async function encryptFilename(filename: string, password: string): Promise<string> {
    return JSON.stringify(await encrypt(filename, password))
}

export async function decryptFilename(encrypted: string, password: string): Promise<string> {
    return decrypt(JSON.parse(encrypted), password)
}

export async function passwordHash(password: string, name: string): Promise<string> {
    const enc = new TextEncoder()
    const keyMaterial = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveBits"])
    const buf = await crypto.subtle.deriveBits(
        { name: "PBKDF2", salt: enc.encode("verify:" + name), iterations: PBKDF2_ITERATIONS, hash: "SHA-256" },
        keyMaterial, 256,
    )
    return b64encode(new Uint8Array(buf))
}
