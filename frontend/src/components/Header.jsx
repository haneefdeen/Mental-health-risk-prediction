import React from 'react'
import { motion } from 'framer-motion'
import { Menu, Sun, Moon, LogOut, User } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { cn } from '../utils/utils'

const Header = ({ setSidebarOpen }) => {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left side */}
        <div className="flex items-center">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <Menu className="h-5 w-5" />
          </button>
          
          <div className="ml-4 lg:ml-0">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              Welcome back, {user?.full_name || user?.username || 'User'}!
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {user?.user_type === 'admin' ? 'Administrator Dashboard' : 'Mental Health Analysis'}
            </p>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Theme toggle */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={toggleTheme}
            className={cn(
              "p-2 rounded-md transition-colors",
              "text-gray-400 hover:text-gray-500 hover:bg-gray-100",
              "dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-700"
            )}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </motion.button>

          {/* User menu */}
          <div className="relative">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <div className="h-8 w-8 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-primary-600 dark:text-primary-400" />
                </div>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {user?.full_name || user?.username || 'User'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {user?.user_type === 'admin' ? 'Administrator' : 'User'}
                  </p>
                </div>
              </div>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={logout}
                className={cn(
                  "p-2 rounded-md transition-colors",
                  "text-gray-400 hover:text-red-500 hover:bg-red-50",
                  "dark:text-gray-400 dark:hover:text-red-400 dark:hover:bg-red-900/20"
                )}
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header