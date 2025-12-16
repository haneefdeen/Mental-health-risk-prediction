import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  Upload, 
  FileText, 
  Image as ImageIcon, 
  Send,
  AlertCircle,
  CheckCircle,
  Loader
} from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import ReactGauge from 'react-gauge-component'
import { analysisAPI } from '../utils/api'
import { getStressColor, getStressBgColor, getEmotionColor } from '../utils/utils'
import toast from 'react-hot-toast'

const AnalyzePostPage = () => {
  const [text, setText] = useState('')
  const [image, setImage] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('text')

  const onDrop = (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setImage(acceptedFiles[0])
      toast.success('Image uploaded successfully')
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif']
    },
    multiple: false
  })

  const handleAnalyze = async () => {
    if (!text.trim() && !image) {
      toast.error('Please provide text or upload an image')
      return
    }

    setLoading(true)
    try {
      let result
      
      if (text.trim() && image) {
        // Multimodal analysis
        const formData = new FormData()
        formData.append('text', text)
        formData.append('image', image)
        
        result = await analysisAPI.analyzeMultimodal({
          text: text,
          image_data: await convertImageToBase64(image)
        })
      } else if (text.trim()) {
        // Text analysis
        result = await analysisAPI.analyzeText({ text })
      } else if (image) {
        // Image analysis
        const formData = new FormData()
        formData.append('image', image)
        result = await analysisAPI.analyzeImage(formData)
      }

      setAnalysisResult(result.data)
      toast.success('Analysis completed successfully')
    } catch (error) {
      console.error('Analysis error:', error)
      toast.error('Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const convertImageToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result.split(',')[1])
      reader.onerror = error => reject(error)
    })
  }

  const getCopingSuggestions = async (stressLevel) => {
    try {
      const result = await analysisAPI.getCopingGuide(stressLevel)
      return result.data.suggestions
    } catch (error) {
      console.error('Error fetching coping suggestions:', error)
      return []
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center space-x-3">
          <Brain className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Analyze Your Post</h1>
            <p className="text-blue-100">Get AI-powered insights about your mental state</p>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            What would you like to analyze?
          </h2>

          {/* Tab Navigation */}
          <div className="flex space-x-1 mb-6">
            <button
              onClick={() => setActiveTab('text')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'text'
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <FileText className="h-4 w-4 inline mr-2" />
              Text
            </button>
            <button
              onClick={() => setActiveTab('image')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'image'
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <ImageIcon className="h-4 w-4 inline mr-2" />
              Image
            </button>
          </div>

          {/* Text Input */}
          {activeTab === 'text' && (
            <div className="space-y-4">
              <div>
                <label htmlFor="text" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Enter your text
                </label>
                <textarea
                  id="text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Share your thoughts, feelings, or experiences..."
                />
              </div>
            </div>
          )}

          {/* Image Upload */}
          {activeTab === 'image' && (
            <div className="space-y-4">
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                {isDragActive ? (
                  <p className="text-primary-600 dark:text-primary-400">Drop the image here...</p>
                ) : (
                  <div>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">
                      Drag & drop an image here, or click to select
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      Supports JPEG, PNG, GIF
                    </p>
                  </div>
                )}
              </div>
              
              {image && (
                <div className="mt-4">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Selected image:</p>
                  <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <ImageIcon className="h-5 w-5 text-gray-400" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{image.name}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Analyze Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleAnalyze}
            disabled={loading || (!text.trim() && !image)}
            className="w-full mt-6 flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader className="h-4 w-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Analyze Post
              </>
            )}
          </motion.button>
        </motion.div>

        {/* Results Section */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          {analysisResult ? (
            <>
              {/* Analysis Results */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Analysis Results
                </h3>
                
                <div className="space-y-4">
                  {/* Stress Level */}
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Stress Level</p>
                      <p className={`text-lg font-semibold ${getStressColor(analysisResult.stress_level)}`}>
                        {analysisResult.stress_level?.toUpperCase() || 'N/A'}
                      </p>
                    </div>
                    <div className={`p-3 rounded-full ${getStressBgColor(analysisResult.stress_level)}`}>
                      <AlertCircle className="h-6 w-6" />
                    </div>
                  </div>

                  {/* Emotion */}
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Detected Emotion</p>
                      <p className={`text-lg font-semibold ${getEmotionColor(analysisResult.emotion)}`}>
                        {analysisResult.emotion?.toUpperCase() || 'N/A'}
                      </p>
                    </div>
                    <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900/20">
                      <Brain className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>

                  {/* Confidence */}
                  <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Confidence</p>
                      <p className="text-lg font-semibold text-gray-900 dark:text-white">
                        {Math.round((analysisResult.confidence || 0) * 100)}%
                      </p>
                    </div>
                    <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/20">
                      <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Risk Assessment Gauge */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Risk Assessment
                </h3>
                <div className="flex justify-center">
                  <ReactGauge
                    value={analysisResult.stress_level === 'high' ? 80 : analysisResult.stress_level === 'medium' ? 50 : 20}
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
              </div>

              {/* Additional Insights */}
              {analysisResult.emoji_analysis && (
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Emoji Analysis
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                        {analysisResult.emoji_analysis.total_emojis || 0}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total Emojis</p>
                    </div>
                    <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {analysisResult.emoji_analysis.positive_emojis || 0}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Positive</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="text-center py-8">
                <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Ready to Analyze
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Enter text or upload an image to get started with your mental health analysis.
                </p>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default AnalyzePostPage