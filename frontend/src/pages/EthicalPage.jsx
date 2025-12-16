import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Shield, 
  Heart, 
  Users, 
  Lock, 
  Eye, 
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react'

const EthicalPage = () => {
  const [activeSection, setActiveSection] = useState('privacy')

  const sections = [
    { id: 'privacy', label: 'Privacy', icon: Lock },
    { id: 'ethics', label: 'Ethics', icon: Heart },
    { id: 'consent', label: 'Consent', icon: CheckCircle },
    { id: 'sdg', label: 'SDG Impact', icon: Users }
  ]

  const privacyPrinciples = [
    {
      title: 'Data Minimization',
      description: 'We only collect data necessary for mental health analysis',
      icon: Lock
    },
    {
      title: 'Local Processing',
      description: 'All analysis happens on your device when possible',
      icon: Shield
    },
    {
      title: 'No Third-Party Sharing',
      description: 'Your data is never shared with external parties',
      icon: Eye
    },
    {
      title: 'Transparent AI',
      description: 'We explain how AI makes decisions about your mental health',
      icon: Info
    }
  ]

  const ethicalPrinciples = [
    {
      title: 'Beneficence',
      description: 'Our AI is designed to help, not harm, your mental wellbeing',
      icon: Heart
    },
    {
      title: 'Non-Maleficence',
      description: 'We prioritize your safety and mental health above all else',
      icon: Shield
    },
    {
      title: 'Autonomy',
      description: 'You maintain full control over your data and analysis',
      icon: Users
    },
    {
      title: 'Justice',
      description: 'Our AI treats all users fairly and without bias',
      icon: CheckCircle
    }
  ]

  const sdgGoals = [
    {
      goal: 'SDG 3: Good Health and Well-being',
      description: 'Promoting mental health and wellbeing through accessible AI analysis',
      icon: Heart
    },
    {
      goal: 'SDG 10: Reduced Inequalities',
      description: 'Making mental health support accessible to everyone, regardless of location or resources',
      icon: Users
    },
    {
      goal: 'SDG 16: Peace, Justice and Strong Institutions',
      description: 'Ensuring ethical AI practices and data protection for all users',
      icon: Shield
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-green-500 to-blue-600 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center space-x-3">
          <Shield className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Ethics & Privacy</h1>
            <p className="text-green-100">Your data, your rights, your wellbeing</p>
          </div>
        </div>
      </motion.div>

      {/* Navigation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <div className="flex flex-wrap gap-2">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === section.id
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <section.icon className="h-4 w-4 mr-2" />
              {section.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Privacy Section */}
      {activeSection === 'privacy' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Privacy Principles
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {privacyPrinciples.map((principle, index) => (
                <div key={index} className="flex items-start space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="p-2 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
                    <principle.icon className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">{principle.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{principle.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Data Protection Measures
            </h2>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="text-gray-700 dark:text-gray-300">End-to-end encryption for all data transmission</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="text-gray-700 dark:text-gray-300">Local data processing when possible</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="text-gray-700 dark:text-gray-300">Regular security audits and updates</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="text-gray-700 dark:text-gray-300">GDPR and CCPA compliance</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Ethics Section */}
      {activeSection === 'ethics' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Ethical AI Principles
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {ethicalPrinciples.map((principle, index) => (
                <div key={index} className="flex items-start space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                    <principle.icon className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">{principle.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{principle.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Bias Prevention
            </h2>
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Diverse Training Data</h3>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  Our AI models are trained on diverse datasets to prevent bias against any demographic group.
                </p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <h3 className="font-medium text-green-900 dark:text-green-100 mb-2">Regular Bias Audits</h3>
                <p className="text-sm text-green-700 dark:text-green-300">
                  We regularly audit our AI systems for bias and take corrective action when needed.
                </p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <h3 className="font-medium text-purple-900 dark:text-purple-100 mb-2">Transparent Decision Making</h3>
                <p className="text-sm text-purple-700 dark:text-purple-300">
                  We provide clear explanations of how AI decisions are made to ensure transparency.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Consent Section */}
      {activeSection === 'consent' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Informed Consent
            </h2>
            <div className="space-y-4">
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <h3 className="font-medium text-yellow-900 dark:text-yellow-100 mb-2">What We Collect</h3>
                <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                  <li>• Text content you choose to analyze</li>
                  <li>• Images you upload for emotion analysis</li>
                  <li>• Behavioral patterns from your usage</li>
                  <li>• Analysis results and insights</li>
                </ul>
              </div>
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">How We Use Your Data</h3>
                <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                  <li>• To provide mental health analysis</li>
                  <li>• To improve our AI models</li>
                  <li>• To generate personalized insights</li>
                  <li>• To create reports and visualizations</li>
                </ul>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <h3 className="font-medium text-green-900 dark:text-green-100 mb-2">Your Rights</h3>
                <ul className="text-sm text-green-700 dark:text-green-300 space-y-1">
                  <li>• Right to access your data</li>
                  <li>• Right to correct inaccurate data</li>
                  <li>• Right to delete your data</li>
                  <li>• Right to withdraw consent</li>
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* SDG Section */}
      {activeSection === 'sdg' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              UN Sustainable Development Goals
            </h2>
            <div className="space-y-6">
              {sdgGoals.map((goal, index) => (
                <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="p-3 bg-primary-100 dark:bg-primary-900/20 rounded-lg">
                    <goal.icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white mb-2">{goal.goal}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{goal.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Our Impact
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <Heart className="h-8 w-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
                <h3 className="font-medium text-green-900 dark:text-green-100">Mental Health</h3>
                <p className="text-sm text-green-700 dark:text-green-300">Promoting accessible mental health support</p>
              </div>
              <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <Users className="h-8 w-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                <h3 className="font-medium text-blue-900 dark:text-blue-100">Equality</h3>
                <p className="text-sm text-blue-700 dark:text-blue-300">Reducing inequalities in mental health access</p>
              </div>
              <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <Shield className="h-8 w-8 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                <h3 className="font-medium text-purple-900 dark:text-purple-100">Ethics</h3>
                <p className="text-sm text-purple-700 dark:text-purple-300">Ensuring ethical AI practices</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Contact Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
      >
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Questions or Concerns?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-2">Privacy Officer</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Email: privacy@mindscope.ai<br />
              Phone: +1 (555) 123-4567
            </p>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-2">Ethics Committee</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Email: ethics@mindscope.ai<br />
              Phone: +1 (555) 123-4568
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default EthicalPage