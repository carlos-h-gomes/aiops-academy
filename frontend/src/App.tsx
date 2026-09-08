import { AppLayout } from './components/layout/AppLayout'
import { AcademyProvider } from './context/AcademyContext'

export function App() {
  return <AcademyProvider><AppLayout /></AcademyProvider>
}
