import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Home, 
  Brain, 
  TrendingUp, 
  Eye, 
  FileText, 
  Shield, 
  Settings,
  X,
  Menu
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { cn } from '../utils/utils'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Analyze', href: '/analyze', icon: Brain },
  { name: 'Timeline', href: '/timeline', icon: TrendingUp },
  { name: 'Explainability', href: '/explainability', icon: Eye },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Privacy', href: '/ethical', icon: Shield },
]

const adminNavigation = [
  { name: 'Admin Panel', href: '/admin', icon: Settings },
]

const Sidebar = ({ open, setOpen }) => {
  const location = useLocation()
  const { user } = useAuth()

  const isAdmin = user?.user_type === 'admin'

  return (
    <>
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 lg:hidden"
            onClick={() => setOpen(false)}
          >
            <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ x: open ? 0 : -256 }}
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Brain className="h-5 w-5 text-white" />
                </div>
              </div>
              <div className="ml-3">
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                  MindScope AI
                </h1>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                    isActive
                      ? "bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400"
                      : "text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
                  )}
                  onClick={() => setOpen(false)}
                >
                  <item.icon
                    className={cn(
                      "mr-3 h-5 w-5 flex-shrink-0",
                      isActive
                        ? "text-primary-500"
                        : "text-gray-400 group-hover:text-gray-500 dark:text-gray-400 dark:group-hover:text-gray-300"
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}

            {/* Admin section */}
            {isAdmin && (
              <>
                <div className="border-t border-gray-200 dark:border-gray-700 my-4" />
                <div className="px-3 py-2">
                  <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Administration
                  </h3>
                </div>
                {adminNavigation.map((item) => {
                  const isActive = location.pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={cn(
                        "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                        isActive
                          ? "bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400"
                          : "text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
                      )}
                      onClick={() => setOpen(false)}
                    >
                      <item.icon
                        className={cn(
                          "mr-3 h-5 w-5 flex-shrink-0",
                          isActive
                            ? "text-primary-500"
                            : "text-gray-400 group-hover:text-gray-500 dark:text-gray-400 dark:group-hover:text-gray-300"
                        )}
                      />
                      {item.name}
                    </Link>
                  )
                })}
              </>
            )}
          </nav>

          {/* User info */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {user?.username?.charAt(0).toUpperCase() || 'U'}
                  </span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {user?.full_name || user?.username || 'User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {user?.user_type === 'admin' ? 'Administrator' : 'User'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </>
  )
}

export default Sidebar