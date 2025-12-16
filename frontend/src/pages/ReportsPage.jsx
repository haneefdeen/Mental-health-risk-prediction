import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  FileText, 
  Download, 
  Trash2, 
  Shield, 
  Eye,
  Calendar,
  User,
  Brain
} from 'lucide-react'
import { reportAPI } from '../utils/api'
import { exportToPDF, downloadFile } from '../utils/utils'
import toast from 'react-hot-toast'

const ReportsPage = () => {
  const [loading, setLoading] = useState(false)
  const [consentInfo, setConsentInfo] = useState(null)
  const [reports, setReports] = useState([
    {
      id: 1,
      title: 'Weekly Mental Health Report',
      date: '2024-01-15',
      type: 'PDF',
      size: '2.3 MB'
    },
    {
      id: 2,
      title: 'Monthly Analysis Summary',
      date: '2024-01-01',
      type: 'PDF',
      size: '1.8 MB'
    }
  ])

  const handleGeneratePDF = async () => {
    setLoading(true)
    try {
      const result = await reportAPI.generatePDF({
        report_type: 'user',
        include_explainability: true,
        include_behavioral: true
      })
      
      // Download the PDF
      const blob = new Blob([result.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'mindscope_report.pdf'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      toast.success('PDF report generated successfully')
    } catch (error) {
      console.error('PDF generation error:', error)
      toast.error('Failed to generate PDF report')
    } finally {
      setLoading(false)
    }
  }

  const handleExportData = async (format) => {
    setLoading(true)
    try {
      const result = await reportAPI.exportData({
        export_format: format,
        include_analyses: true,
        include_behavioral: true
      })
      
      const filename = `mindscope_data_${new Date().toISOString().split('T')[0]}.${format}`
      downloadFile(JSON.stringify(result.data, null, 2), filename)
      
      toast.success(`Data exported as ${format.toUpperCase()}`)
    } catch (error) {
      console.error('Export error:', error)
      toast.error('Failed to export data')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteData = async () => {
    if (window.confirm('Are you sure you want to delete all your data? This action cannot be undone.')) {
      setLoading(true)
      try {
        await reportAPI.deleteData()
        setReports([])
        toast.success('All data deleted successfully')
      } catch (error) {
        console.error('Delete error:', error)
        toast.error('Failed to delete data')
      } finally {
        setLoading(false)
      }
    }
  }

  const handleGetConsentInfo = async () => {
    try {
      const result = await reportAPI.getConsentInfo()
      setConsentInfo(result.data)
    } catch (error) {
      console.error('Consent info error:', error)
      toast.error('Failed to load consent information')
    }
  }

  const handleUpdateConsent = async (consent) => {
    try {
      await reportAPI.updateConsent(consent)
      toast.success(`Consent updated to ${consent ? 'granted' : 'withdrawn'}`)
    } catch (error) {
      console.error('Consent update error:', error)
      toast.error('Failed to update consent')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center space-x-3">
          <FileText className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Reports & Data</h1>
            <p className="text-indigo-100">Manage your mental health reports and data</p>
          </div>
        </div>
      </motion.div>

      {/* Generate Reports */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Generate Reports
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleGeneratePDF}
            disabled={loading}
            className="flex items-center justify-center p-4 border-2 border-dashed border-primary-300 dark:border-primary-600 rounded-lg hover:border-primary-400 dark:hover:border-primary-500 transition-colors disabled:opacity-50"
          >
            <div className="text-center">
              <FileText className="h-8 w-8 text-primary-600 dark:text-primary-400 mx-auto mb-2" />
              <p className="font-medium text-primary-700 dark:text-primary-300">Generate PDF Report</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Comprehensive analysis report</p>
            </div>
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => handleExportData('json')}
            disabled={loading}
            className="flex items-center justify-center p-4 border-2 border-dashed border-secondary-300 dark:border-secondary-600 rounded-lg hover:border-secondary-400 dark:hover:border-secondary-500 transition-colors disabled:opacity-50"
          >
            <div className="text-center">
              <Download className="h-8 w-8 text-secondary-600 dark:text-secondary-400 mx-auto mb-2" />
              <p className="font-medium text-secondary-700 dark:text-secondary-300">Export JSON Data</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Raw data in JSON format</p>
            </div>
          </motion.button>
        </div>
      </motion.div>

      {/* Existing Reports */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Your Reports
        </h2>
        
        {reports.length > 0 ? (
          <div className="space-y-3">
            {reports.map((report) => (
              <div key={report.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{report.title}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {report.date} • {report.type} • {report.size}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">
                    <Download className="h-4 w-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">No reports generated yet</p>
          </div>
        )}
      </motion.div>

      {/* Data Privacy */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="h-5 w-5 text-primary-600 dark:text-primary-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Data Privacy
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <button
              onClick={handleGetConsentInfo}
              className="w-full flex items-center justify-center p-3 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <Eye className="h-4 w-4 mr-2" />
              View Data Consent Info
            </button>
            
            <button
              onClick={() => handleUpdateConsent(true)}
              className="w-full flex items-center justify-center p-3 border border-green-300 dark:border-green-600 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors text-green-700 dark:text-green-400"
            >
              <Shield className="h-4 w-4 mr-2" />
              Grant Data Consent
            </button>
          </div>
          
          <div className="space-y-4">
            <button
              onClick={() => handleUpdateConsent(false)}
              className="w-full flex items-center justify-center p-3 border border-yellow-300 dark:border-yellow-600 rounded-lg hover:bg-yellow-50 dark:hover:bg-yellow-900/20 transition-colors text-yellow-700 dark:text-yellow-400"
            >
              <Shield className="h-4 w-4 mr-2" />
              Withdraw Data Consent
            </button>
            
            <button
              onClick={handleDeleteData}
              disabled={loading}
              className="w-full flex items-center justify-center p-3 border border-red-300 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-red-700 dark:text-red-400 disabled:opacity-50"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete All Data
            </button>
          </div>
        </div>
        
        {consentInfo && (
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="font-medium text-gray-900 dark:text-white mb-2">Consent Information</h3>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <p><strong>User ID:</strong> {consentInfo.user_id}</p>
              <p><strong>Data Collected:</strong> {consentInfo.data_collected.text_analyses} text analyses</p>
              <p><strong>Consent Status:</strong> {consentInfo.consent_status}</p>
              <p><strong>Rights:</strong> {consentInfo.rights.join(', ')}</p>
            </div>
          </div>
        )}
      </motion.div>

      {/* Privacy Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Privacy & Data Protection
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-2">Your Rights</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• Right to access your data</li>
              <li>• Right to export your data</li>
              <li>• Right to delete your data</li>
              <li>• Right to withdraw consent</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-2">Data Protection</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• Data processed locally</li>
              <li>• No third-party sharing</li>
              <li>• Encrypted storage</li>
              <li>• GDPR compliant</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default ReportsPage