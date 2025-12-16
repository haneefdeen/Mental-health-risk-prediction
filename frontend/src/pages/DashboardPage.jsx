import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  TrendingUp, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react'
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Cell, BarChart as RechartsBarChart, Bar } from 'recharts'
import ReactGauge from 'react-gauge-component'
import { useAuth } from '../contexts/AuthContext'
import { generateMockData, getStressColor, getStressBgColor } from '../utils/utils'

const DashboardPage = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState(null)

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      setLoading(true)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockData = {
        recentAnalysis: {
          stress_level: 'medium',
          confidence: 0.75,
          emotion: 'neutral',
          timestamp: new Date().toISOString()
        },
        behavioralScore: 0.65,
        totalAnalyses: 24,
        weeklyTrend: generateMockData('stress', 7),
        emotionDistribution: [
          { name: 'Joy', value: 35, color: '#22c55e' },
          { name: 'Neutral', value: 30, color: '#6b7280' },
          { name: 'Sadness', value: 20, color: '#3b82f6' },
          { name: 'Anger', value: 10, color: '#ef4444' },
          { name: 'Fear', value: 5, color: '#8b5cf6' }
        ],
        activityLevel: 'medium',
        recommendations: [
          'Consider practicing mindfulness meditation',
          'Maintain regular sleep schedule',
          'Engage in physical activity'
        ]
      }
      
      setDashboardData(mockData)
      setLoading(false)
    }
    
    loadDashboardData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
      </div>
    )
  }

  const { recentAnalysis, behavioralScore, totalAnalyses, weeklyTrend, emotionDistribution, activityLevel, recommendations } = dashboardData

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-6 text-white"
      >
        <h1 className="text-2xl font-bold mb-2">
          Welcome back, {user?.full_name || user?.username}!
        </h1>
        <p className="text-blue-100">
          Here's your mental health analysis overview
        </p>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Current Stress Level</p>
              <p className={`text-2xl font-bold ${getStressColor(recentAnalysis.stress_level)}`}>
                {recentAnalysis.stress_level.toUpperCase()}
              </p>
            </div>
            <div className={`p-3 rounded-full ${getStressBgColor(recentAnalysis.stress_level)}`}>
              <AlertTriangle className="h-6 w-6" />
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
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Behavioral Score</p>
              <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                {Math.round(behavioralScore * 100)}%
              </p>
            </div>
            <div className="p-3 rounded-full bg-primary-100 dark:bg-primary-900/20">
              <Activity className="h-6 w-6 text-primary-600 dark:text-primary-400" />
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
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {totalAnalyses}
              </p>
            </div>
            <div className="p-3 rounded-full bg-gray-100 dark:bg-gray-700">
              <Brain className="h-6 w-6 text-gray-600 dark:text-gray-400" />
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
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Activity Level</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {activityLevel.toUpperCase()}
              </p>
            </div>
            <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/20">
              <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stress Trend Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Stress Trend</h3>
            <TrendingUp className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsLineChart data={weeklyTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="stress" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                />
              </RechartsLineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Emotion Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Emotion Distribution</h3>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={emotionDistribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {emotionDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Risk Assessment Gauge */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Risk Assessment</h3>
          <BarChart3 className="h-5 w-5 text-gray-400" />
        </div>
        <div className="flex justify-center">
          <ReactGauge
            value={recentAnalysis.stress_level === 'high' ? 80 : recentAnalysis.stress_level === 'medium' ? 50 : 20}
            minValue={0}
            maxValue={100}
            arc={{
              colorArray: ['#10b981', '#f59e0b', '#ef4444'],
              subArcs: [
                { limit: 33 },
                { limit: 66 },
                { limit: 100 }
              ]
            }}
            pointer={{
              color: '#345243'
            }}
            labels={{
              valueLabel: {
                formatTextValue: (value) => `${Math.round(value)}%`
              }
            }}
          />
        </div>
      </motion.div>

      {/* Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">AI Recommendations</h3>
          <Clock className="h-5 w-5 text-gray-400" />
        </div>
        <div className="space-y-3">
          {recommendations.map((recommendation, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-gray-700 dark:text-gray-300">{recommendation}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

export default DashboardPage