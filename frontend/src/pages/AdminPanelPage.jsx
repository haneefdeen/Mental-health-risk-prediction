import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  BarChart3,
  PieChart,
  LineChart,
  Download,
  Eye,
  Shield
} from 'lucide-react'
import { 
  LineChart as RechartsLineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Cell,
  BarChart as RechartsBarChart,
  Bar
} from 'recharts'
import { adminAPI } from '../utils/api'
import { generateMockData } from '../utils/utils'
import toast from 'react-hot-toast'

const AdminPanelPage = () => {
  const [loading, setLoading] = useState(true)
  const [adminData, setAdminData] = useState(null)
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d')

  useEffect(() => {
    loadAdminData()
  }, [selectedTimeRange])

  const loadAdminData = async () => {
    setLoading(true)
    try {
      // Simulate API calls
      const [summaryResult, usersResult, trendsResult, flaggedResult] = await Promise.all([
        adminAPI.getSummary(),
        adminAPI.getUsers(),
        adminAPI.getStressTrends(selectedTimeRange === '7d' ? 7 : selectedTimeRange === '30d' ? 30 : 90),
        adminAPI.getFlaggedUsers()
      ])

      const mockData = {
        summary: {
          total_users: 1247,
          active_users: 892,
          total_analyses: 15643,
          stress_distribution: {
            low: 45,
            medium: 35,
            high: 20
          },
          behavioral_insights: {
            average_behavioral_score: 0.68,
            activity_distribution: {
              low: 25,
              medium: 45,
              high: 30
            },
            users_needing_attention: 23
          }
        },
        users: generateMockData('user', 10),
        trends: generateMockData('stress', selectedTimeRange === '7d' ? 7 : selectedTimeRange === '30d' ? 30 : 90),
        flagged: [
          {
            user_id: 'user_1234',
            behavioral_score: 0.25,
            recent_stress: 0.85,
            total_posts: 45,
            flag_reason: 'high_stress'
          },
          {
            user_id: 'user_5678',
            behavioral_score: 0.28,
            recent_stress: 0.78,
            total_posts: 32,
            flag_reason: 'low_behavioral_score'
          }
        ]
      }

      setAdminData(mockData)
    } catch (error) {
      console.error('Error loading admin data:', error)
      toast.error('Failed to load admin data')
    } finally {
      setLoading(false)
    }
  }

  const handleExportData = async () => {
    try {
      const result = await adminAPI.exportData()
      const dataStr = JSON.stringify(result.data, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'admin_export.json'
      link.click()
      URL.revokeObjectURL(url)
      toast.success('Data exported successfully')
    } catch (error) {
      console.error('Export error:', error)
      toast.error('Failed to export data')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
      </div>
    )
  }

  const { summary, users, trends, flagged } = adminData

  const stressDistributionData = [
    { name: 'Low', value: summary.stress_distribution.low, color: '#22c55e' },
    { name: 'Medium', value: summary.stress_distribution.medium, color: '#f59e0b' },
    { name: 'High', value: summary.stress_distribution.high, color: '#ef4444' }
  ]

  const activityDistributionData = [
    { name: 'Low', value: summary.behavioral_insights.activity_distribution.low, color: '#6b7280' },
    { name: 'Medium', value: summary.behavioral_insights.activity_distribution.medium, color: '#3b82f6' },
    { name: 'High', value: summary.behavioral_insights.activity_distribution.high, color: '#8b5cf6' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-red-500 to-orange-600 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Users className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold">Admin Dashboard</h1>
              <p className="text-red-100">Mental health analytics and user management</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="px-3 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-white/50"
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
            <button
              onClick={handleExportData}
              className="flex items-center px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
            >
              <Download className="h-4 w-4 mr-2" />
              Export Data
            </button>
          </div>
        </div>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Users</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.total_users}</p>
            </div>
            <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900/20">
              <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Users</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.active_users}</p>
            </div>
            <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/20">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Analyses</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.total_analyses}</p>
            </div>
            <div className="p-3 rounded-full bg-purple-100 dark:bg-purple-900/20">
              <BarChart3 className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Need Attention</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">{summary.behavioral_insights.users_needing_attention}</p>
            </div>
            <div className="p-3 rounded-full bg-red-100 dark:bg-red-900/20">
              <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stress Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Stress Distribution</h3>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={stressDistributionData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {stressDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Activity Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Activity Distribution</h3>
            <BarChart3 className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsBarChart data={activityDistributionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" />
              </RechartsBarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Stress Trends */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Stress Trends Over Time</h3>
          <LineChart className="h-5 w-5 text-gray-400" />
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <RechartsLineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="stress" 
                stroke="#ef4444" 
                strokeWidth={2}
                dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
              />
            </RechartsLineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Flagged Users */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Users Needing Attention</h3>
          <AlertTriangle className="h-5 w-5 text-red-500" />
        </div>
        
        {flagged.length > 0 ? (
          <div className="space-y-3">
            {flagged.map((user, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                    <AlertTriangle className="h-4 w-4 text-red-600 dark:text-red-400" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{user.user_id}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {user.flag_reason === 'high_stress' ? 'High stress levels detected' : 'Low behavioral score'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Behavioral Score</p>
                    <p className="font-medium text-red-600 dark:text-red-400">
                      {Math.round(user.behavioral_score * 100)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Recent Stress</p>
                    <p className="font-medium text-red-600 dark:text-red-400">
                      {Math.round(user.recent_stress * 100)}%
                    </p>
                  </div>
                  <button className="p-2 text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">
                    <Eye className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">No users currently need attention</p>
          </div>
        )}
      </motion.div>

      {/* User Analytics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          User Analytics Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <Users className="h-8 w-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
            <h4 className="font-medium text-blue-900 dark:text-blue-100">User Engagement</h4>
            <p className="text-sm text-blue-700 dark:text-blue-300">
              {Math.round((summary.active_users / summary.total_users) * 100)}% active users
            </p>
          </div>
          <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <TrendingUp className="h-8 w-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
            <h4 className="font-medium text-green-900 dark:text-green-100">Average Behavioral Score</h4>
            <p className="text-sm text-green-700 dark:text-green-300">
              {Math.round(summary.behavioral_insights.average_behavioral_score * 100)}%
            </p>
          </div>
          <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <BarChart3 className="h-8 w-8 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
            <h4 className="font-medium text-purple-900 dark:text-purple-100">Analyses per User</h4>
            <p className="text-sm text-purple-700 dark:text-purple-300">
              {Math.round(summary.total_analyses / summary.total_users)} average
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default AdminPanelPage