import {webcrypto} from 'node:crypto'
import assert from 'node:assert/strict'

globalThis.crypto??=webcrypto
const {CREDENTIAL_PROFILE,deriveCredential}=await import('../src/credential.mjs')

const salt=Uint8Array.from(Buffer.from('00112233445566778899aabbccddeeff','hex'))
const expected='pbkdf2-sha256$v1$600000$ABEiM0RVZneImaq7zN3u_w$zAhH72rWsTArKoEnyqwUzO9ZOGD1CIzAeyhM0LN4Jj8'
assert.equal(CREDENTIAL_PROFILE.iterations,600000)
assert.equal(await deriveCredential('AIOps-Academy vector password',salt),expected)
await assert.rejects(deriveCredential('short',salt))
console.log('PASS credential compatibility vector')
