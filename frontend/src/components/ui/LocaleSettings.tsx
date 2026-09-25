import{useEffect,useState}from'react'
import{LOCALE_STORAGE_KEY,localeStatus,preferredLocale,type PreferredLocale}from'../../services/locale'

export function LocaleSettings(){
  const[locale,setLocale]=useState<PreferredLocale>(()=>preferredLocale(localStorage.getItem(LOCALE_STORAGE_KEY)))
  useEffect(()=>{localStorage.setItem(LOCALE_STORAGE_KEY,locale);document.documentElement.lang='pt-BR';document.documentElement.dataset.preferredLocale=locale},[locale])
  return <section className="panel"><h2>Idioma</h2><p>Português é o conteúdo completo. Outros idiomas só serão publicados após revisão editorial humana.</p><label className="form-label" htmlFor="preferred-locale">Preferência de idioma</label><select id="preferred-locale" value={locale} onChange={event=>setLocale(preferredLocale(event.target.value))}><option value="pt-BR">Português (completo)</option><option value="en">English (fallback em português)</option><option value="es">Español (fallback em português)</option></select><p className="muted small" role="status">{localeStatus(locale)}</p></section>
}
