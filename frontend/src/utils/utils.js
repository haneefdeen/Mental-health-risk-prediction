import { clsx } from 'clsx'

export const cn = (...inputs) => {
  return clsx(inputs)
}

export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export const formatTime = (date) => {
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

export const getStressColor = (level) => {
  switch (level) {
    case 'high':
      return 'text-red-600 dark:text-red-400'
    case 'medium':
      return 'text-yellow-600 dark:text-yellow-400'
    case 'low':
      return 'text-green-600 dark:text-green-400'
    default:
      return 'text-gray-600 dark:text-gray-400'
  }
}

export const getStressBgColor = (level) => {
  switch (level) {
    case 'high':
      return 'bg-red-100 dark:bg-red-900/20'
    case 'medium':
      return 'bg-yellow-100 dark:bg-yellow-900/20'
    case 'low':
      return 'bg-green-100 dark:bg-green-900/20'
    default:
      return 'bg-gray-100 dark:bg-gray-900/20'
  }
}

export const getEmotionColor = (emotion) => {
  switch (emotion) {
    case 'joy':
    case 'happy':
      return 'text-green-600 dark:text-green-400'
    case 'sadness':
    case 'sad':
      return 'text-blue-600 dark:text-blue-400'
    case 'anger':
    case 'angry':
      return 'text-red-600 dark:text-red-400'
    case 'fear':
      return 'text-purple-600 dark:text-purple-400'
    case 'surprise':
      return 'text-yellow-600 dark:text-yellow-400'
    case 'disgust':
      return 'text-orange-600 dark:text-orange-400'
    default:
      return 'text-gray-600 dark:text-gray-400'
  }
}

export const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return 'text-green-600 dark:text-green-400'
  if (confidence >= 0.6) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

export const generateMockData = (type, count = 10) => {
  const data = []
  const now = new Date()
  
  for (let i = 0; i < count; i++) {
    const date = new Date(now.getTime() - (count - i) * 24 * 60 * 60 * 1000)
    
    switch (type) {
      case 'stress':
        data.push({
          date: date.toISOString(),
          stress: Math.random() * 100,
          level: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low'
        })
        break
      case 'emotion':
        const emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust', 'neutral']
        data.push({
          date: date.toISOString(),
          emotion: emotions[Math.floor(Math.random() * emotions.length)],
          confidence: Math.random()
        })
        break
      case 'behavioral':
        data.push({
          date: date.toISOString(),
          score: Math.random(),
          activity: Math.random() > 0.5 ? 'high' : 'low'
        })
        break
      default:
        data.push({
          date: date.toISOString(),
          value: Math.random() * 100
        })
    }
  }
  
  return data
}

export const downloadFile = (data, filename, type = 'application/json') => {
  const blob = new Blob([data], { type })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

export const exportToPDF = async (elementId, filename) => {
  try {
    const { default: html2canvas } = await import('html2canvas')
    const { default: jsPDF } = await import('jspdf')
    
    const element = document.getElementById(elementId)
    if (!element) {
      throw new Error('Element not found')
    }
    
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      allowTaint: true
    })
    
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgWidth = 210
    const pageHeight = 295
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    
    let position = 0
    
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight
    
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }
    
    pdf.save(filename)
  } catch (error) {
    console.error('PDF export failed:', error)
    throw error
  }
}

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

export const validatePassword = (password) => {
  return password.length >= 6
}

export const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}