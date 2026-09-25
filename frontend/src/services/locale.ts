export const LOCALE_STORAGE_KEY='academy-preferred-locale'
export type PreferredLocale='pt-BR'|'en'|'es'

export function preferredLocale(value:unknown):PreferredLocale{
  return value==='en'||value==='es'||value==='pt-BR'?value:'pt-BR'
}

export function localeStatus(value:PreferredLocale){
  if(value==='en')return 'English is not editorially reviewed yet. Portuguese remains active so no lesson is partially translated.'
  if(value==='es')return 'Español todavía no tiene revisión editorial. El contenido sigue en portugués para evitar una traducción parcial.'
  return 'Português é o idioma completo e ativo do curso.'
}
