export const CREDENTIAL_PROFILE=Object.freeze({
 algorithm:'PBKDF2',
 hash:'SHA-256',
 iterations:600000,
 saltBytes:16,
 derivedBytes:32,
 version:'v1'
})

const encoder=new TextEncoder()

function base64url(bytes){
 let text=''
 for(const byte of bytes)text+=String.fromCharCode(byte)
 return btoa(text).replaceAll('+','-').replaceAll('/','_').replaceAll('=','')
}

export async function deriveCredential(password,salt){
 if(typeof password!=='string'||password.length<12||password.length>256)throw new Error('Password length is invalid.')
 if(!(salt instanceof Uint8Array)||salt.byteLength!==CREDENTIAL_PROFILE.saltBytes)throw new Error('Credential salt is invalid.')
 const key=await crypto.subtle.importKey('raw',encoder.encode(password),CREDENTIAL_PROFILE.algorithm,false,['deriveBits'])
 const bits=await crypto.subtle.deriveBits({name:CREDENTIAL_PROFILE.algorithm,hash:CREDENTIAL_PROFILE.hash,salt,iterations:CREDENTIAL_PROFILE.iterations},key,CREDENTIAL_PROFILE.derivedBytes*8)
 return `pbkdf2-sha256$${CREDENTIAL_PROFILE.version}$${CREDENTIAL_PROFILE.iterations}$${base64url(salt)}$${base64url(new Uint8Array(bits))}`
}
