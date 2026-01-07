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
    const userRole = localStorage.getItem('userRole');
    
    if (sessionToken && userRole) {
        // Restore currentUser from localStorage
        currentUser = { role: userRole };
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
    
    // Admin
    document.getElementById('create-user-btn')?.addEventListener('click', showCreateUserForm);
    document.getElementById('cancel-create-user')?.addEventListener('click', hideCreateUserForm);
    document.getElementById('admin-create-user-form')?.addEventListener('submit', handleAdminCreateUser);
    
    // Log Admin Report
    document.getElementById('generate-report-btn')?.addEventListener('click', generateReport);
    document.getElementById('export-csv-btn')?.addEventListener('click', exportReportToCSV);
    
    // Subtab navigation - using event delegation
    document.addEventListener('click', (e) => {
        if (e.target.matches('.subtab')) {
            switchLogAdminSubtab(e.target.dataset.subtab);
        }
    });
}

function switchLogAdminSubtab(subtabName) {
    // Update subtab buttons
    document.querySelectorAll('#logadmin-tab .subtab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`#logadmin-tab [data-subtab="${subtabName}"]`).classList.add('active');
    
    // Update subtab content
    document.querySelectorAll('#logadmin-tab .subtab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(subtabName).classList.add('active');
    
    // Load data if needed
    if (subtabName === 'logadmin-users') {
        loadLogAdminUsers();
    } else if (subtabName === 'logadmin-report') {
        loadAdditionalFields();
    }
}

async function loadAdditionalFields() {
    const container = document.getElementById('additional-fields-container');
    const grid = document.getElementById('additional-fields-grid');
    
    try {
        const response = await apiCall('/logadmin/available-fields');
        const data = await response.json();
        
        console.log('Additional fields response:', data);
        
        if (response.ok) {
            const allFields = data.all_fields || [];
            const fieldsWithData = new Set(data.fields_with_data || []);
            
            if (allFields.length > 0) {
                const html = allFields.map(field => {
                    const label = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    const hasData = fieldsWithData.has(field);
                    const dataIndicator = hasData ? ' <span class="has-data-indicator" title="This field has data in logs">●</span>' : '';
                    const labelClass = hasData ? 'field-with-data' : 'field-no-data';
                    return `<label class="${labelClass}"><input type="checkbox" name="report-field" value="json:${field}"> ${label}${dataIndicator}</label>`;
                }).join('');
                
                const infoText = `<p style="font-size: 0.9em; color: #666; margin-bottom: 10px;">Showing all ${allFields.length} ADIF 3.1.6 fields. Fields with <span class="has-data-indicator">●</span> contain data in uploaded logs.</p>`;
                grid.innerHTML = infoText + html;
                container.classList.remove('hidden');
            } else {
                grid.innerHTML = '<p style="font-style: italic; color: #666;">No additional ADIF fields available</p>';
                container.classList.remove('hidden');
            }
        } else {
            console.error('Failed to load additional fields:', data);
            grid.innerHTML = '<p style="font-style: italic; color: #999;">Unable to load additional fields</p>';
            container.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading additional fields:', error);
        grid.innerHTML = '<p style="font-style: italic; color: #999;">Error loading additional fields</p>';
        container.classList.remove('hidden');
    }
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
        case 'logadmin':
            loadLogAdminUsers();
            break;
        case 'sysop':
            loadSysopUsers();
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
    
    // Only treat 401 as session expired if we sent a session token
    if (!response.ok && response.status === 401 && !options.skipAuth && sessionToken) {
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
            currentUser = { 
                callsign: data.callsign,
                role: data.role || 'user'
            };
            
            if (data.mfa_required) {
                // Show MFA verification
                document.getElementById('login-form-container').classList.add('hidden');
                document.getElementById('mfa-verify-container').classList.remove('hidden');
            } else {
                // Login complete
                localStorage.setItem('sessionToken', sessionToken);
                localStorage.setItem('userRole', currentUser.role);
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
            localStorage.setItem('userRole', currentUser.role);
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
        console.error('Registration error:', error);
        showMessage(`Registration failed: ${error.message}`, 'error');
    }
}

async function handleLogout() {
    try {
        await apiCall('/logout', { method: 'POST' });
    } catch (error) {
        // Ignore errors
    }
    
    localStorage.removeItem('sessionToken');
    localStorage.removeItem('userRole');
    sessionToken = null;
    currentUser = null;
    showScreen('login');
    showMessage('Logged out successfully', 'success');
}

// Dashboard
async function loadDashboard() {
    showScreen('dashboard');
    
    // Hide admin tabs and contest links by default
    document.getElementById('contests-link-btn').classList.add('hidden');
    document.getElementById('contest-admin-link-btn').classList.add('hidden');
    document.getElementById('logadmin-tab-btn').classList.add('hidden');
    document.getElementById('sysop-tab-btn').classList.add('hidden');
    
    // Show contest links for all authenticated users
    document.getElementById('contests-link-btn').classList.remove('hidden');
    
    // Show admin tabs and links based on role hierarchy
    const userRole = localStorage.getItem('userRole') || 'user';
    if (userRole === 'contestadmin') {
        document.getElementById('contest-admin-link-btn').classList.remove('hidden');
    }
    if (userRole === 'logadmin') {
        document.getElementById('logadmin-tab-btn').classList.remove('hidden');
    }
    if (userRole === 'sysop') {
        document.getElementById('contest-admin-link-btn').classList.remove('hidden');
        document.getElementById('logadmin-tab-btn').classList.remove('hidden');
        document.getElementById('sysop-tab-btn').classList.remove('hidden');
    }
    
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
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No logs found</td></tr>';
        return;
    }
    
    tbody.innerHTML = logs.map(log => {
        // Format additional fields for display
        let additionalFieldsHtml = '-';
        if (log.additional_fields && Object.keys(log.additional_fields).length > 0) {
            const fields = Object.entries(log.additional_fields)
                .map(([key, value]) => {
                    // Format field name nicely
                    const fieldName = key.toUpperCase().replace(/_/g, ' ');
                    return `${fieldName}: ${value}`;
                })
                .join('\n');
            
            const count = Object.keys(log.additional_fields).length;
            additionalFieldsHtml = `<span class="additional-fields-badge" title="${escapeHtml(fields)}">${count} field${count > 1 ? 's' : ''}</span>`;
        }
        
        return `
        <tr>
            <td>${formatDate(log.qso_date)}</td>
            <td>${formatTime(log.time_on)}</td>
            <td><strong>${log.call}</strong></td>
            <td>${log.band || '-'}</td>
            <td>${log.mode || '-'}</td>
            <td>${log.rst_sent || '-'}</td>
            <td>${log.rst_rcvd || '-'}</td>
            <td>${log.gridsquare || '-'}</td>
            <td>${additionalFieldsHtml}</td>
        </tr>
        `;
    }).join('');
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
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

// Admin Functions - Log Admin
async function loadLogAdminUsers() {
    try {
        const response = await apiCall('/logadmin/users');
        const data = await response.json();
        
        if (response.ok) {
            displayLogAdminUsers(data.users);
        }
    } catch (error) {
        showMessage('Failed to load users', 'error');
    }
}

function displayLogAdminUsers(users) {
    const container = document.getElementById('logadmin-users-list');
    
    if (users.length === 0) {
        container.innerHTML = '<p>No users found</p>';
        return;
    }
    
    const html = `
        <table>
            <thead>
                <tr>
                    <th>Callsign</th>
                    <th>Log Count</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(u => `
                    <tr>
                        <td><strong>${u.callsign}</strong></td>
                        <td>${u.log_count}</td>
                        <td>${formatDateTime(u.created_at)}</td>
                        <td>
                            <button class="btn btn-sm" onclick="viewLogAdminUserLogs(${u.id}, '${u.callsign}')">View Logs</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

async function viewLogAdminUserLogs(userId, callsign) {
    try {
        const response = await apiCall(`/logadmin/users/${userId}/logs?page=1&per_page=100`);
        const data = await response.json();
        
        if (response.ok) {
            const logs = data.logs;
            const logHtml = logs.length > 0 ? `
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Call</th>
                            <th>Band</th>
                            <th>Mode</th>
                            <th>RST Sent</th>
                            <th>RST Rcvd</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${logs.map(log => `
                            <tr>
                                <td>${formatDate(log.qso_date)}</td>
                                <td>${formatTime(log.time_on)}</td>
                                <td><strong>${log.call}</strong></td>
                                <td>${log.band || '-'}</td>
                                <td>${log.mode || '-'}</td>
                                <td>${log.rst_sent || '-'}</td>
                                <td>${log.rst_rcvd || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <p>Total: ${data.total} logs (Read-only access)</p>
            ` : '<p>No logs found for this user</p>';
            
            const modal = `
                <div class="modal-overlay" id="contest-user-logs-modal">
                    <div class="modal-content">
                        <h3>${callsign}'s Logs</h3>
                        ${logHtml}
                        <button class="btn" onclick="closeModal('contest-user-logs-modal')">Close</button>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modal);
        }
    } catch (error) {
        showMessage('Failed to load user logs', 'error');
    }
}

async function generateReport() {
    const checkboxes = document.querySelectorAll('input[name="report-field"]:checked');
    const fields = Array.from(checkboxes).map(cb => cb.value);
    
    if (fields.length === 0) {
        showMessage('Please select at least one field', 'error');
        return;
    }
    
    // Get filters
    const filters = {};
    const dateFrom = document.getElementById('report-date-from').value;
    const dateTo = document.getElementById('report-date-to').value;
    const bandsInput = document.getElementById('report-bands').value;
    const modesInput = document.getElementById('report-modes').value;
    
    if (dateFrom) filters.date_from = dateFrom;
    if (dateTo) filters.date_to = dateTo;
    if (bandsInput) filters.bands = bandsInput.split(',').map(b => b.trim());
    if (modesInput) filters.modes = modesInput.split(',').map(m => m.trim());
    
    try {
        const response = await apiCall('/logadmin/report', {
            method: 'POST',
            body: JSON.stringify({ fields, filters })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayReport(data.report, data.fields, data.total);
            showMessage('Report generated successfully', 'success');
        } else {
            showMessage(data.error || 'Failed to generate report', 'error');
        }
    } catch (error) {
        showMessage('Failed to generate report', 'error');
    }
}

function displayReport(report, fields, total) {
    const container = document.getElementById('report-table-container');
    const resultsDiv = document.getElementById('report-results');
    const countSpan = document.getElementById('report-count');
    const exportBtn = document.getElementById('export-csv-btn');
    
    countSpan.textContent = `(${total} records)`;
    resultsDiv.classList.remove('hidden');
    exportBtn.classList.remove('hidden');
    
    // Store report data for export
    window.currentReport = { report, fields };
    
    if (report.length === 0) {
        container.innerHTML = '<p>No results found</p>';
        return;
    }
    
    // Build table headers
    const headers = fields.map(f => {
        let label = f;
        // Handle JSON fields
        if (f.startsWith('json:')) {
            label = f.substring(5); // Remove 'json:' prefix
        }
        label = label.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        return `<th>${label}</th>`;
    }).join('');
    
    // Build table rows
    const rows = report.map(row => {
        const cells = fields.map(field => {
            let value = row[field] || '-';
            
            // Format date
            if (field === 'qso_date' && value !== '-') {
                value = formatDate(value);
            }
            // Format time
            if ((field === 'time_on' || field === 'time_off') && value !== '-') {
                value = formatTime(value);
            }
            
            return `<td>${value}</td>`;
        }).join('');
        return `<tr>${cells}</tr>`;
    }).join('');
    
    container.innerHTML = `
        <div style="max-height: 600px; overflow-y: auto;">
            <table>
                <thead>
                    <tr>${headers}</tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    `;
}

function exportReportToCSV() {
    if (!window.currentReport) {
        showMessage('No report to export', 'error');
        return;
    }
    
    const { report, fields } = window.currentReport;
    
    // Build CSV headers
    const headers = fields.map(f => {
        let label = f;
        if (f.startsWith('json:')) {
            label = f.substring(5); // Remove 'json:' prefix
        }
        return label.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    });
    const csvRows = [headers.join(',')];
    
    report.forEach(row => {
        const values = fields.map(field => {
            let value = row[field] || '';
            // Escape commas and quotes
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                value = `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        });
        csvRows.push(values.join(','));
    });
    
    const csv = csvRows.join('\n');
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `contest_report_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showMessage('Report exported to CSV', 'success');
}

// Admin Functions - Log Admin
async function loadLogAdminUsers() {
    try {
        const response = await apiCall('/logadmin/users');
        const data = await response.json();
        
        if (response.ok) {
            displayLogAdminUsers(data.users);
        }
    } catch (error) {
        showMessage('Failed to load users', 'error');
    }
}

function displayLogAdminUsers(users) {
    const container = document.getElementById('logadmin-users-list');
    
    if (users.length === 0) {
        container.innerHTML = '<p>No users found</p>';
        return;
    }
    
    const html = `
        <table>
            <thead>
                <tr>
                    <th>Callsign</th>
                    <th>Log Count</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(u => `
                    <tr>
                        <td><strong>${u.callsign}</strong></td>
                        <td>${u.log_count}</td>
                        <td>${formatDateTime(u.created_at)}</td>
                        <td>
                            <button class="btn btn-sm" onclick="viewUserLogs(${u.id}, '${u.callsign}')">View Logs</button>
                            <button class="btn btn-sm btn-danger" onclick="resetUserLogs(${u.id}, '${u.callsign}')">Reset Logs</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

async function viewUserLogs(userId, callsign) {
    try {
        const response = await apiCall(`/logadmin/users/${userId}/logs?page=1&per_page=100`);
        const data = await response.json();
        
        if (response.ok) {
            const logs = data.logs;
            const logHtml = logs.length > 0 ? `
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Call</th>
                            <th>Band</th>
                            <th>Mode</th>
                            <th>RST Sent</th>
                            <th>RST Rcvd</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${logs.map(log => `
                            <tr>
                                <td>${formatDate(log.qso_date)}</td>
                                <td>${formatTime(log.time_on)}</td>
                                <td><strong>${log.call}</strong></td>
                                <td>${log.band || '-'}</td>
                                <td>${log.mode || '-'}</td>
                                <td>${log.rst_sent || '-'}</td>
                                <td>${log.rst_rcvd || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <p>Total: ${data.total} logs</p>
            ` : '<p>No logs found</p>';
            
            const container = document.getElementById('logadmin-users-list');
            container.innerHTML = `
                <div class="admin-section">
                    <h3>Logs for ${callsign}</h3>
                    <button class="btn btn-secondary" onclick="loadLogAdminUsers()">Back to Users</button>
                    ${logHtml}
                </div>
            `;
        }
    } catch (error) {
        showMessage('Failed to load user logs', 'error');
    }
}

async function resetUserLogs(userId, callsign) {
    if (!confirm(`Are you sure you want to reset ALL logs for ${callsign}? This cannot be undone!`)) {
        return;
    }
    
    try {
        const response = await apiCall(`/logadmin/users/${userId}/logs`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            loadLogAdminUsers();
        } else {
            showMessage(data.error || 'Failed to reset logs', 'error');
        }
    } catch (error) {
        showMessage('Failed to reset logs', 'error');
    }
}

// Admin Functions - Sysop
async function loadSysopUsers() {
    try {
        const response = await apiCall('/admin/users');
        const data = await response.json();
        
        if (response.ok) {
            displaySysopUsers(data.users);
        }
    } catch (error) {
        showMessage('Failed to load users', 'error');
    }
}

function displaySysopUsers(users) {
    const container = document.getElementById('sysop-users-list');
    
    if (users.length === 0) {
        container.innerHTML = '<p>No users found</p>';
        return;
    }
    
    const html = `
        <table>
            <thead>
                <tr>
                    <th>Callsign</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>MFA</th>
                    <th>Logs</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(u => `
                    <tr>
                        <td><strong>${u.callsign}</strong></td>
                        <td>${u.email}</td>
                        <td><span class="badge badge-${u.role}">${u.role}</span></td>
                        <td>${u.is_active ? '✓ Active' : '✗ Inactive'}</td>
                        <td>${u.mfa_enabled ? '✓' : '✗'}</td>
                        <td>${u.log_count}</td>
                        <td>${formatDateTime(u.created_at)}</td>
                        <td>
                            <button class="btn btn-sm" onclick="editUser(${u.id})">Edit</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteUser(${u.id}, '${u.callsign}')">Delete</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

function showCreateUserForm() {
    document.getElementById('create-user-form').classList.remove('hidden');
}

function hideCreateUserForm() {
    document.getElementById('create-user-form').classList.add('hidden');
    document.getElementById('admin-create-user-form').reset();
}

async function handleAdminCreateUser(e) {
    e.preventDefault();
    
    const callsign = document.getElementById('admin-user-callsign').value.trim().toUpperCase();
    const email = document.getElementById('admin-user-email').value.trim();
    const password = document.getElementById('admin-user-password').value;
    const role = document.getElementById('admin-user-role').value;
    
    try {
        const response = await apiCall('/admin/users', {
            method: 'POST',
            body: JSON.stringify({ callsign, email, password, role })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            hideCreateUserForm();
            loadSysopUsers();
        } else {
            showMessage(data.error || 'Failed to create user', 'error');
        }
    } catch (error) {
        showMessage('Failed to create user', 'error');
    }
}

async function editUser(userId) {
    const newRole = prompt('Enter new role (user/contestadmin/logadmin/sysop):');
    if (!newRole || !['user', 'contestadmin', 'logadmin', 'sysop'].includes(newRole)) {
        if (newRole) showMessage('Invalid role', 'error');
        return;
    }
    
    try {
        const response = await apiCall(`/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify({ role: newRole })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            loadSysopUsers();
        } else {
            showMessage(data.error || 'Failed to update user', 'error');
        }
    } catch (error) {
        showMessage('Failed to update user', 'error');
    }
}

async function deleteUser(userId, callsign) {
    if (!confirm(`Are you sure you want to delete user ${callsign} and ALL their logs? This cannot be undone!`)) {
        return;
    }
    
    try {
        const response = await apiCall(`/admin/users/${userId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'success');
            loadSysopUsers();
        } else {
            showMessage(data.error || 'Failed to delete user', 'error');
        }
    } catch (error) {
        showMessage('Failed to delete user', 'error');
    }
}

// Make functions globally accessible for onclick handlers
window.loadLogs = loadLogs;
window.deleteAPIKey = deleteAPIKey;
window.viewUserLogs = viewUserLogs;
window.resetUserLogs = resetUserLogs;
window.editUser = editUser;
window.deleteUser = deleteUser;
