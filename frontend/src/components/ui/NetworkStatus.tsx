import{WifiOff}from'lucide-react'
import{useNetworkStatus}from'../../hooks/useNetworkStatus'

export function NetworkStatus(){
 const available=useNetworkStatus()
 if(available)return null
 const offline=!navigator.onLine
 return <div className="network-status" role="status"><WifiOff size={17}/><span><strong>{offline?'Você está sem conexão.':'O app local não respondeu.'}</strong> Conteúdo já aberto pode continuar disponível. Ações que dependem do app local serão retomadas quando ele responder.</span></div>
}
