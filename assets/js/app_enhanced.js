// MindScope AI – Enhanced Frontend wired to Flask backend
class MindScopeApp {
    constructor() {
        this.apiBase = ''; // same origin as Flask (e.g. http://localhost:5000)
        this.token = null;
        this.currentUser = null;
        this.charts = {};
        this.timeline = [];
        this.behavioral = null;
        this.webcamStream = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.restoreSession();
    }

    // ---------------- Auth & session ---------------- //
    restoreSession() {
        const saved = localStorage.getItem('mindscope_session');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                this.token = parsed.token;
                this.currentUser = parsed.user;
            } catch (_) {
                this.token = null;
                this.currentUser = null;
            }
        }
        if (this.token) {
            this.updateUI();
            this.showSection('dashboard');
        } else {
        this.showLoginModal();
        }
        // restore theme
        const savedTheme = localStorage.getItem('mindscope_theme') || 'light';
        const html = document.documentElement;
        const body = document.body;
        html.setAttribute('data-theme', savedTheme);
        body.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'dark') {
            body.classList.add('dark-theme');
        }
        const icon = document.getElementById('theme-icon');
        if (icon) icon.className = savedTheme === 'dark' ? 'bi bi-moon' : 'bi bi-sun';
    }

    setupEventListeners() {
        const textForm = document.getElementById('textAnalysisForm');
        if (textForm) {
            textForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeText();
        });
        }

        const imageForm = document.getElementById('imageAnalysisForm');
        if (imageForm) {
            imageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeImage();
        });
        }

        const imageInput = document.getElementById('imageInput');
        if (imageInput) {
            imageInput.addEventListener('change', (e) => this.handleImageUpload(e));
        }

        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.login();
            });
        }

        const signupForm = document.getElementById('signupForm');
        if (signupForm) {
            signupForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.signup();
            });
        }

        const supportForm = document.getElementById('supportForm');
        if (supportForm) {
            supportForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendSupportMessage();
            });
        }
    }

    get authHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async login() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        if (!username || !password) {
            this.showAlert('Please enter username and password', 'warning');
            return;
        }
        try {
            const res = await fetch(`${this.apiBase}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAlert(data.error || 'Login failed', 'danger');
                return;
            }
            this.token = data.access_token;
                this.currentUser = data.user;
            localStorage.setItem('mindscope_session', JSON.stringify({ token: this.token, user: this.currentUser }));
                this.hideLoginModal();
                this.updateUI();
            this.showSection('dashboard');
            await this.loadDashboard();
        } catch (err) {
            this.showAlert('Login failed. Make sure the Flask server is running.', 'danger');
        }
    }

    async signup() {
        const full_name = document.getElementById('signupName').value.trim();
        const email = document.getElementById('signupEmail').value.trim();
        const username = document.getElementById('signupUsername').value.trim();
        const password = document.getElementById('signupPassword').value;
        const role = document.getElementById('signupRole').value;
        if (!full_name || !email || !username || !password) {
            this.showAlert('Please fill all signup fields', 'warning');
            return;
        }
        try {
            const res = await fetch(`${this.apiBase}/api/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ full_name, email, username, password, role }),
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAlert(data.error || 'Signup failed', 'danger');
                return;
            }
            this.showAlert('Account created. You can now log in.', 'success');
            const signupModal = bootstrap.Modal.getInstance(document.getElementById('signupModal'));
            if (signupModal) signupModal.hide();
        } catch (err) {
            this.showAlert('Signup failed. Please try again.', 'danger');
        }
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('mindscope_session');
        this.updateUI();
        this.showLoginModal();
    }

    showLoginModal() {
        const modal = new bootstrap.Modal(document.getElementById('loginModal'));
        modal.show();
    }

    hideLoginModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
        if (modal) modal.hide();
    }

    updateUI() {
        const nameSpan = document.getElementById('user-name');
        const roleBadge = document.getElementById('user-role-badge');
        if (this.currentUser) {
            if (nameSpan) nameSpan.textContent = this.currentUser.username;
            if (roleBadge) roleBadge.textContent = this.currentUser.role.toUpperCase();
        } else {
            if (nameSpan) nameSpan.textContent = 'Guest';
            if (roleBadge) roleBadge.textContent = 'GUEST';
        }
        const isAdmin = this.currentUser && this.currentUser.role === 'admin';
        const isUser = this.currentUser && this.currentUser.role === 'user';
        
        // Show/hide admin-only elements
        const adminEls = document.querySelectorAll('.admin-only');
        adminEls.forEach(el => {
            el.style.display = isAdmin ? 'block' : 'none';
        });
        
        // Show/hide user-only elements
        const userEls = document.querySelectorAll('.user-only');
        userEls.forEach(el => {
            el.style.display = isUser ? 'block' : 'none';
        });
        
        // Default section based on role
        if (isAdmin && !document.querySelector('.section[style*="block"]')) {
            this.showSection('admin');
        } else if (isUser && !document.querySelector('.section[style*="block"]')) {
            this.showSection('dashboard');
        }
    }

    // ---------------- Navigation ---------------- //
    showSection(sectionName) {
        document.querySelectorAll('.section').forEach(sec => {
            sec.style.display = 'none';
        });
        const target = document.getElementById(sectionName);
        if (target) target.style.display = 'block';

        if (!this.currentUser) return;

        if (sectionName === 'dashboard') this.loadDashboard();
        if (sectionName === 'timeline') this.loadTimeline();
        if (sectionName === 'reports') this.loadReports();
        if (sectionName === 'resources') this.loadResources();
        if (sectionName === 'admin') this.loadAdminPanel();
        if (sectionName === 'messages') this.loadMessages();
    }

    // ---------------- Analysis ---------------- //
    async analyzeText() {
        if (!this.currentUser) {
            this.showAlert('Please login first', 'warning');
            return;
        }
        const text = document.getElementById('textInput').value.trim();
        if (!text) {
            this.showAlert('Please enter some text to analyze', 'warning');
            return;
        }
        this.lastText = text;
        try {
            // Use unified /api/predict endpoint
            const res = await fetch(`${this.apiBase}/api/predict`, {
                method: 'POST',
                headers: this.authHeaders,
                body: JSON.stringify({ mode: 'text', text }),
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAlert(data.error || 'Text analysis failed', 'danger');
                return;
            }
            // New unified response format
            this.displayAnalysisResult(data);
            await this.loadDashboard(true);
        } catch (err) {
            this.showAlert('Text analysis failed. Check backend logs.', 'danger');
        }
    }

    async analyzeImage(base64Override = null, mode = 'image') {
        if (!this.currentUser) {
            this.showAlert('Please login first', 'warning');
            return;
        }
        let imageData = base64Override;
        if (!imageData) {
        const imageInput = document.getElementById('imageInput');
        if (!imageInput.files[0]) {
            this.showAlert('Please select an image to analyze', 'warning');
            return;
        }
        const file = imageInput.files[0];
            imageData = await this.fileToBase64(file);
        }
        // Use unified /api/predict endpoint
        const apiMode = mode === 'webcam' ? 'webcam' : 'image';
        try {
            this.lastImageData = imageData;
            const res = await fetch(`${this.apiBase}/api/predict`, {
                method: 'POST',
                headers: this.authHeaders,
                body: JSON.stringify({ mode: apiMode, image_base64: imageData }),
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAlert(data.error || 'Image analysis failed', 'danger');
                return;
            }
            // New unified response format
            this.displayAnalysisResult(data);
            this.updateOriginalImagePreview();
            await this.loadDashboard(true);
        } catch (err) {
            this.showAlert('Image analysis failed. Check backend logs.', 'danger');
        }
    }

    async analyzeFusion() {
        if (!this.currentUser) {
            this.showAlert('Please login first', 'warning');
            return;
        }
        const text = document.getElementById('textInput').value.trim();
        const imageInput = document.getElementById('imageInput');
        if (!text && (!imageInput || !imageInput.files[0])) {
            this.showAlert('Provide text, image, or both for fusion analysis', 'warning');
            return;
        }
        let imageData = null;
        if (imageInput && imageInput.files[0]) {
            const file = imageInput.files[0];
            imageData = await this.fileToBase64(file);
        }
        this.lastText = text;
        this.lastImageData = imageData;
        const behavioral_data = this.buildBehavioralPayload();
        try {
            // Use unified /api/predict endpoint
            const res = await fetch(`${this.apiBase}/api/predict`, {
                method: 'POST',
                headers: this.authHeaders,
                body: JSON.stringify({ mode: 'fusion', text, image_base64: imageData, behavioral_data }),
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAlert(data.error || 'Fusion analysis failed', 'danger');
                return;
            }
            // New unified response format
            this.displayAnalysisResult(data);
            this.updateOriginalImagePreview();
            await this.loadDashboard(true);
        } catch (err) {
            this.showAlert('Fusion analysis failed. Check backend logs.', 'danger');
        }
    }

    buildBehavioralPayload() {
        if (!this.behavioral) return {};
        const profile = this.behavioral.behavioral_profile || {};
        const emoji_fingerprint = this.behavioral.emoji_fingerprint || {};
        return {
            total_sessions: this.behavioral.total_sessions || 0,
            emoji_fingerprint,
            history: profile.history || [],
        };
    }

    async startWebcam() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showAlert('Webcam not supported on this browser/device. Please upload an image instead.', 'warning');
            return;
        }
        try {
            this.webcamStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            const video = document.getElementById('webcamVideo');
            video.srcObject = this.webcamStream;
        } catch (err) {
            this.showAlert('Camera access denied or unavailable. You can still upload an image.', 'danger');
        }
    }

    async captureWebcam() {
        const video = document.getElementById('webcamVideo');
        const canvas = document.getElementById('webcamCanvas');
        if (!video || !canvas || !video.srcObject) {
            this.showAlert('Start the webcam first.', 'warning');
            return;
        }
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/png');
        const base64 = dataUrl.split(',')[1];
        this.lastImageData = base64;
        this.updateOriginalImagePreview(dataUrl);
        await this.analyzeImage(base64, 'webcam');
    }

    stopWebcam() {
        if (this.webcamStream) {
            this.webcamStream.getTracks().forEach(t => t.stop());
            this.webcamStream = null;
        }
        const video = document.getElementById('webcamVideo');
        if (video) video.srcObject = null;
    }

    handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.getElementById('imagePreview');
                const img = document.getElementById('previewImg');
                img.src = e.target.result;
                preview.style.display = 'block';
                document.getElementById('analyzeImageBtn').disabled = false;
            };
            reader.readAsDataURL(file);
    }

    removeImage() {
        const input = document.getElementById('imageInput');
        if (input) input.value = '';
        const preview = document.getElementById('imagePreview');
        if (preview) preview.style.display = 'none';
        const btn = document.getElementById('analyzeImageBtn');
        if (btn) btn.disabled = true;
    }

    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
        });
    }

    displayAnalysisResult(result) {
        const container = document.getElementById('analysisResults');
        if (!container) return;
        container.style.display = 'block';

        // 1. PRIMARY EMOTION
        const primaryEmotion = result.primary_emotion || {};
        const emotionLabel = primaryEmotion.label || result.emotion || 'Neutral';
        const emotionEmoji = primaryEmotion.emoji || result.emotion_emoji || '😐';
        const emotionDescription = primaryEmotion.description || 'Your emotional tone has been analyzed.';
        
        document.getElementById('primary-emotion-emoji').textContent = emotionEmoji;
        document.getElementById('primary-emotion-label').textContent = emotionLabel;
        document.getElementById('primary-emotion-description').textContent = emotionDescription;

        // 2. STRESS CATEGORY
        const stressCategory = result.stress_category_display || result.stress_category || result.stress_level || 'No Apparent Stress';
        const stressDescription = result.stress_category_description || this.getStressCategoryDescription(stressCategory);
        
        const stressLabelEl = document.getElementById('stress-category-label');
        stressLabelEl.textContent = stressCategory;
        stressLabelEl.className = `fw-bold my-2 ${this.getStressCategoryColorClass(stressCategory)}`;
        document.getElementById('stress-category-description').textContent = stressDescription;

        // 3. OVERALL RISK SCORE
        const riskScore = result.risk_score !== undefined ? Math.round(result.risk_score) : Math.round((result.stress_score || 0.5) * 100);
        const riskLevel = result.risk_level || this.getRiskLevelFromScore(riskScore);
        
        const riskScoreTextEl = document.getElementById('overall-risk-score-text');
        riskScoreTextEl.textContent = `${riskScore}% (${riskLevel})`;
        riskScoreTextEl.className = `fw-bold my-2 ${this.getRiskScoreColorClass(riskScore)}`;
        
        const riskBar = document.getElementById('overall-risk-score-bar');
        riskBar.style.width = `${riskScore}%`;
        riskBar.className = `progress-bar ${this.getRiskBarColorClass(riskScore)}`;

        // 4. KEY INDICATORS
        const keyIndicators = result.key_indicators || {};
        document.getElementById('indicator-mood').textContent = keyIndicators.mood_tone || 'Stable';
        document.getElementById('indicator-cognitive').textContent = keyIndicators.cognitive_clues || 'Positive thinking';
        document.getElementById('indicator-social').textContent = keyIndicators.social_cues || 'Connected & active';

        // 5. AI COPING SUGGESTIONS
        const suggestionsUl = document.getElementById('suggestions-list');
        suggestionsUl.innerHTML = '';
        const suggestions = result.coping_suggestions || result.suggestions || [];
        if (suggestions.length === 0) {
            suggestionsUl.innerHTML = '<li class="list-group-item small text-muted">No specific suggestions available.</li>';
        } else {
            suggestions.forEach((s) => {
                const li = document.createElement('li');
                li.className = 'list-group-item small';
                li.textContent = s;
                suggestionsUl.appendChild(li);
            });
        }

        // 6. AI WELLNESS TIP
        const wellnessTip = result.wellness_tip || result.ai_tip || 'Keep checking in with yourself. Small steps matter.';
        document.getElementById('aiTipText').textContent = wellnessTip;

        // 7. WHY THIS RESULT? (TEXT)
        const textExplain = result.text_explain || {};
        const hasText = textExplain.has_text !== false; // Default to true if not specified
        const textSummary = textExplain.summary || (hasText ? 'Text analysis completed.' : 'No text was analyzed for this prediction.');
        const textKeywords = textExplain.keywords || [];
        const textTone = textExplain.tone || 'N/A';
        
        document.getElementById('text-explanation-summary').textContent = textSummary;
        const textTokensContainer = document.getElementById('text-explanation-tokens');
        textTokensContainer.innerHTML = '';
        if (textKeywords.length > 0) {
            textKeywords.forEach(keyword => {
                const span = document.createElement('span');
                span.className = 'badge bg-primary me-1';
                span.textContent = keyword;
                textTokensContainer.appendChild(span);
            });
        } else if (hasText) {
            textTokensContainer.innerHTML = '<span class="text-muted small">No specific keywords detected.</span>';
        }
        document.getElementById('text-tone').textContent = textTone;

        // 8. WHY THIS RESULT? (IMAGE)
        const imageExplain = result.image_explain || {};
        const hasImage = imageExplain.has_image !== false; // Default to true if not specified
        const imageSummary = imageExplain.summary || (hasImage ? 'Image analysis completed.' : 'No image was analyzed for this prediction.');
        const imageEmotion = imageExplain.emotion_from_face || (hasImage ? 'N/A' : null);
        const imageHint = imageExplain.cam_hint || '';
        
        document.getElementById('image-explanation-text').textContent = imageSummary + (imageHint ? ` ${imageHint}` : '');
        
        // Update image preview if available
        if (this.lastImageData) {
            const originalImg = document.getElementById('original-image-preview');
            originalImg.src = `data:image/png;base64,${this.lastImageData}`;
            originalImg.style.display = 'block';
        }

        container.scrollIntoView({ behavior: 'smooth' });
    }

    getStressCategoryDescription(category) {
        const descriptions = {
            'No Apparent Stress': 'Minimal indicators of emotional strain detected.',
            'Low Stress': 'Some mild indicators of stress are present.',
            'Moderate Stress': 'Some indicators of emotional strain are present.',
            'High Stress': 'Multiple indicators of significant stress detected.',
            'Severe Stress': 'Severe indicators of stress require attention.'
        };
        return descriptions[category] || 'Stress level has been assessed.';
    }

    getStressCategoryColorClass(category) {
        if (category.includes('Severe') || category.includes('High')) return 'text-danger';
        if (category.includes('Moderate')) return 'text-warning';
        if (category.includes('Low')) return 'text-info';
        return 'text-success';
    }

    getRiskLevelFromScore(score) {
        if (score <= 30) return 'Low Risk';
        if (score <= 60) return 'Moderate Risk';
        if (score <= 85) return 'High Risk';
        return 'Critical Risk';
    }

    getRiskScoreColorClass(score) {
        if (score <= 30) return 'text-success';
        if (score <= 60) return 'text-warning';
        if (score <= 85) return 'text-danger';
        return 'text-danger';
    }

    getRiskBarColorClass(score) {
        if (score <= 30) return 'bg-success';
        if (score <= 60) return 'bg-warning';
        if (score <= 85) return 'bg-danger';
        return 'bg-danger';
    }

    normalizeStressCategory(raw = '') {
        const value = (raw || '').toString().toLowerCase();
        if (value.includes('severe') || value.includes('critical') || value.includes('high')) {
            return 'High Stress';
        }
        if (value.includes('moderate')) {
            return 'Moderate Stress';
        }
        return 'Low Stress';
    }

    getEmotionalTone(emotion = '') {
        const value = emotion.toLowerCase();
        const positive = ['happy', 'joy', 'calm', 'peaceful', 'neutral'];
        const negative = ['sad', 'anger', 'angry', 'fear', 'stressed', 'anxious', 'depressed'];
        if (positive.some((term) => value.includes(term))) return 'Positive';
        if (negative.some((term) => value.includes(term))) return 'Negative';
        return 'Neutral';
    }

    getRiskBarClass(category) {
        if (category === 'High Stress') return 'risk-high';
        if (category === 'Moderate Stress') return 'risk-moderate';
        return 'risk-low';
    }

    getSleepIndicator(category) {
        if (category === 'High Stress') return 'Irregular / restless';
        if (category === 'Moderate Stress') return 'Light disturbances';
        return 'Stable / restorative';
    }

    getMoodIndicator(tone, category) {
        if (category === 'High Stress' || tone === 'Negative') return 'Emotional strain detected';
        if (category === 'Moderate Stress' || tone === 'Neutral') return 'Balanced but cautious';
        return 'Grounded and optimistic';
    }

    getSocialIndicator(category) {
        if (category === 'High Stress') return 'Likely withdrawn';
        if (category === 'Moderate Stress') return 'Selectively connected';
        return 'Engaged & supported';
    }

    async loadTextExplanation() {
        if (!this.lastText) return;
        try {
            const res = await fetch(`${this.apiBase}/api/explain/text`, {
                method: 'POST',
                headers: this.authHeaders,
                body: JSON.stringify({ text: this.lastText }),
            });
            const data = await res.json();
            if (!res.ok) return;

            const summaryEl = document.getElementById('text-explanation-summary');
            const tokensContainer = document.getElementById('text-explanation-tokens');
            if (!summaryEl || !tokensContainer) return;

            summaryEl.textContent = data.summary || 'Important words highlighted below.';
            tokensContainer.innerHTML = '';

            (data.tokens || []).forEach((tok) => {
                const span = document.createElement('span');
                const score = Math.abs(tok.importance || tok.score || 0);
                let cls = 'token-importance-low';
                if (score > 0.6) cls = 'token-importance-high';
                else if (score > 0.3) cls = 'token-importance-medium';
                span.className = cls;
                span.textContent = `${tok.token} `;
                tokensContainer.appendChild(span);
            });
        } catch (_) {
            // ignore explanation failures
        }
    }

    updateOriginalImagePreview(dataUrl) {
        const img = document.getElementById('original-image-preview');
        if (!img) return;
        const src = dataUrl || (this.lastImageData ? `data:image/png;base64,${this.lastImageData}` : null);
        if (!src) return;
        img.src = src;
        img.style.display = 'block';
    }

    async loadImageExplanation() {
        if (!this.lastImageData) return;
        try {
            const res = await fetch(`${this.apiBase}/api/explain/image`, {
                method: 'POST',
                headers: this.authHeaders,
                body: JSON.stringify({ image_base64: this.lastImageData }),
            });
            const data = await res.json();
            if (!res.ok) return;
            if (!data.overlay_base64) return;
            const img = document.getElementById('image-heatmap');
            if (!img) return;
            img.src = `data:image/png;base64,${data.overlay_base64}`;
            img.style.display = 'block';
        } catch (_) {
            // ignore explanation failures
        }
    }

    resetTextAnalysis() {
        const textarea = document.getElementById('textInput');
        if (textarea) textarea.value = '';
    }

    resetImageAnalysis() {
        this.removeImage();
    }

    clearResults() {
        const container = document.getElementById('analysisResults');
        if (container) container.style.display = 'none';
    }

    // ---------------- Dashboard & Timeline ---------------- //
    async loadDashboard(skipCharts = false) {
        try {
            const histRes = await fetch(`${this.apiBase}/api/analyze/history`, {
                headers: this.authHeaders,
            });
            const histData = await histRes.json();
            this.timeline = histData.analyses || [];
            this.updateDashboardStats();
            if (!skipCharts) {
                this.createEmotionChart();
                this.createStressChart();
            }
            if (this.currentUser && this.currentUser.role === 'admin') {
                await this.loadAdminPanel();
            }
        } catch (_) {
            // ignore for now
        }
    }

    updateDashboardStats() {
        document.getElementById('total-analyses').textContent = this.timeline.length;
        if (this.timeline.length === 0) return;
        const latest = this.timeline[0]; // most recent (history is desc)
        document.getElementById('current-mood').textContent = latest.emoji || '😊';
        document.getElementById('stress-level').textContent = latest.stress_level;
        document.getElementById('risk-level').textContent = latest.risk_level;
    }

    createEmotionChart() {
        const ctx = document.getElementById('emotionChart');
        if (!ctx) return;
        if (this.charts.emotion) this.charts.emotion.destroy();
        const counts = {};
        this.timeline.forEach(r => {
            counts[r.emotion] = (counts[r.emotion] || 0) + 1;
        });
        this.charts.emotion = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(counts),
                datasets: [{
                    data: Object.values(counts),
                    backgroundColor: ['#22c55e','#3b82f6','#f97316','#ef4444','#a855f7'],
                }],
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
        });
    }

    createStressChart() {
        const ctx = document.getElementById('stressChart');
        if (!ctx) return;
        if (this.charts.stress) this.charts.stress.destroy();
        const counts = {};
        this.timeline.forEach(r => {
            counts[r.stress_level] = (counts[r.stress_level] || 0) + 1;
        });
        this.charts.stress = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(counts),
                datasets: [{
                    label: 'Stress levels',
                    data: Object.values(counts),
                    backgroundColor: ['#22c55e','#eab308','#f97316','#ef4444'],
                }],
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } },
        });
    }

    async loadTimeline() {
        try {
            const [timelineRes, behRes] = await Promise.all([
                fetch(`${this.apiBase}/api/user/timeline`, { headers: this.authHeaders }),
                fetch(`${this.apiBase}/api/user/behavioral`, { headers: this.authHeaders }),
            ]);
            const timelineData = await timelineRes.json();
            const behavioralData = await behRes.json();
            this.timelinePoints = timelineData.timeline || [];
            this.behavioral = behavioralData;
            this.createTimelineChart();
            this.createEmojiChart();
            this.createFrequencyChart();
            this.updateBehavioralFingerprint();
        } catch (_) {
            // ignore
        }
    }

    createTimelineChart() {
        const ctx = document.getElementById('timelineChart');
        if (!ctx) return;
        if (this.charts.timeline) this.charts.timeline.destroy();
        const labels = this.timelinePoints.map(p => p.timestamp);
        const values = this.timelinePoints.map(p => p.stress_score);
        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Stress score',
                    data: values,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59,130,246,0.15)',
                    fill: true,
                    tension: 0.4,
                }],
            },
            options: { responsive: true, scales: { y: { beginAtZero: true, max: 1 } } },
        });
    }

    createEmojiChart() {
        const ctx = document.getElementById('emojiChart');
        if (!ctx) return;
        if (!this.behavioral) return;
        if (this.charts.emoji) this.charts.emoji.destroy();
        const emoji_fp = this.behavioral.emoji_fingerprint || {};
        const labels = Object.keys(emoji_fp);
        const data = Object.values(emoji_fp);
        this.charts.emoji = new Chart(ctx, {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: ['#22c55e','#3b82f6','#eab308','#f97316','#ef4444'],
                }],
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
        });
    }

    createFrequencyChart() {
        const ctx = document.getElementById('frequencyChart');
        if (!ctx) return;
        if (!this.behavioral) return;
        if (this.charts.frequency) this.charts.frequency.destroy();
        const totalSessions = this.behavioral.total_sessions || 0;
        const weeks = 4;
        const perWeek = totalSessions / weeks;
        this.charts.frequency = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Avg / week'],
                datasets: [{
                    label: 'Sessions',
                    data: [perWeek],
                    backgroundColor: '#06b6d4',
                }],
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } },
        });
        const freqScore = Math.min(perWeek / 7, 1); // heuristic
        document.getElementById('frequencyProgress').style.width = `${freqScore * 100}%`;
        document.getElementById('frequencyScore').textContent = perWeek.toFixed(1);
    }

    updateBehavioralFingerprint() {
        const container = document.getElementById('behavioralFingerprint');
        if (!container || !this.behavioral) return;
        const profile = this.behavioral.behavioral_profile || {};
        const avgConf = profile.average_confidence || 0;
        const total = this.behavioral.total_sessions || 0;
        container.innerHTML = `
            <p class="mb-1"><strong>Total check-ins:</strong> ${total}</p>
            <p class="mb-1"><strong>Average model confidence:</strong> ${(avgConf * 100).toFixed(1)}%</p>
            <p class="mb-0 text-muted">Your emoji fingerprint summarizes how often each mood appears across your sessions.</p>
        `;
    }

    // ---------------- Reports & data ---------------- //
    async loadReports() {
        // Nothing dynamic to preload right now
    }

    async downloadPdfReport() {
        try {
            const res = await fetch(`${this.apiBase}/api/reports/pdf`, {
                method: 'POST',
                headers: this.authHeaders,
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                this.showAlert(err.error || 'Failed to generate report', 'danger');
                return;
            }
            const blob = await res.blob();
                this.downloadBlob(blob, `mindscope_report_${new Date().toISOString().split('T')[0]}.pdf`);
        } catch (_) {
            this.showAlert('Failed to generate report', 'danger');
        }
    }

    async exportDataZip() {
        try {
            const res = await fetch(`${this.apiBase}/api/reports/export`, {
                method: 'POST',
                headers: this.authHeaders,
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                this.showAlert(err.error || 'Failed to export data', 'danger');
                return;
            }
            const blob = await res.blob();
            this.downloadBlob(blob, `mindscope_export_${new Date().toISOString().split('T')[0]}.zip`);
        } catch (_) {
            this.showAlert('Failed to export data', 'danger');
        }
    }

    async deleteMyData() {
        if (!confirm('Delete all your analyses and behavioral data? This cannot be undone.')) {
            return;
        }
        try {
            const res = await fetch(`${this.apiBase}/api/user/data`, {
                method: 'DELETE',
                headers: this.authHeaders,
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAlert(data.error || 'Failed to delete data', 'danger');
                return;
            }
            this.showAlert('Your data has been cleared from this device and server account.', 'success');
            await this.loadDashboard();
        } catch (_) {
            this.showAlert('Failed to delete data', 'danger');
        }
    }

    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    // ---------------- Admin panel ---------------- //
    async loadAdminPanel() {
        if (!this.currentUser || this.currentUser.role !== 'admin') return;
        try {
            const [usersRes, analyticsRes, metricsRes] = await Promise.all([
                fetch(`${this.apiBase}/api/admin/users`, { headers: this.authHeaders }),
                fetch(`${this.apiBase}/api/admin/analytics`, { headers: this.authHeaders }),
                fetch(`${this.apiBase}/api/admin/metrics`, { headers: this.authHeaders }),
            ]);
            const usersData = await usersRes.json();
            const analytics = await analyticsRes.json();
            const metricsData = await metricsRes.json();
            if (!usersRes.ok || !analyticsRes.ok) return;
            this.updateAdminUsers(usersData.users || []);
            this.updateAdminAnalytics(analytics);
            this.updateAdminMetrics(metricsData.metrics);
        } catch (_) {
            // ignore
        }
    }

    updateAdminMetrics(metrics) {
        const container = document.getElementById('model-metrics-card-body');
        if (!container) return;
        if (!metrics || metrics.message) {
            container.innerHTML = `<p class="text-muted">${metrics?.message || 'No evaluation metrics found. Run backend/evaluate_models.py first.'}</p>`;
        } else {
            container.innerHTML = `
                <p class="mb-1"><strong>Accuracy:</strong> ${(metrics.accuracy * 100).toFixed(2)}%</p>
                <p class="mb-1"><strong>F1-Score:</strong> ${(metrics.f1 * 100).toFixed(2)}%</p>
                <p class="mb-1"><strong>Precision:</strong> ${(metrics.precision * 100).toFixed(2)}%</p>
                <p class="mb-1"><strong>Recall:</strong> ${(metrics.recall * 100).toFixed(2)}%</p>
                <small class="text-muted">Last evaluated: ${new Date(metrics.timestamp).toLocaleString()}</small>
            `;
        }
    }

    updateAdminUsers(users) {
        const userList = document.getElementById('userList');
        const select = document.getElementById('supportUserSelect');
        if (!userList || !select) return;
        userList.innerHTML = '';
        select.innerHTML = '';
        users.forEach(u => {
            const item = document.createElement('div');
            item.className = 'list-group-item d-flex justify-content-between align-items-center';
            item.innerHTML = `
                    <div>
                    <strong>${u.username}</strong><br>
                    <small class="text-muted">${u.email}</small>
                    </div>
                <span class="badge bg-${u.role === 'admin' ? 'primary' : 'success'}">${u.role}</span>
            `;
            userList.appendChild(item);

            const opt = document.createElement('option');
            opt.value = u.id;
            opt.textContent = `${u.username} (${u.email})`;
            select.appendChild(opt);
        });
    }

    updateAdminAnalytics(data) {
        document.getElementById('total-users').textContent = data.total_users || 0;
        document.getElementById('high-risk-cases').textContent =
            (data.alerts || []).filter(a => a.severity === 'high' || a.severity === 'critical').length;
        document.getElementById('crisis-cases').textContent =
            (data.alerts || []).filter(a => a.severity === 'critical').length;

        const riskMonitoring = document.getElementById('riskMonitoring');
        if (!riskMonitoring) return;
        if ((data.alerts || []).length === 0) {
            riskMonitoring.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="bi bi-check-circle me-2"></i>All Clear</h6>
                    <p>No high-stress alerts triggered yet.</p>
                </div>`;
        } else {
            const critical = data.alerts.filter(a => a.severity === 'critical').length;
            riskMonitoring.innerHTML = `
                <div class="alert alert-warning">
                    <h6><i class="bi bi-exclamation-triangle me-2"></i>High Stress Alerts</h6>
                    <p>Total alerts: ${data.alerts.length}, critical: ${critical}</p>
                </div>`;
        }

        const systemCtx = document.getElementById('systemChart');
        if (systemCtx) {
            if (this.charts.system) this.charts.system.destroy();
            const sd = data.stress_distribution || {};
            this.charts.system = new Chart(systemCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(sd),
                    datasets: [{
                        label: 'Stress level counts',
                        data: Object.values(sd),
                        backgroundColor: ['#22c55e','#eab308','#f97316','#ef4444'],
                    }],
                },
                options: { responsive: true, scales: { y: { beginAtZero: true } } },
            });
        }

        const adminCtx = document.getElementById('adminChart');
        if (adminCtx) {
            if (this.charts.admin) this.charts.admin.destroy();
            const ed = data.emotion_distribution || {};
            this.charts.admin = new Chart(adminCtx, {
                type: 'pie',
                data: {
                    labels: Object.keys(ed),
                    datasets: [{
                        data: Object.values(ed),
                        backgroundColor: ['#22c55e','#3b82f6','#eab308','#f97316','#ef4444'],
                    }],
                },
                options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
            });
        }

        const highRiskList = document.getElementById('high-risk-list');
        if (highRiskList) {
            const criticalAlerts = (data.alerts || []).filter(a => a.severity === 'critical');
            if (criticalAlerts.length === 0) {
                highRiskList.innerHTML = '<p class="text-muted">No high-risk cases detected</p>';
            } else {
                highRiskList.innerHTML = criticalAlerts.map(a =>
                    `<div class="d-flex justify-content-between align-items-center mb-2">
                        <span><span class="risk-indicator risk-critical"></span>User #${a.user_id}</span>
                        <small>${a.stress_count} high-stress events</small>
                    </div>`
                ).join('');
            }
        }
    }

    async sendSupportMessage() {
        const select = document.getElementById('supportUserSelect');
        const titleEl = document.getElementById('messageTitle');
        const msgEl = document.getElementById('supportMessage');
        if (!msgEl.value.trim()) {
            this.showAlert('Please write a message.', 'warning');
            return;
        }
        try {
            const payload = {
                title: titleEl?.value.trim() || 'Support Message',
                body: msgEl.value.trim(),
            };
            if (select.value) {
                payload.receiver_id = Number(select.value);
                payload.is_broadcast = false;
            } else {
                payload.is_broadcast = true;
            }
            const res = await fetch(`${this.apiBase}/api/admin/messages`, {
                method: 'POST',
                headers: this.authHeaders,
                body: JSON.stringify(payload),
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAlert(data.error || 'Failed to send message', 'danger');
                return;
            }
            this.showAlert(data.message || 'Message sent successfully.', 'success');
            if (msgEl) msgEl.value = '';
            if (titleEl) titleEl.value = '';
        } catch (_) {
            this.showAlert('Failed to send message', 'danger');
        }
    }

    async loadMessages() {
        try {
            const res = await fetch(`${this.apiBase}/api/user/messages`, {
                headers: this.authHeaders,
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAlert(data.error || 'Failed to load messages', 'danger');
                return;
            }
            this.displayMessages(data.messages || []);
        } catch (_) {
            this.showAlert('Failed to load messages', 'danger');
        }
    }

    displayMessages(messages) {
        const container = document.getElementById('messagesList');
        if (!container) return;
        if (messages.length === 0) {
            container.innerHTML = '<p class="text-muted">No messages yet.</p>';
            return;
        }
        container.innerHTML = messages.map(m => `
            <div class="card mb-3 ${m.is_read ? '' : 'border-primary'}" data-message-id="${m.id}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title">${m.title || 'Message'}</h6>
                            <p class="card-text">${m.body}</p>
                            <small class="text-muted">From: ${m.sender} • ${new Date(m.created_at).toLocaleString()}</small>
                            ${m.is_broadcast ? '<span class="badge bg-info ms-2">Broadcast</span>' : ''}
                        </div>
                        ${!m.is_read ? '<button class="btn btn-sm btn-outline-primary" onclick="app.markMessageRead(${m.id})">Mark Read</button>' : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    async markMessageRead(messageId) {
        try {
            const res = await fetch(`${this.apiBase}/api/user/messages/read`, {
                method: 'POST',
                headers: this.authHeaders,
                body: JSON.stringify({ message_ids: [messageId] }),
            });
            if (res.ok) {
                await this.loadMessages();
            }
        } catch (_) {
            // ignore
        }
    }

    // ---------------- Utils ---------------- //
    showAlert(message, type = 'info') {
        const div = document.createElement('div');
        div.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        div.style.top = '1rem';
        div.style.right = '1rem';
        div.style.zIndex = 2000;
        div.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(div);
        setTimeout(() => div.remove(), 5000);
    }

    toggleTheme() {
        const html = document.documentElement;
    const body = document.body;
        const icon = document.getElementById('theme-icon');
        const currentTheme = html.getAttribute('data-theme') || localStorage.getItem('mindscope_theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        html.setAttribute('data-theme', newTheme);
        body.setAttribute('data-theme', newTheme);
        body.classList.toggle('dark-theme', newTheme === 'dark');
        
        if (icon) icon.className = newTheme === 'dark' ? 'bi bi-moon' : 'bi bi-sun';
        localStorage.setItem('mindscope_theme', newTheme);
    }
}

// Global helpers for inline HTML handlers
const app = new MindScopeApp();

function login() { app.login(); }
function logout() { app.logout(); }
function showSection(sectionName) { app.showSection(sectionName); }
function removeImage() { app.removeImage(); }
function resetTextAnalysis() { app.resetTextAnalysis(); }
function resetImageAnalysis() { app.resetImageAnalysis(); }
function clearResults() { app.clearResults(); }
function toggleTheme() { app.toggleTheme(); }
function showSignupModal() {
    const modal = new bootstrap.Modal(document.getElementById('signupModal'));
    modal.show();
}
function signup() { app.signup(); }
function downloadPdfReport() { app.downloadPdfReport(); }
function exportDataZip() { app.exportDataZip(); }
function deleteMyData() { app.deleteMyData(); }
function startWebcam() { app.startWebcam(); }
function captureWebcam() { app.captureWebcam(); }
function stopWebcam() { app.stopWebcam(); }
function markMessageRead(id) { app.markMessageRead(id); }
