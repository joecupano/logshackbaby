/**
 * LogShackBaby Frontend Application
 * Amateur Radio Log Server Client
 */

// Configuration
const API_BASE = window.location.origin + '/api';
let sessionToken = null;
let currentUser = null;
let currentPage = 1;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Check for existing session
    sessionToken = localStorage.getItem('sessionToken');
    
    if (sessionToken) {
        // Try to load dashboard
        loadDashboard();
    } else {
        showScreen('login');
    }
    
    // Setup event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // Auth forms
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('mfa-verify-form').addEventListener('submit', handleMFAVerify);
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        showScreen('register');
    });
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        showScreen('login');
    });
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // Tab navigation
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    // Logs
    document.getElementById('apply-filters').addEventListener('click', loadLogs);
    document.getElementById('export-logs-btn').addEventListener('click', exportLogs);
    
    // Upload
    document.getElementById('upload-btn').addEventListener('click', handleUpload);
    
    // API Keys
    document.getElementById('create-api-key-btn').addEventListener('click', createAPIKey);
    document.getElementById('copy-api-key')?.addEventListener('click', copyAPIKey);
    
    // Settings
    document.getElementById('enable-mfa-btn')?.addEventListener('click', startMFASetup);
    document.getElementById('mfa-enable-form')?.addEventListener('submit', enableMFA);
    document.getElementById('cancel-mfa-setup')?.addEventListener('click', cancelMFASetup);
    document.getElementById('disable-mfa-btn')?.addEventListener('click', disableMFA);
}

// Screen Management
function showScreen(screenName) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    document.getElementById(`${screenName}-screen`).classList.add('active');
    
    if (screenName === 'dashboard') {
        document.getElementById('navbar').classList.remove('hidden');
    } else {
        document.getElementById('navbar').classList.add('hidden');
    }
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Load tab-specific data
    switch(tabName) {
        case 'logs':
            loadLogs();
            loadStats();
            break;
        case 'upload':
            loadUploads();
            break;
        case 'api-keys':
            loadAPIKeys();
            break;
        case 'settings':
            loadSettings();
            break;
    }
}

// Messages
function showMessage(text, type = 'info') {
    const container = document.getElementById('message-container');
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    
    container.appendChild(message);
    
    setTimeout(() => {
        message.remove();
    }, 5000);
}

// API Helper
async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (sessionToken && !options.skipAuth) {
        headers['X-Session-Token'] = sessionToken;
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });
    
    if (!response.ok && response.status === 401) {
        // Session expired
        localStorage.removeItem('sessionToken');
        sessionToken = null;
        showScreen('login');
        showMessage('Session expired. Please login again.', 'error');
        throw new Error('Session expired');
    }
    
    return response;
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    
    const callsign = document.getElementById('login-callsign').value.trim().toUpperCase();
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await apiCall('/login', {
            method: 'POST',
            body: JSON.stringify({ callsign, password }),
            skipAuth: true
        });
        
        const data = await response.json();
        
        if (response.ok) {
            sessionToken = data.session_token;
            currentUser = { callsign: data.callsign };
            
            if (data.mfa_required) {
                // Show MFA verification
                document.getElementById('login-form-container').classList.add('hidden');
                document.getElementById('mfa-verify-container').classList.remove('hidden');
            } else {
                // Login complete
                localStorage.setItem('sessionToken', sessionToken);
                loadDashboard();
            }
        } else {
            showMessage(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('Login failed. Please try again.', 'error');
    }
}

async function handleMFAVerify(e) {
    e.preventDefault();
    
    const token = document.getElementById('mfa-verify-code').value;
    
    try {
        const response = await apiCall('/mfa/verify', {
            method: 'POST',
            body: JSON.stringify({ session_token: sessionToken, token }),
            skipAuth: true
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('sessionToken', sessionToken);
            loadDashboard();
        } else {
            showMessage(data.error || 'Invalid code', 'error');
        }
    } catch (error) {
        showMessage('Verification failed. Please try again.', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const callsign = document.getElementById('register-callsign').value.trim().toUpperCase();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const passwordConfirm = document.getElementById('register-password-confirm').value;
    
    if (password !== passwordConfirm) {
        showMessage('Passwords do not match', 'error');
        return;
    }
    
    try {
        const response = await apiCall('/register', {
            method: 'POST',
            body: JSON.stringify({ callsign, email, password }),
            skipAuth: true
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Registration successful! Please login.', 'success');
            showScreen('login');
            document.getElementById('login-callsign').value = callsign;
        } else {
            showMessage(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('Registration failed. Please try again.', 'error');
    }
}

async function handleLogout() {
    try {
        await apiCall('/logout', { method: 'POST' });
    } catch (error) {
        // Ignore errors
    }
    
    localStorage.removeItem('sessionToken');
    sessionToken = null;
    currentUser = null;
    showScreen('login');
    showMessage('Logged out successfully', 'success');
}

// Dashboard
async function loadDashboard() {
    showScreen('dashboard');
    
    // Get user info from session
    try {
        const response = await apiCall('/logs/stats');
        if (response.ok) {
            switchTab('logs');
        }
    } catch (error) {
        // Session invalid, return to login
        showScreen('login');
    }
}

// Logs
async function loadLogs(page = 1) {
    currentPage = page;
    
    const callsign = document.getElementById('filter-callsign').value;
    const band = document.getElementById('filter-band').value;
    const mode = document.getElementById('filter-mode').value;
    
    const params = new URLSearchParams({
        page: currentPage,
        per_page: 50
    });
    
    if (callsign) params.append('callsign', callsign);
    if (band) params.append('band', band);
    if (mode) params.append('mode', mode);
    
    try {
        const response = await apiCall(`/logs?${params}`);
        const data = await response.json();
        
        if (response.ok) {
            displayLogs(data.logs);
            displayPagination(data.current_page, data.pages);
        }
    } catch (error) {
        showMessage('Failed to load logs', 'error');
    }
}

function displayLogs(logs) {
    const tbody = document.getElementById('logs-tbody');
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">No logs found</td></tr>';
        return;
    }
    
    tbody.innerHTML = logs.map(log => `
        <tr>
            <td>${formatDate(log.qso_date)}</td>
            <td>${formatTime(log.time_on)}</td>
            <td><strong>${log.call}</strong></td>
            <td>${log.band || '-'}</td>
            <td>${log.mode || '-'}</td>
            <td>${log.rst_sent || '-'}</td>
            <td>${log.rst_rcvd || '-'}</td>
            <td>${log.gridsquare || '-'}</td>
        </tr>
    `).join('');
}

function displayPagination(currentPage, totalPages) {
    const container = document.getElementById('logs-pagination');
    
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="loadLogs(${currentPage - 1})">Previous</button>`;
    
    // Page numbers (show up to 5 pages)
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, startPage + 4);
    
    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="loadLogs(${i})">${i}</button>`;
    }
    
    // Next button
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="loadLogs(${currentPage + 1})">Next</button>`;
    
    container.innerHTML = html;
}

async function loadStats() {
    try {
        const response = await apiCall('/logs/stats');
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('stat-total-qsos').textContent = data.total_qsos;
            document.getElementById('stat-unique-calls').textContent = data.unique_callsigns;
            document.getElementById('stat-bands').textContent = Object.keys(data.bands).length;
            document.getElementById('stat-modes').textContent = Object.keys(data.modes).length;
            
            // Populate filter dropdowns
            const bandSelect = document.getElementById('filter-band');
            const modeSelect = document.getElementById('filter-mode');
            
            bandSelect.innerHTML = '<option value="">All Bands</option>' + 
                Object.keys(data.bands).sort().map(band => `<option value="${band}">${band}</option>`).join('');
            
            modeSelect.innerHTML = '<option value="">All Modes</option>' + 
                Object.keys(data.modes).sort().map(mode => `<option value="${mode}">${mode}</option>`).join('');
        }
    } catch (error) {
        showMessage('Failed to load statistics', 'error');
    }
}

// Upload
async function handleUpload() {
    const fileInput = document.getElementById('adif-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Please select a file', 'error');
        return;
    }
    
    // Get an API key first
    const apiKey = prompt('Please enter your API key for uploading:');
    if (!apiKey) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/logs/upload`, {
            method: 'POST',
            headers: {
                'X-API-Key': apiKey
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`Upload successful! New: ${data.new}, Duplicates: ${data.duplicates}`, 'success');
            
            // Display result
            const resultDiv = document.getElementById('upload-result');
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>Upload Complete</strong>
                    <p>Total records: ${data.total}</p>
                    <p>New records added: ${data.new}</p>
                    <p>Duplicates skipped: ${data.duplicates}</p>
                    ${data.errors > 0 ? `<p>Errors: ${data.errors}</p>` : ''}
                </div>
            `;
            resultDiv.classList.remove('hidden');
            
            // Clear file input
            fileInput.value = '';
            
            // Reload uploads history
            loadUploads();
            
            // Refresh stats if on logs tab
            loadStats();
        } else {
            showMessage(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showMessage('Upload failed. Please try again.', 'error');
    }
}

async function loadUploads() {
    try {
        const response = await apiCall('/uploads');
        const data = await response.json();
        
        if (response.ok) {
            displayUploads(data.uploads);
        }
    } catch (error) {
        showMessage('Failed to load upload history', 'error');
    }
}

function displayUploads(uploads) {
    const tbody = document.getElementById('uploads-tbody');
    
    if (uploads.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No uploads yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = uploads.map(upload => `
        <tr>
            <td>${upload.filename}</td>
            <td>${formatDateTime(upload.uploaded_at)}</td>
            <td>${upload.total_records}</td>
            <td>${upload.new_records}</td>
            <td>${upload.duplicate_records}</td>
            <td><span class="status-${upload.status}">${upload.status}</span></td>
        </tr>
    `).join('');
}

// API Keys
async function loadAPIKeys() {
    try {
        const response = await apiCall('/keys');
        const data = await response.json();
        
        if (response.ok) {
            displayAPIKeys(data.keys);
        }
    } catch (error) {
        showMessage('Failed to load API keys', 'error');
    }
}

function displayAPIKeys(keys) {
    const tbody = document.getElementById('api-keys-tbody');
    
    if (keys.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No API keys yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = keys.map(key => `
        <tr>
            <td><code>${key.prefix}...</code></td>
            <td>${key.description || '-'}</td>
            <td>${formatDateTime(key.created_at)}</td>
            <td>${key.last_used ? formatDateTime(key.last_used) : 'Never'}</td>
            <td>
                <button class="btn btn-danger btn-small" onclick="deleteAPIKey(${key.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

async function createAPIKey() {
    const description = prompt('Enter a description for this API key (optional):');
    
    try {
        const response = await apiCall('/keys', {
            method: 'POST',
            body: JSON.stringify({ description: description || '' })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Display the new API key
            document.getElementById('new-api-key-value').textContent = data.api_key;
            document.getElementById('new-api-key-display').classList.remove('hidden');
            
            // Reload keys list
            loadAPIKeys();
            
            showMessage('API key created successfully!', 'success');
        } else {
            showMessage(data.error || 'Failed to create API key', 'error');
        }
    } catch (error) {
        showMessage('Failed to create API key', 'error');
    }
}

function copyAPIKey() {
    const apiKey = document.getElementById('new-api-key-value').textContent;
    navigator.clipboard.writeText(apiKey).then(() => {
        showMessage('API key copied to clipboard', 'success');
    });
}

async function deleteAPIKey(keyId) {
    if (!confirm('Are you sure you want to delete this API key? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await apiCall(`/keys/${keyId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showMessage('API key deleted', 'success');
            loadAPIKeys();
        } else {
            showMessage('Failed to delete API key', 'error');
        }
    } catch (error) {
        showMessage('Failed to delete API key', 'error');
    }
}

// Settings / MFA
async function loadSettings() {
    // Check MFA status from current user state
    // For now, we'll need to add an endpoint or store this info
    // Simplified: assume MFA is disabled initially
    document.getElementById('mfa-disabled').classList.remove('hidden');
    document.getElementById('mfa-enabled').classList.add('hidden');
    document.getElementById('mfa-setup').classList.add('hidden');
}

async function startMFASetup() {
    try {
        const response = await apiCall('/mfa/setup', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Display QR code
            document.getElementById('mfa-qr-code').innerHTML = `<img src="${data.qr_code}" alt="QR Code">`;
            document.getElementById('mfa-secret').textContent = data.secret;
            
            // Show setup form
            document.getElementById('mfa-disabled').classList.add('hidden');
            document.getElementById('mfa-setup').classList.remove('hidden');
        } else {
            showMessage(data.error || 'Failed to setup MFA', 'error');
        }
    } catch (error) {
        showMessage('Failed to setup MFA', 'error');
    }
}

async function enableMFA(e) {
    e.preventDefault();
    
    const token = document.getElementById('mfa-enable-code').value;
    
    try {
        const response = await apiCall('/mfa/enable', {
            method: 'POST',
            body: JSON.stringify({ token })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Two-factor authentication enabled!', 'success');
            
            // Update UI
            document.getElementById('mfa-setup').classList.add('hidden');
            document.getElementById('mfa-enabled').classList.remove('hidden');
        } else {
            showMessage(data.error || 'Invalid code', 'error');
        }
    } catch (error) {
        showMessage('Failed to enable MFA', 'error');
    }
}

function cancelMFASetup() {
    document.getElementById('mfa-setup').classList.add('hidden');
    document.getElementById('mfa-disabled').classList.remove('hidden');
}

async function disableMFA() {
    const password = prompt('Enter your password to disable 2FA:');
    if (!password) return;
    
    try {
        const response = await apiCall('/mfa/disable', {
            method: 'POST',
            body: JSON.stringify({ password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Two-factor authentication disabled', 'success');
            
            // Update UI
            document.getElementById('mfa-enabled').classList.add('hidden');
            document.getElementById('mfa-disabled').classList.remove('hidden');
        } else {
            showMessage(data.error || 'Failed to disable MFA', 'error');
        }
    } catch (error) {
        showMessage('Failed to disable MFA', 'error');
    }
}

// Export Logs
async function exportLogs() {
    const callsign = document.getElementById('filter-callsign').value;
    const band = document.getElementById('filter-band').value;
    const mode = document.getElementById('filter-mode').value;
    
    const params = new URLSearchParams();
    if (callsign) params.append('callsign', callsign);
    if (band) params.append('band', band);
    if (mode) params.append('mode', mode);
    
    try {
        const response = await fetch(`${API_BASE}/logs/export?${params}`, {
            headers: {
                'X-Session-Token': sessionToken
            }
        });
        
        if (response.ok) {
            // Get filename from header or use default
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'logbook.adi';
            if (contentDisposition) {
                const matches = /filename="([^"]+)"/.exec(contentDisposition);
                if (matches) filename = matches[1];
            }
            
            // Download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showMessage('Logs exported successfully', 'success');
        } else {
            showMessage('Failed to export logs', 'error');
        }
    } catch (error) {
        showMessage('Export failed. Please try again.', 'error');
    }
}

// Utility Functions
function formatDate(dateStr) {
    if (!dateStr) return '-';
    // YYYYMMDD -> YYYY-MM-DD
    return `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
}

function formatTime(timeStr) {
    if (!timeStr) return '-';
    // HHMMSS -> HH:MM:SS or HH:MM
    const hours = timeStr.substring(0, 2);
    const minutes = timeStr.substring(2, 4);
    return `${hours}:${minutes}`;
}

function formatDateTime(isoStr) {
    if (!isoStr) return '-';
    const date = new Date(isoStr);
    return date.toLocaleString();
}

// Make functions globally accessible for onclick handlers
window.loadLogs = loadLogs;
window.deleteAPIKey = deleteAPIKey;
