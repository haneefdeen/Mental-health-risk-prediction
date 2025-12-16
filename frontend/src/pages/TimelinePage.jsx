import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Calendar, 
  Activity, 
  BarChart3,
  LineChart,
  PieChart
} from 'lucide-react'
import { 
  LineChart as RechartsLineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar
} from 'recharts'
import { generateMockData, formatDate, getStressColor } from '../utils/utils'

const TimelinePage = () => {
  const [timeRange, setTimeRange] = useState('7d')
  const [chartType, setChartType] = useState('line')
  const [timelineData, setTimelineData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTimelineData()
  }, [timeRange])

  const loadTimelineData = async () => {
    setLoading(true)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90
    const mockData = {
      stressTrend: generateMockData('stress', days),
      emotionTrend: generateMockData('emotion', days),
      behavioralTrend: generateMockData('behavioral', days),
      weeklySummary: {
        averageStress: 0.45,
        dominantEmotion: 'neutral',
        activityLevel: 'medium',
        improvement: '+12%'
      }
    }
    
    setTimelineData(mockData)
    setLoading(false)
  }

  const timeRanges = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' }
  ]

  const chartTypes = [
    { value: 'line', label: 'Line Chart', icon: LineChart },
    { value: 'area', label: 'Area Chart', icon: AreaChart },
    { value: 'bar', label: 'Bar Chart', icon: BarChart3 }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
      </div>
    )
  }

  const { stressTrend, emotionTrend, behavioralTrend, weeklySummary } = timelineData

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-green-500 to-blue-600 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center space-x-3">
          <TrendingUp className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Emotional Timeline</h1>
            <p className="text-green-100">Track your mental health journey over time</p>
          </div>
        </div>
      </motion.div>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          {/* Time Range Selector */}
          <div className="flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-gray-400" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Time Range:</span>
            <div className="flex space-x-1">
              {timeRanges.map((range) => (
                <button
                  key={range.value}
                  onClick={() => setTimeRange(range.value)}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                    timeRange === range.value
                      ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  {range.label}
                </button>
              ))}
            </div>
          </div>

          {/* Chart Type Selector */}
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Chart Type:</span>
            <div className="flex space-x-1">
              {chartTypes.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setChartType(type.value)}
                  className={`p-2 rounded-md transition-colors ${
                    chartType === type.value
                      ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                  title={type.label}
                >
                  <type.icon className="h-4 w-4" />
                </button>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Average Stress</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {Math.round(weeklySummary.averageStress * 100)}%
              </p>
            </div>
            <div className="p-3 rounded-full bg-red-100 dark:bg-red-900/20">
              <Activity className="h-6 w-6 text-red-600 dark:text-red-400" />
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
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Dominant Emotion</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {weeklySummary.dominantEmotion.toUpperCase()}
              </p>
            </div>
            <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900/20">
              <TrendingUp className="h-6 w-6 text-blue-600 dark:text-blue-400" />
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
                {weeklySummary.activityLevel.toUpperCase()}
              </p>
            </div>
            <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/20">
              <BarChart3 className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Improvement</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {weeklySummary.improvement}
              </p>
            </div>
            <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/20">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stress Trend Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Stress Trend</h3>
            <Activity className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              {chartType === 'line' ? (
                <RechartsLineChart data={stressTrend}>
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
              ) : chartType === 'area' ? (
                <AreaChart data={stressTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="stress" 
                    stroke="#ef4444" 
                    fill="#ef4444"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              ) : (
                <RechartsBarChart data={stressTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="stress" fill="#ef4444" />
                </RechartsBarChart>
              )}
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Behavioral Trend Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Behavioral Score</h3>
            <BarChart3 className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              {chartType === 'line' ? (
                <RechartsLineChart data={behavioralTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                  />
                </RechartsLineChart>
              ) : chartType === 'area' ? (
                <AreaChart data={behavioralTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#3b82f6" 
                    fill="#3b82f6"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              ) : (
                <RechartsBarChart data={behavioralTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="score" fill="#3b82f6" />
                </RechartsBarChart>
              )}
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Insights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Timeline Insights
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900 dark:text-white">Positive Trends</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                Stress levels have decreased by 12% this week
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                More positive emotions detected recently
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                Consistent activity patterns observed
              </li>
            </ul>
          </div>
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900 dark:text-white">Areas for Improvement</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
                Consider stress management techniques
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
                Maintain consistent sleep schedule
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
                Practice mindfulness exercises
              </li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default TimelinePage