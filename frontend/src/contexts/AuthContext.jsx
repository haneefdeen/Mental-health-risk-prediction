import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../utils/api'
import toast from 'react-hot-toast'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      verifyToken()
    } else {
      setLoading(false)
    }
  }, [token])

  const verifyToken = async () => {
    try {
      const response = await authAPI.get('/verify')
      setUser(response.data.user)
    } catch (error) {
      console.error('Token verification failed:', error)
      localStorage.removeItem('token')
      setToken(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password, userType) => {
    try {
      const response = await authAPI.post('/login', {
        username,
        password,
        user_type: userType
      })
      
      const { access_token, user: userData } = response.data
      
      localStorage.setItem('token', access_token)
      setToken(access_token)
      setUser(userData)
      
      toast.success(`Welcome back, ${userData.full_name || userData.username}!`)
      return { success: true, user: userData }
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const register = async (username, email, password, fullName, userType) => {
    try {
      const response = await authAPI.post('/register', {
        username,
        email,
        password,
        full_name: fullName,
        user_type: userType
      })
      
      toast.success('Registration successful! Please log in.')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    toast.success('Logged out successfully')
  }

  const value = {
    user,
    loading,
    token,
    login,
    register,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}