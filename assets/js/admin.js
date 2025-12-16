// MindScope AI Admin Dashboard JavaScript

let emotionChart = null;
let loginChart = null;
let stressChart = null;
let authToken = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Admin Dashboard v2.0 - New Features Loaded!');
    restoreSession();
    setupEventListeners();
    
    // Hide all sections first
    document.querySelectorAll('.admin-section').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show dashboard by default
    const dashboard = document.getElementById('admin-dashboard');
    if (dashboard) {
        dashboard.style.display = 'block';
    }
    
    // Load dashboard data
    loadDashboard();
    
    // Show feature availability
    const features = {
        emotionChart: !!document.getElementById('emotionChart'),
        loginChart: !!document.getElementById('loginChart'),
        broadcastForm: !!document.getElementById('broadcast-form'),
        modelVersionInfo: !!document.getElementById('model-version-info'),
        resourcesList: !!document.getElementById('resources-list'),
        logsTable: !!document.getElementById('logs-table-body'),
        statusColumn: Array.from(document.querySelectorAll('th')).some(th => th.textContent.includes('Status'))
    };
    console.log('✅ Features detected:', features);
});

function restoreSession() {
    const saved = localStorage.getItem('mindscope_session');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            authToken = parsed.token;
        } catch (e) {
            console.error('Failed to restore session:', e);
        }
    }
}

function getAuthHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    return headers;
}

function setupEventListeners() {
    // Broadcast form
    const broadcastForm = document.getElementById('broadcast-form');
    if (broadcastForm) {
        broadcastForm.addEventListener('submit', handleBroadcast);
    }
    
    // Resource form
    const resourceForm = document.getElementById('new-resource-form');
    if (resourceForm) {
        resourceForm.addEventListener('submit', handleResourceSubmit);
    }
}

function showAdminSection(section, evt) {
    // Hide all sections
    document.querySelectorAll('.admin-section').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show selected section
    const target = document.getElementById(`admin-${section}`);
    if (target) {
        target.style.display = 'block';
    }
    
    // Update nav active state
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Find and activate the clicked link
    const event = evt || window.event;
    if (event) {
        const clickedLink = event.target.closest('.nav-link');
        if (clickedLink) {
            clickedLink.classList.add('active');
        }
    } else {
        // Fallback: find link by section
        const sectionLink = Array.from(document.querySelectorAll('.nav-link')).find(link => {
            const onclick = link.getAttribute('onclick') || '';
            return onclick.includes(`'${section}'`);
        });
        if (sectionLink) {
            sectionLink.classList.add('active');
        }
    }
    
    // Load section-specific data
    if (section === 'dashboard') {
        loadDashboard();
    } else if (section === 'users') {
        loadUsers();
    } else if (section === 'analyses') {
        loadAnalyses();
    } else if (section === 'models') {
        loadModelManagement();
    } else if (section === 'notifications') {
        loadNotifications();
    } else if (section === 'resources') {
        loadResources();
    } else if (section === 'logs') {
        loadAuditLogs();
    }
}

// Make function globally accessible
window.showAdminSection = showAdminSection;

// ========================================================================
// DASHBOARD
// ========================================================================

async function loadDashboard() {
    await Promise.all([
        loadEmotionStats(),
        loadLoginStats(),
        loadAnalytics()
    ]);
}

function refreshDashboard() {
    loadDashboard();
}

async function loadEmotionStats() {
    try {
        const res = await fetch('/api/admin/emotion-stats?days=7&limit=500', {
            headers: getAuthHeaders()
        });
        
        if (!res.ok) {
            console.warn('Emotion stats endpoint returned:', res.status);
            return;
        }
        
        const contentType = res.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.warn('Emotion stats endpoint returned non-JSON response');
            return;
        }
        
        const data = await res.json();
        
        if (data.emotion_counts && Object.keys(data.emotion_counts).length > 0) {
            renderEmotionChart(data.emotion_counts);
        } else {
            // Show empty state
            const ctx = document.getElementById('emotionChart');
            if (ctx) {
                const parent = ctx.closest('.card-body');
                if (parent) {
                    const existing = parent.querySelector('.no-data-message');
                    if (!existing) {
                        const msg = document.createElement('p');
                        msg.className = 'text-muted text-center no-data-message';
                        msg.textContent = 'No emotion data available yet';
                        parent.appendChild(msg);
                    }
                }
            }
        }
    } catch (e) {
        console.error('Failed to load emotion stats:', e);
    }
}

function renderEmotionChart(emotionCounts) {
    const ctx = document.getElementById('emotionChart');
    if (!ctx) return;
    
    const labels = Object.keys(emotionCounts);
    const counts = Object.values(emotionCounts);
    
    if (emotionChart) {
        emotionChart.destroy();
    }
    
    // Color mapping for emotions
    const emotionColors = {
        'Happy': '#10b981',
        'Sad': '#3b82f6',
        'Anxious': '#f59e0b',
        'Angry': '#ef4444',
        'Fearful': '#8b5cf6',
        'Neutral': '#06b6d4',
        'Surprised': '#fbbf24',
        'Disgusted': '#ec4899',
    };
    
    const backgroundColor = labels.map(l => emotionColors[l] || '#6b7280');
    const textColor = getComputedStyle(document.body).getPropertyValue('--text-admin') || '#fff';
    
    emotionChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: backgroundColor,
                borderWidth: 2,
                borderColor: 'rgba(0, 0, 0, 0.1)',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: textColor,
                        padding: 15,
                        font: { size: 12, weight: '500' },
                        usePointStyle: true,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

async function loadLoginStats() {
    try {
        const res = await fetch('/api/admin/login-stats?days=7', {
            headers: getAuthHeaders()
        });
        
        if (!res.ok) {
            console.warn('Login stats endpoint returned:', res.status, res.statusText);
            return;
        }
        
        const contentType = res.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.warn('Login stats endpoint returned non-JSON response');
            return;
        }
        
        const data = await res.json();
        
        if (data.daily_logins && data.daily_logins.length > 0) {
            renderLoginChart(data.daily_logins);
        } else {
            // Show empty state
            const ctx = document.getElementById('loginChart');
            if (ctx) {
                const parent = ctx.closest('.card-body');
                if (parent) {
                    const existing = parent.querySelector('.no-data-message');
                    if (!existing) {
                        const msg = document.createElement('p');
                        msg.className = 'text-muted text-center no-data-message';
                        msg.textContent = 'No login data available yet';
                        parent.appendChild(msg);
                    }
                }
            }
        }
    } catch (e) {
        console.error('Failed to load login stats:', e);
    }
}

function renderLoginChart(dailyLogins) {
    const ctx = document.getElementById('loginChart');
    if (!ctx) return;
    
    const labels = dailyLogins.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const counts = dailyLogins.map(d => d.count);
    
    if (loginChart) {
        loginChart.destroy();
    }
    
    const textColor = getComputedStyle(document.body).getPropertyValue('--text-admin') || '#fff';
    const gridColor = 'rgba(255,255,255,0.1)';
    
    loginChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'User Logins',
                data: counts,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true,
                borderWidth: 3,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: textColor,
                        font: { size: 12, weight: '500' },
                        usePointStyle: true,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { 
                        color: textColor,
                        stepSize: 1,
                        precision: 0
                    },
                    grid: { 
                        color: gridColor,
                        drawBorder: false
                    }
                },
                x: {
                    ticks: { 
                        color: textColor,
                        font: { weight: '500' }
                    },
                    grid: { 
                        display: false
                    }
                }
            }
        }
    });
}

let analysesOffset = 0;
const analysesLimit = 50;

async function loadAnalytics() {
    try {
        const res = await fetch('/api/admin/analytics', {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        // Update stats (users only, no admin count)
        const totalUsersEl = document.getElementById('stat-total-users');
        if (totalUsersEl) totalUsersEl.textContent = data.total_users || 0;
        
        const totalAnalysesEl = document.getElementById('stat-total-analyses');
        if (totalAnalysesEl) totalAnalysesEl.textContent = data.total_analyses || 0;
        
        // Count high-risk users
        const highRiskEl = document.getElementById('stat-high-risk');
        if (highRiskEl) {
            const highRiskCount = data.users ? data.users.filter(u => u.high_risk_flag).length : 0;
            highRiskEl.textContent = highRiskCount;
        }
        
        // Render stress chart if exists
        if (data.stress_distribution) {
            renderStressChart(data.stress_distribution);
        }
        
        // Load recent analyses
        if (data.recent_predictions && data.recent_predictions.length > 0) {
            renderRecentAnalyses(data.recent_predictions);
        }
    } catch (e) {
        console.error('Failed to load analytics:', e);
    }
}

function renderRecentAnalyses(analyses) {
    const tbody = document.getElementById('recent-analyses-table-body');
    if (!tbody) return;
    
    if (analyses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-5"><span class="text-muted" style="font-size: 1.1rem; font-weight: 500;">No analyses yet</span></td></tr>';
        return;
    }
    
    tbody.innerHTML = analyses.slice(0, 10).map(a => `
        <tr>
            <td style="font-weight: 500; font-size: 1rem;">${new Date(a.timestamp).toLocaleString()}</td>
            <td><span class="badge bg-info" style="font-size: 0.9rem; font-weight: 600;">${a.emotion || 'N/A'}</span></td>
            <td><span class="badge ${getStressBadgeClass(a.stress_level)}" style="font-size: 0.9rem; font-weight: 600;">${a.stress_level || 'N/A'}</span></td>
            <td><span class="badge ${getRiskBadgeClass(a.risk_level)}" style="font-size: 0.9rem; font-weight: 600;">${a.risk_level || 'N/A'}</span></td>
            <td><span class="badge bg-secondary" style="font-size: 0.9rem; font-weight: 600;">${a.mode || 'N/A'}</span></td>
        </tr>
    `).join('');
}

function getStressBadgeClass(stress) {
    if (!stress) return 'bg-secondary';
    const s = stress.toLowerCase();
    if (s.includes('high') || s.includes('critical')) return 'bg-danger';
    if (s.includes('moderate')) return 'bg-warning';
    return 'bg-success';
}

function getRiskBadgeClass(risk) {
    if (!risk) return 'bg-secondary';
    const r = risk.toLowerCase();
    if (r.includes('high') || r.includes('critical')) return 'bg-danger';
    if (r.includes('moderate')) return 'bg-warning';
    return 'bg-success';
}

function renderStressChart(stressDist) {
    const ctx = document.getElementById('stressChart');
    if (!ctx) return;
    
    if (stressChart) {
        stressChart.destroy();
    }
    
    const labels = Object.keys(stressDist).map(k => k.charAt(0).toUpperCase() + k.slice(1));
    const values = Object.values(stressDist);
    const colors = ['#10b981', '#f59e0b', '#ef4444', '#dc2626'];
    const textColor = getComputedStyle(document.body).getPropertyValue('--text-admin') || '#fff';
    const gridColor = 'rgba(255,255,255,0.1)';
    
    stressChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'User Analyses',
                data: values,
                backgroundColor: labels.map((_, i) => colors[i % colors.length]),
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { 
                        color: textColor,
                        stepSize: 1,
                        precision: 0
                    },
                    grid: { 
                        color: gridColor,
                        drawBorder: false
                    }
                },
                x: {
                    ticks: { 
                        color: textColor,
                        font: { weight: '500' }
                    },
                    grid: { 
                        display: false
                    }
                }
            }
        }
    });
}

// ========================================================================
// USERS
// ========================================================================

async function loadUsers() {
    try {
        const res = await fetch('/api/admin/users', {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        renderUsersTable(data.users || []);
    } catch (e) {
        console.error('Failed to load users:', e);
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-5"><span class="text-muted" style="font-size: 1.1rem; font-weight: 500;">No users found</span></td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td style="font-weight: 600; font-size: 1rem;">
                <div class="d-flex align-items-center">
                    <i class="bi bi-person-circle me-2 fs-5"></i>
                    <div>
                        <strong style="font-size: 1.05rem;">${user.full_name || user.username}</strong>
                        <br><small class="text-muted" style="font-size: 0.9rem; font-weight: 500;">ID: ${user.hashed_id || user.id}</small>
                    </div>
                </div>
            </td>
            <td style="font-weight: 500; font-size: 1rem;">${user.email}</td>
            <td>
                ${user.high_risk_flag ? 
                    '<span class="badge bg-danger" style="font-size: 0.9rem; font-weight: 600;"><i class="bi bi-exclamation-triangle-fill me-1"></i>Needs Attention</span>' : 
                    '<span class="badge bg-success" style="font-size: 0.9rem; font-weight: 600;"><i class="bi bi-check-circle-fill me-1"></i>OK</span>'
                }
            </td>
            <td>
                ${user.high_risk_flag ? 
                    `<div class="alert alert-danger mb-0 py-2 px-3" style="font-size: 0.9rem; font-weight: 600; border-radius: 0.5rem; max-width: 300px;">
                        <i class="bi bi-exclamation-triangle-fill me-1"></i>
                        <strong>⚠️ High Risk Alert!</strong><br>
                        <small style="font-size: 0.85rem; font-weight: 500;">${user.high_risk_reason || 'Repeated high stress detected'}</small>
                    </div>` : 
                    '<span class="text-muted" style="font-size: 0.9rem;">No alerts</span>'
                }
            </td>
            <td style="font-weight: 500; font-size: 1rem;">
                ${user.last_login_at ? 
                    `<span style="font-weight: 600;"><i class="bi bi-circle-fill me-1" style="font-size: 0.5rem;"></i>${new Date(user.last_login_at).toLocaleDateString()}</span><br><small class="text-muted" style="font-size: 0.9rem;">${new Date(user.last_login_at).toLocaleTimeString()}</small>` : 
                    '<span class="text-muted" style="font-weight: 500;">Never</span>'
                }
            </td>
            <td><span class="badge bg-info" style="font-size: 0.95rem; font-weight: 600;">${user.total_sessions || 0}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-info me-1" onclick="viewUserDetails('${user.hashed_id || user.id}')" title="View Details">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-primary" onclick="downloadUserReport('${user.id || user.hashed_id}')" title="Download Report">
                    <i class="bi bi-download"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function viewUserDetails(userId) {
    // TODO: Implement user detail modal
    alert('User details for: ' + userId);
}

async function downloadUserReport(userId) {
    try {
        // Get user analyses first
        const res = await fetch(`/api/admin/users/${userId}/analyses`, {
            headers: getAuthHeaders()
        });
        
        if (!res.ok) {
            alert('Failed to fetch user analyses');
            return;
        }
        
        const data = await res.json();
        
        // Create report data
        const reportData = {
            user_id: userId,
            analyses: data.analyses || [],
            generated_at: new Date().toISOString()
        };
        
        // Download as JSON
        const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `user_report_${userId}_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        alert('✅ Report downloaded successfully!');
    } catch (e) {
        console.error('Report download error:', e);
        alert('❌ Failed to download report');
    }
}

function trainModel(modelType) {
    if (!confirm(`Start training ${modelType} model? This may take a few minutes.`)) {
        return;
    }
    
    alert(`Training ${modelType} model... This feature requires backend training endpoint.`);
    // TODO: Implement actual training endpoint call
    console.log('Training model:', modelType);
}

function filterUsers() {
    const search = document.getElementById('user-search')?.value.toLowerCase() || '';
    const rows = document.querySelectorAll('#users-table-body tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(search) ? '' : 'none';
    });
}

// ========================================================================
// NOTIFICATIONS / BROADCAST
// ========================================================================

async function handleBroadcast(e) {
    e.preventDefault();
    const title = document.getElementById('broadcast-title')?.value;
    const body = document.getElementById('broadcast-body')?.value;
    
    if (!title || !body) {
        alert('Title and message are required');
        return;
    }
    
    try {
        const res = await fetch('/api/admin/messages/broadcast', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ title, body })
        });
        
        const data = await res.json();
        if (res.ok) {
            alert(`✅ ${data.message}`);
            document.getElementById('broadcast-form')?.reset();
            loadNotifications();
        } else {
            alert('❌ Failed to send broadcast: ' + (data.error || 'Unknown error'));
        }
    } catch (e) {
        console.error('Broadcast error:', e);
        alert('❌ Failed to send broadcast');
    }
}

async function loadNotifications() {
    // Load users for dropdown
    await loadUsersForMessage();
    
    // Load sent messages
    try {
        const res = await fetch('/api/admin/messages/sent?limit=20', {
            headers: getAuthHeaders()
        });
        
        if (!res.ok) {
            console.warn('Messages endpoint returned:', res.status);
            return;
        }
        
        const data = await res.json();
        const historyDiv = document.getElementById('message-history-list');
        
        if (!historyDiv) return;
        
        if (!data.messages || data.messages.length === 0) {
            historyDiv.innerHTML = '<p class="text-center py-5"><span class="text-muted" style="font-size: 1.1rem; font-weight: 500;">No messages sent yet</span></p>';
            return;
        }
        
        historyDiv.innerHTML = data.messages.map(msg => `
            <div class="card mb-3 border-secondary" style="background-color: var(--bs-card-bg);">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="mb-0" style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary);">${msg.title}</h6>
                        <span class="badge ${msg.is_broadcast ? 'bg-primary' : 'bg-secondary'}" style="font-size: 0.85rem; font-weight: 600;">
                            ${msg.is_broadcast ? '<i class="bi bi-broadcast me-1"></i>Broadcast' : 'Direct'}
                        </span>
                    </div>
                    <p class="mb-2" style="font-size: 1rem; font-weight: 500; color: var(--text-primary); line-height: 1.6;">${msg.body}</p>
                    <small class="text-muted" style="font-size: 0.95rem; font-weight: 500;">
                        <i class="bi bi-clock me-1"></i>${new Date(msg.created_at).toLocaleString()}
                    </small>
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Failed to load notifications:', e);
        const historyDiv = document.getElementById('message-history-list');
        if (historyDiv) {
            historyDiv.innerHTML = '<p class="text-danger text-center">Failed to load messages</p>';
        }
    }
}

async function loadUsersForMessage() {
    try {
        const res = await fetch('/api/admin/users', {
            headers: getAuthHeaders()
        });
        
        if (!res.ok) {
            console.warn('Failed to load users for message dropdown');
            return;
        }
        
        const data = await res.json();
        const select = document.getElementById('message-user-id');
        
        if (!select) return;
        
        // Clear existing options
        select.innerHTML = '<option value="">-- Choose a user --</option>';
        
        if (!data.users || data.users.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No users available';
            option.disabled = true;
            select.appendChild(option);
            return;
        }
        
        // Add users to dropdown
        data.users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id; // Use actual ID for sending
            option.textContent = `${user.full_name || user.username} (${user.email})`;
            option.setAttribute('data-email', user.email);
            select.appendChild(option);
        });
    } catch (e) {
        console.error('Failed to load users for message:', e);
    }
}

// Handle individual message form submission
document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const userId = document.getElementById('message-user-id')?.value;
            const title = document.getElementById('message-title')?.value;
            const body = document.getElementById('message-body')?.value;
            
            if (!userId) {
                alert('Please select a user');
                return;
            }
            
            if (!title || !body) {
                alert('Title and message are required');
                return;
            }
            
            try {
                const res = await fetch('/api/admin/messages', {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({
                        receiver_id: userId,
                        title: title,
                        body: body,
                        is_broadcast: false
                    })
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    alert('✅ Message sent successfully!');
                    messageForm.reset();
                    loadNotifications();
                } else {
                    alert('❌ Failed: ' + (data.error || 'Unknown error'));
                }
            } catch (e) {
                console.error('Message send error:', e);
                alert('❌ Failed to send message');
            }
        });
    }
});

// ========================================================================
// RESOURCES
// ========================================================================

async function loadResources() {
    try {
        const res = await fetch('/api/admin/resources', {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        renderResourcesList(data.resources || []);
    } catch (e) {
        console.error('Failed to load resources:', e);
    }
}

function renderResourcesList(resources) {
    const listDiv = document.getElementById('resources-list');
    if (!listDiv) return;
    
    if (resources.length === 0) {
        listDiv.innerHTML = '<div class="alert alert-info text-center py-4" style="font-size: 1.1rem; font-weight: 500;"><i class="bi bi-info-circle me-2"></i>No resources yet. Add one to get started!</div>';
        return;
    }
    
    listDiv.innerHTML = `
        <div class="table-responsive">
            <table class="table table-dark table-hover">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Description</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${resources.map(r => `
                        <tr>
                            <td><strong>${r.title}</strong></td>
                            <td><small class="text-muted">${(r.description || '').substring(0, 50)}${(r.description || '').length > 50 ? '...' : ''}</small></td>
                            <td><span class="badge bg-info"><i class="bi bi-${getResourceIcon(r.type)} me-1"></i>${r.type}</span></td>
                            <td>${r.is_active ? '<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>Active</span>' : '<span class="badge bg-secondary"><i class="bi bi-x-circle me-1"></i>Inactive</span>'}</td>
                            <td><small>${new Date(r.created_at).toLocaleDateString()}</small></td>
                            <td>
                                <button class="btn btn-sm btn-outline-warning me-1" onclick="editResource(${r.id})" title="Edit">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteResource(${r.id})" title="Delete">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function getResourceIcon(type) {
    const icons = {
        'pdf': 'file-pdf',
        'video': 'play-circle',
        'article': 'file-text',
        'link': 'link-45deg'
    };
    return icons[type] || 'file';
}

function editResource(id) {
    // TODO: Implement resource editing
    alert('Edit resource: ' + id);
}

function showResourceForm() {
    document.getElementById('resource-form').style.display = 'block';
}

function hideResourceForm() {
    document.getElementById('resource-form').style.display = 'none';
    document.getElementById('new-resource-form')?.reset();
}

async function handleResourceSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('resource-title')?.value;
    const description = document.getElementById('resource-description')?.value;
    const type = document.getElementById('resource-type')?.value;
    const url = document.getElementById('resource-url')?.value;
    const isActive = document.getElementById('resource-active')?.checked;
    
    try {
        const res = await fetch('/api/admin/resources', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ title, description, type, url_or_path: url, is_active: isActive })
        });
        
        if (res.ok) {
            alert('✅ Resource created successfully');
            hideResourceForm();
            loadResources();
        } else {
            const data = await res.json();
            alert('❌ Failed: ' + (data.error || 'Unknown error'));
        }
    } catch (e) {
        console.error('Resource creation error:', e);
        alert('❌ Failed to create resource');
    }
}

async function deleteResource(id) {
    if (!confirm('Are you sure you want to delete this resource?')) return;
    
    try {
        const res = await fetch(`/api/admin/resources/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        if (res.ok) {
            alert('✅ Resource deleted');
            loadResources();
        } else {
            alert('❌ Failed to delete resource');
        }
    } catch (e) {
        console.error('Delete error:', e);
        alert('❌ Failed to delete resource');
    }
}

// ========================================================================
// MODEL MANAGEMENT
// ========================================================================

async function loadModelManagement() {
    await Promise.all([
        loadModelVersions(),
        loadModelMetrics()
    ]);
}

async function loadModelVersions() {
    try {
        const res = await fetch('/api/admin/model-versions', {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        const infoDiv = document.getElementById('model-version-info');
        if (infoDiv) {
            infoDiv.innerHTML = `
                <div class="row">
                    <div class="col-md-4">
                        <strong>Model Version:</strong><br>
                        <span class="badge bg-primary fs-6">${data.model_version || 'v1.0'}</span>
                    </div>
                    <div class="col-md-4">
                        <strong>Last Trained:</strong><br>
                        <span class="text-muted">${data.last_trained_at ? new Date(data.last_trained_at).toLocaleString() : 'Not available'}</span>
                    </div>
                    <div class="col-md-4">
                        <strong>Status:</strong><br>
                        <span class="badge bg-success">Active</span>
                    </div>
                </div>
                ${data.metrics ? `
                    <hr>
                    <h6>Key Metrics:</h6>
                    <div class="table-responsive">
                        <table class="table table-sm table-dark">
                            <thead>
                                <tr>
                                    <th>Model</th>
                                    <th>Accuracy</th>
                                    <th>F1 Score</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.metrics.text_stress ? `
                                    <tr>
                                        <td>Text Stress</td>
                                        <td>${(data.metrics.text_stress.accuracy * 100).toFixed(1)}%</td>
                                        <td>${data.metrics.text_stress.f1?.toFixed(3) || 'N/A'}</td>
                                    </tr>
                                ` : ''}
                                ${data.metrics.image_emotion ? `
                                    <tr>
                                        <td>Image Emotion</td>
                                        <td>${(data.metrics.image_emotion.accuracy * 100).toFixed(1)}%</td>
                                        <td>${data.metrics.image_emotion.f1?.toFixed(3) || 'N/A'}</td>
                                    </tr>
                                ` : ''}
                            </tbody>
                        </table>
                    </div>
                ` : ''}
            `;
        }
    } catch (e) {
        console.error('Failed to load model versions:', e);
    }
}

async function loadModelMetrics() {
    try {
        const res = await fetch('/api/admin/metrics', {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        const metricsDiv = document.getElementById('model-metrics-content');
        if (metricsDiv) {
            if (data.metrics) {
                metricsDiv.innerHTML = `<pre class="text-light">${JSON.stringify(data.metrics, null, 2)}</pre>`;
            } else {
                metricsDiv.innerHTML = '<p class="text-muted">No metrics available yet.</p>';
            }
        }
    } catch (e) {
        console.error('Failed to load metrics:', e);
    }
}

// ========================================================================
// AUDIT LOGS
// ========================================================================

async function loadAuditLogs() {
    try {
        const res = await fetch('/api/admin/logs?limit=100', {
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        renderAuditLogs(data.logs || []);
    } catch (e) {
        console.error('Failed to load audit logs:', e);
    }
}

function renderAuditLogs(logs) {
    const tbody = document.getElementById('logs-table-body');
    if (!tbody) return;
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center py-5"><span class="text-muted" style="font-size: 1.1rem; font-weight: 500;">No audit logs yet</span></td></tr>';
        return;
    }
    
        tbody.innerHTML = logs.map(log => {
        const actionBadge = getActionBadge(log.action);
        return `
        <tr>
            <td style="font-weight: 600; font-size: 1rem;">
                <div>
                    <strong style="font-size: 1.05rem;">${new Date(log.created_at).toLocaleDateString()}</strong><br>
                    <small class="text-muted" style="font-size: 0.9rem; font-weight: 500;">${new Date(log.created_at).toLocaleTimeString()}</small>
                </div>
            </td>
            <td><span class="badge bg-secondary" style="font-size: 0.9rem; font-weight: 600;">${log.admin_email || 'Unknown'}</span></td>
            <td>${actionBadge}</td>
            <td style="font-weight: 500; font-size: 1rem;">${log.details || '-'}</td>
        </tr>
    `;
    }).join('');
}

function getActionBadge(action) {
    const badges = {
        'SEND_BROADCAST': '<span class="badge bg-primary"><i class="bi bi-broadcast me-1"></i>Broadcast</span>',
        'ADD_RESOURCE': '<span class="badge bg-success"><i class="bi bi-plus-circle me-1"></i>Add Resource</span>',
        'UPDATE_RESOURCE': '<span class="badge bg-warning"><i class="bi bi-pencil me-1"></i>Update Resource</span>',
        'DELETE_RESOURCE': '<span class="badge bg-danger"><i class="bi bi-trash me-1"></i>Delete Resource</span>',
        'TRAIN_MODEL': '<span class="badge bg-info"><i class="bi bi-cpu me-1"></i>Train Model</span>',
    };
    return badges[action] || `<code class="text-light">${action}</code>`;
}

// ========================================================================
// ANALYSES
// ========================================================================

async function loadAnalyses() {
    try {
        analysesOffset = 0;
        await loadMoreAnalyses();
    } catch (e) {
        console.error('Failed to load analyses:', e);
    }
}

async function loadMoreAnalyses() {
    try {
        const res = await fetch(`/api/admin/analyses?limit=${analysesLimit}&offset=${analysesOffset}`, {
            headers: getAuthHeaders()
        });
        
        if (!res.ok) {
            console.warn('Analyses endpoint returned:', res.status);
            return;
        }
        
        const data = await res.json();
        const tbody = document.getElementById('analyses-table-body');
        const countEl = document.getElementById('analyses-count');
        const loadMoreBtn = document.getElementById('load-more-btn');
        
        if (!tbody) return;
        
        if (analysesOffset === 0) {
            // First load - replace content
        if (data.analyses.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-5"><span class="text-muted" style="font-size: 1.1rem; font-weight: 500;">No analyses found</span></td></tr>';
            if (countEl) countEl.textContent = 'No analyses';
            if (loadMoreBtn) loadMoreBtn.style.display = 'none';
            return;
        }
            tbody.innerHTML = '';
        }
        
        // Append new analyses
        data.analyses.forEach(a => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><code>${a.hashed_user_id}</code></td>
                <td>${new Date(a.created_at).toLocaleString()}</td>
                <td><span class="badge bg-info">${a.emotion || 'N/A'} ${a.emotion_emoji || ''}</span></td>
                <td><span class="badge ${getStressBadgeClass(a.stress_level)}">${a.stress_level || 'N/A'}</span></td>
                <td><span class="badge ${getRiskBadgeClass(a.risk_level)}">${a.risk_level || 'N/A'}</span></td>
                <td><span class="badge bg-secondary">${a.mode || 'N/A'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="viewAnalysisDetails(${a.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Update count and load more button
        if (countEl) {
            countEl.textContent = `Showing ${Math.min(analysesOffset + data.analyses.length, data.total)} of ${data.total} analyses`;
        }
        
        if (loadMoreBtn) {
            loadMoreBtn.style.display = (analysesOffset + data.analyses.length < data.total) ? 'inline-block' : 'none';
        }
        
        analysesOffset += data.analyses.length;
    } catch (e) {
        console.error('Failed to load analyses:', e);
    }
}

function refreshAnalyses() {
    analysesOffset = 0;
    loadAnalyses();
}

function viewAnalysisDetails(id) {
    // TODO: Implement analysis detail modal
    alert('Analysis details for ID: ' + id);
}

// ========================================================================
// UTILITY
// ========================================================================

function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme') || 'dark';
    const newTheme = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('mindscope_theme', newTheme);
    
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.className = newTheme === 'dark' ? 'bi bi-moon' : 'bi bi-sun';
    }
}

function logout() {
    localStorage.removeItem('mindscope_session');
    window.location.href = '/';
}


