# MindScope AI - Frontend

A modern, production-ready React frontend for the MindScope AI mental health analysis platform.

## 🚀 Features

### ✨ User Interface
- **Modern Design**: Clean, professional UI with TailwindCSS
- **Dark/Light Theme**: Toggle between themes with localStorage persistence
- **Responsive**: Fully responsive design for all screen sizes
- **Animations**: Smooth micro-animations with Framer Motion
- **Glassmorphism**: Modern glass effects and gradients

### 🔐 Authentication
- **Dual Login Modes**: Separate interfaces for users and doctors
- **JWT Integration**: Secure token-based authentication
- **Protected Routes**: Role-based access control
- **Session Management**: Persistent login state

### 📊 Analysis Features
- **Text Analysis**: Upload and analyze text for emotional patterns
- **Image Analysis**: Upload images for facial emotion detection
- **Risk Assessment**: Visual gauge charts for stress/anxiety levels
- **Coping Suggestions**: AI-powered wellness recommendations

### 📈 Data Visualization
- **Timeline Charts**: Track emotional trends over time
- **Risk Distribution**: Pie charts for population analytics
- **Trend Analysis**: Line and area charts with multiple metrics
- **Interactive Charts**: Hover tooltips and responsive design

### 🔍 AI Explainability
- **Token Importance**: Highlight important words in text analysis
- **Attention Weights**: Show model attention patterns
- **GradCAM Visualization**: Image attention heatmaps
- **Feature Attribution**: Explain AI decision-making

### 📋 Reports & Export
- **PDF Reports**: Professional reports with charts and insights
- **JSON Export**: Raw data export for further analysis
- **Data Management**: View, export, and delete personal data
- **Privacy Controls**: Granular consent management

### 👨‍⚕️ Admin Dashboard
- **Population Analytics**: Aggregated user statistics
- **Risk Monitoring**: Flag high-risk users
- **System Health**: Monitor AI model performance
- **Trend Analysis**: Population-level mental health trends

## 🛠️ Tech Stack

- **React 18**: Modern React with hooks and context
- **Vite**: Fast build tool and development server
- **TailwindCSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **React Router**: Client-side routing
- **Recharts**: Data visualization library
- **React Gauge Chart**: Risk assessment gauges
- **Axios**: HTTP client for API calls
- **React Hot Toast**: Toast notifications
- **Lucide React**: Modern icon library

## 📦 Installation

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Build for Production**:
   ```bash
   npm run build
   ```

## 🚀 Quick Start

### Windows
```bash
# Run the complete frontend setup
.\start_frontend.bat
```

### Manual Setup
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Pages & Features

### Public Pages
- **Login Page**: User/Doctor authentication
- **Register Page**: Account creation with validation

### User Pages
- **Dashboard**: Overview with charts and recent analyses
- **Analyze Post**: Text and image analysis interface
- **Timeline**: Emotional trends over time
- **Explainability**: AI decision transparency
- **Reports**: Export and data management
- **Privacy & Ethics**: Data protection and consent

### Doctor Pages
- **Admin Panel**: Population analytics and user monitoring
- **Risk Assessment**: Flagged users and trends
- **System Health**: AI model monitoring

## 🎨 Design System

### Colors
- **Primary**: Blue gradient (#2563eb to #8b5cf6)
- **Success**: Green (#10b981)
- **Warning**: Yellow (#f59e0b)
- **Danger**: Red (#ef4444)
- **Muted**: Gray variations

### Typography
- **Headings**: Inter font family
- **Body**: System font stack
- **Sizes**: Responsive typography scale

### Components
- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Hover effects and loading states
- **Forms**: Focus states and validation
- **Charts**: Responsive with custom tooltips

## 🔧 Configuration

### Environment Variables
Create `.env.local`:
```env
VITE_API_URL=http://localhost:8000
```

### TailwindCSS
Custom configuration in `tailwind.config.js`:
- Dark mode support
- Custom color palette
- Animation utilities
- Glassmorphism effects

## 📱 Responsive Design

- **Mobile**: Optimized for phones (320px+)
- **Tablet**: Adapted for tablets (768px+)
- **Desktop**: Full features on desktop (1024px+)
- **Large**: Enhanced experience on large screens (1400px+)

## 🎯 Performance

- **Code Splitting**: Lazy loading for routes
- **Bundle Optimization**: Vite's built-in optimizations
- **Image Optimization**: Responsive images
- **Caching**: Efficient data caching strategies

## 🔒 Security

- **XSS Protection**: Sanitized inputs
- **CSRF Protection**: Token-based requests
- **Data Validation**: Client-side validation
- **Secure Storage**: Encrypted localStorage

## 🧪 Testing

```bash
# Run tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run linting
npm run lint
```

## 📦 Build & Deploy

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run preview
```

### Deployment
The built files in `dist/` can be deployed to any static hosting service:
- Vercel
- Netlify
- AWS S3
- GitHub Pages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact: support@mindscope-ai.com
- Documentation: [docs.mindscope-ai.com](https://docs.mindscope-ai.com)

---

**MindScope AI** - Empowering mental health through AI technology 🧠💙
