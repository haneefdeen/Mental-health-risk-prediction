import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

// Pages
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import AnalyzePostPage from './pages/AnalyzePostPage'
import TimelinePage from './pages/TimelinePage'
import ExplainabilityPage from './pages/ExplainabilityPage'
import ReportsPage from './pages/ReportsPage'
import EthicalPage from './pages/EthicalPage'
import AdminPanelPage from './pages/AdminPanelPage'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Protected routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route index element={<DashboardPage />} />
                <Route path="analyze" element={<AnalyzePostPage />} />
                <Route path="timeline" element={<TimelinePage />} />
                <Route path="explainability" element={<ExplainabilityPage />} />
                <Route path="reports" element={<ReportsPage />} />
                <Route path="ethical" element={<EthicalPage />} />
                <Route path="admin" element={<AdminPanelPage />} />
              </Route>
            </Routes>
            
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'hsl(var(--card))',
                  color: 'hsl(var(--card-foreground))',
                  border: '1px solid hsl(var(--border))',
                },
                success: {
                  iconTheme: {
                    primary: '#22c55e',
                    secondary: '#fff',
                  },
                },
                error: {
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App