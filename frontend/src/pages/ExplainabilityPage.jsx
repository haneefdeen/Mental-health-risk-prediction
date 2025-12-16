import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Eye, Brain, Image as ImageIcon, FileText, BarChart3, Info } from 'lucide-react'
import { generateMockData } from '../utils/utils'

const ExplainabilityPage = () => {
  const [activeTab, setActiveTab] = useState('text')
  const [explainabilityData, setExplainabilityData] = useState(null)

  // Mock explainability data
  const mockData = {
    text: {
      tokenImportance: [
        { token: 'stressed', importance: 0.85, position: 0 },
        { token: 'overwhelmed', importance: 0.92, position: 1 },
        { token: 'work', importance: 0.65, position: 2 },
        { token: 'deadline', importance: 0.78, position: 3 },
        { token: 'pressure', importance: 0.88, position: 4 }
      ],
      explanation: "The model identified 'overwhelmed' and 'stressed' as the most important tokens for predicting high stress levels."
    },
    image: {
      attentionRegions: [
        { region: [100, 150, 80, 60], attention_score: 0.85, description: "Facial expression area" },
        { region: [200, 180, 60, 40], attention_score: 0.72, description: "Eye region" }
      ],
      explanation: "The model focused on facial features, particularly the mouth and eye regions, to detect emotional state."
    },
    behavioral: {
      featureWeights: {
        emoji_usage: 0.35,
        posting_frequency: 0.25,
        sentiment_score: 0.40
      },
      explanation: "Sentiment score had the highest influence on the behavioral analysis, followed by emoji usage patterns."
    }
  }

  const tabs = [
    { id: 'text', label: 'Text Analysis', icon: FileText },
    { id: 'image', label: 'Image Analysis', icon: ImageIcon },
    { id: 'behavioral', label: 'Behavioral Analysis', icon: BarChart3 }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center space-x-3">
          <Eye className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">AI Explainability</h1>
            <p className="text-purple-100">Understand how AI makes decisions</p>
          </div>
        </div>
      </motion.div>

      {/* Tab Navigation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <div className="flex space-x-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Explanation */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center space-x-3 mb-4">
            <Info className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              How AI Made This Decision
            </h3>
          </div>
          
          <div className="space-y-4">
            <p className="text-gray-600 dark:text-gray-400">
              {mockData[activeTab].explanation}
            </p>
            
            {activeTab === 'text' && (
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Token Importance</h4>
                <div className="space-y-2">
                  {mockData.text.tokenImportance.map((token, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <span className="font-mono text-sm">{token.token}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full" 
                            style={{ width: `${token.importance * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{Math.round(token.importance * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'image' && (
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Attention Regions</h4>
                <div className="space-y-2">
                  {mockData.image.attentionRegions.map((region, index) => (
                    <div key={index} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">{region.description}</span>
                        <span className="text-sm font-medium">{Math.round(region.attention_score * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'behavioral' && (
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Feature Weights</h4>
                <div className="space-y-2">
                  {Object.entries(mockData.behavioral.featureWeights).map(([feature, weight]) => (
                    <div key={feature} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <span className="text-sm capitalize">{feature.replace('_', ' ')}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full" 
                            style={{ width: `${weight * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{Math.round(weight * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Visualization */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center space-x-3 mb-4">
            <Brain className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              AI Decision Process
            </h3>
          </div>
          
          <div className="space-y-4">
            {activeTab === 'text' && (
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Text Heatmap</h4>
                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="text-sm leading-relaxed">
                    <span className="px-2 py-1 bg-red-200 dark:bg-red-900/30 rounded">stressed</span>
                    <span className="px-2 py-1 bg-red-300 dark:bg-red-800/40 rounded ml-1">overwhelmed</span>
                    <span className="px-2 py-1 bg-yellow-200 dark:bg-yellow-900/30 rounded ml-1">at</span>
                    <span className="px-2 py-1 bg-yellow-200 dark:bg-yellow-900/30 rounded ml-1">work</span>
                    <span className="px-2 py-1 bg-orange-200 dark:bg-orange-900/30 rounded ml-1">with</span>
                    <span className="px-2 py-1 bg-red-200 dark:bg-red-900/30 rounded ml-1">deadline</span>
                    <span className="px-2 py-1 bg-red-300 dark:bg-red-800/40 rounded ml-1">pressure</span>
                  </div>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Color intensity indicates importance: Red = High, Orange = Medium, Yellow = Low
                </p>
              </div>
            )}
            
            {activeTab === 'image' && (
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Grad-CAM Visualization</h4>
                <div className="relative">
                  <div className="w-full h-48 bg-gray-200 dark:bg-gray-600 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <ImageIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-500 dark:text-gray-400">Image with attention overlay</p>
                    </div>
                  </div>
                  <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                    Heatmap
                  </div>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Red areas show where the AI focused most attention
                </p>
              </div>
            )}
            
            {activeTab === 'behavioral' && (
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Feature Importance</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Sentiment Score</span>
                    <div className="w-24 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                      <div className="bg-primary-600 h-2 rounded-full" style={{ width: '40%' }}></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Emoji Usage</span>
                    <div className="w-24 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                      <div className="bg-primary-600 h-2 rounded-full" style={{ width: '35%' }}></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Posting Frequency</span>
                    <div className="w-24 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                      <div className="bg-primary-600 h-2 rounded-full" style={{ width: '25%' }}></div>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Bar length indicates relative importance in the final decision
                </p>
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Additional Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          About AI Explainability
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Why Explainability Matters</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• Builds trust in AI decisions</li>
              <li>• Helps identify potential biases</li>
              <li>• Enables better model improvement</li>
              <li>• Provides transparency for users</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Methods Used</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• Integrated Gradients for text</li>
              <li>• Grad-CAM for images</li>
              <li>• Feature importance analysis</li>
              <li>• Attention mechanism visualization</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default ExplainabilityPage