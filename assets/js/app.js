// MindScope AI - Professional JavaScript Application
class MindScopeApp {
    constructor() {
        this.currentUser = null;
        this.currentSection = 'dashboard';
        this.charts = {};
        this.analysisHistory = [];
        this.apiBaseUrl = 'http://localhost:8000';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.checkAuth();
        this.updateCurrentDate();
    }

    setupEventListeners() {
        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Analysis forms
        document.getElementById('textAnalysisForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeText();
        });

        document.getElementById('imageAnalysisForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeImage();
        });

        // Global functions
        window.showSection = (section) => this.showSection(section);
        window.toggleTheme = () => this.toggleTheme();
        window.logout = () => this.logout();
        window.generatePDF = () => this.generatePDF();
        window.exportData = () => this.exportData();
    }

    checkAuth() {
        const user = localStorage.getItem('mindscope_user');
        if (user) {
            this.currentUser = JSON.parse(user);
            this.hideLoginModal();
            this.updateUserInterface();
        } else {
            this.showLoginModal();
        }
    }

    showLoginModal() {
        const modal = new bootstrap.Modal(document.getElementById('loginModal'));
        modal.show();
    }

    hideLoginModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
        if (modal) modal.hide();
    }

    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const userType = document.querySelector('input[name="userType"]:checked').value;

        this.showLoading('Authenticating...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    password,
                    user_type: userType
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.currentUser = {
                    username: data.user.username,
                    name: data.user.name,
                    type: data.user.user_type,
                    token: data.access_token
                };
                
                localStorage.setItem('mindscope_user', JSON.stringify(this.currentUser));
                this.hideLoginModal();
                this.hideLoading();
                this.updateUserInterface();
                this.showSection('dashboard');
                this.showNotification('Login successful!', 'success');
            } else {
                throw new Error('Invalid credentials');
            }
        } catch (error) {
            this.hideLoading();
            this.showNotification('Login failed. Please check your credentials.', 'error');
        }
    }

    logout() {
        this.currentUser = null;
        localStorage.removeItem('mindscope_user');
        this.showLoginModal();
        this.showNotification('Logged out successfully!', 'info');
    }

    updateUserInterface() {
        if (this.currentUser) {
            document.getElementById('userName').textContent = this.currentUser.name;
        }
    }

    showSection(section) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.add('d-none');
        });

        // Show selected section
        const targetSection = document.getElementById(section);
        if (targetSection) {
            targetSection.classList.remove('d-none');
            this.currentSection = section;
            this.updateCharts();
        }

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        const activeLink = document.querySelector(`[onclick="showSection('${section}')"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    initializeCharts() {
        this.createEmotionChart();
        this.createStressChart();
        this.createTimelineChart();
    }

    createEmotionChart() {
        const ctx = document.getElementById('emotionChart');
        if (!ctx) return;

        this.charts.emotion = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Emotion Score',
                    data: [65, 70, 75, 80, 85, 82, 88],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    createStressChart() {
        const ctx = document.getElementById('stressChart');
        if (!ctx) return;

        this.charts.stress = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Low', 'Medium', 'High'],
                datasets: [{
                    data: [60, 30, 10],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 0,
                    cutout: '60%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    createTimelineChart() {
        const ctx = document.getElementById('timelineChart');
        if (!ctx) return;

        this.charts.timeline = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Stress Level',
                    data: [45, 38, 42, 35],
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    updateCharts() {
        // Update charts with new data
        if (this.charts.emotion) {
            this.charts.emotion.update();
        }
        if (this.charts.stress) {
            this.charts.stress.update();
        }
        if (this.charts.timeline) {
            this.charts.timeline.update();
        }
    }

    async analyzeText() {
        const text = document.getElementById('textInput').value;
        if (!text.trim()) {
            this.showNotification('Please enter some text to analyze!', 'warning');
            return;
        }

        this.showLoading('Analyzing text...');
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/analyze/text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentUser.token}`
                },
                body: JSON.stringify({
                    text: text,
                    user_id: this.currentUser.username
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayAnalysisResults(result);
                this.hideLoading();
                this.showNotification('Text analysis completed!', 'success');
            } else {
                throw new Error('Analysis failed');
            }
        } catch (error) {
            this.hideLoading();
            this.showNotification('Analysis failed. Please try again.', 'error');
        }
    }

    async analyzeImage() {
        const fileInput = document.getElementById('imageInput');
        if (!fileInput.files[0]) {
            this.showNotification('Please select an image to analyze!', 'warning');
            return;
        }

        this.showLoading('Analyzing image...');
        
        try {
            const file = fileInput.files[0];
            const base64 = await this.fileToBase64(file);
            
            const response = await fetch(`${this.apiBaseUrl}/api/analyze/image`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentUser.token}`
                },
                body: JSON.stringify({
                    image_data: base64,
                    user_id: this.currentUser.username
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayAnalysisResults(result);
                this.hideLoading();
                this.showNotification('Image analysis completed!', 'success');
            } else {
                throw new Error('Analysis failed');
            }
        } catch (error) {
            this.hideLoading();
            this.showNotification('Analysis failed. Please try again.', 'error');
        }
    }

    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    displayAnalysisResults(result) {
        document.getElementById('emotionResult').textContent = result.emotion;
        document.getElementById('stressResult').textContent = result.stress_level;
        document.getElementById('confidenceResult').textContent = Math.round(result.confidence * 100) + '%';
        document.getElementById('timestampResult').textContent = new Date().toLocaleTimeString();

        // Update colors based on results
        const stressElement = document.getElementById('stressResult');
        stressElement.className = 'text-success fw-bold';
        if (result.stress_level === 'medium') stressElement.className = 'text-warning fw-bold';
        if (result.stress_level === 'high') stressElement.className = 'text-danger fw-bold';

        // Display suggestions
        const suggestionsList = document.getElementById('suggestionsList');
        suggestionsList.innerHTML = '';
        
        result.suggestions.forEach((suggestion, index) => {
            const col = document.createElement('div');
            col.className = 'col-md-6 mb-2';
            col.innerHTML = `
                <div class="d-flex align-items-center p-2 bg-light rounded">
                    <i class="bi bi-lightbulb text-warning me-2"></i>
                    <small class="mb-0">${suggestion}</small>
                </div>
            `;
            suggestionsList.appendChild(col);
        });

        document.getElementById('analysisResults').style.display = 'block';
        
        // Update dashboard stats
        this.updateDashboardStats(result);
    }

    updateDashboardStats(result) {
        document.getElementById('currentMood').textContent = result.emotion;
        document.getElementById('stressLevel').textContent = result.stress_level;
        
        // Update risk assessment
        const riskScore = result.stress_level === 'high' ? 75 : result.stress_level === 'medium' ? 50 : 25;
        document.getElementById('riskScore').textContent = riskScore + '%';
        
        const riskBar = document.getElementById('riskBar');
        riskBar.style.width = riskScore + '%';
        riskBar.textContent = result.stress_level === 'high' ? 'High Risk' : 
                            result.stress_level === 'medium' ? 'Medium Risk' : 'Low Risk';
        riskBar.className = result.stress_level === 'high' ? 'progress-bar bg-danger' :
                           result.stress_level === 'medium' ? 'progress-bar bg-warning' :
                           'progress-bar bg-success';
    }

    async generatePDF() {
        this.showLoading('Generating PDF report...');
        
        try {
            // Simulate PDF generation
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Create a simple text report
            const reportContent = `
MindScope AI - Mental Health Report
Generated: ${new Date().toLocaleDateString()}
User: ${this.currentUser.name}

Summary:
- Total Analyses: ${this.analysisHistory.length}
- Current Mood: ${document.getElementById('currentMood').textContent}
- Stress Level: ${document.getElementById('stressLevel').textContent}
- Risk Score: ${document.getElementById('riskScore').textContent}

Recommendations:
- Continue monitoring your mental health
- Practice self-care activities
- Consider professional help if needed
            `;
            
            const blob = new Blob([reportContent], { type: 'text/plain' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `mindscope_report_${new Date().toISOString().split('T')[0]}.txt`;
            link.click();
            
            this.hideLoading();
            this.showNotification('PDF report generated!', 'success');
        } catch (error) {
            this.hideLoading();
            this.showNotification('Failed to generate report.', 'error');
        }
    }

    async exportData() {
        this.showLoading('Exporting data...');
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/reports/export`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.currentUser.token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = `mindscope_data_${new Date().toISOString().split('T')[0]}.json`;
                link.click();
                
                this.hideLoading();
                this.showNotification('Data exported successfully!', 'success');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            this.hideLoading();
            this.showNotification('Export failed. Please try again.', 'error');
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('mindscope_theme', newTheme);
        
        const icon = document.getElementById('themeIcon');
        icon.className = newTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }

    updateCurrentDate() {
        const now = new Date();
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', options);
    }

    showNotification(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';

        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    showLoading(message = 'Loading...') {
        document.getElementById('loadingText').textContent = message;
        document.getElementById('loadingOverlay').classList.remove('d-none');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('d-none');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mindscopeApp = new MindScopeApp();
    
    // Load saved theme
    const savedTheme = localStorage.getItem('mindscope_theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = savedTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }
});