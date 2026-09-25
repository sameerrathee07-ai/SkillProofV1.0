import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import api from '../services/api'
import { User } from '../types'

interface AuthContextType {
  user: User | null
  login: (email: string, password: string, role: 'poster' | 'solver') => Promise<void>
  signup: (email: string, password: string, name: string, role: 'poster' | 'solver') => Promise<void>
  logout: () => Promise<void>
  loading: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchMe = async () => {
    try {
      const resp = await api.get('/auth/me')
      setUser(resp.data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMe()
  }, [])

  const login = async (email: string, password: string, _role: 'poster' | 'solver') => {
    const resp = await api.post('/auth/login', { email, password })
    setUser(resp.data)
  }

  const signup = async (email: string, password: string, name: string, _role: 'poster' | 'solver') => {
    const resp = await api.post('/auth/signup', { email, password, name, role: _role })
    setUser(resp.data)
  }

  const logout = async () => {
    await api.post('/auth/logout')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}