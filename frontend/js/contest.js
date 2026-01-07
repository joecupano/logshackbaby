// Contest Management JavaScript

const CONTEST_API_BASE = 'http://localhost:5001/api';
const APP_API_BASE = 'http://localhost:5000/api';

let currentUser = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    await loadContests();
    
    // Setup form submission
    document.getElementById('contestForm').addEventListener('submit', handleFormSubmit);
});

async function checkAuth() {
    const sessionToken = localStorage.getItem('sessionToken');
    if (!sessionToken) {
        window.location.href = 'index.html';
        return;
    }

    try {
        // Get current user info from main app
        const response = await fetch(`${APP_API_BASE}/auth/me`, {
            headers: {
                'X-Session-Token': sessionToken
            }
        });

        if (!response.ok) {
            localStorage.removeItem('sessionToken');
            window.location.href = 'index.html';
            return;
        }

        currentUser = await response.json();
        document.getElementById('userCallsign').textContent = currentUser.callsign;

        // Check if user has contestadmin role
        if (currentUser.role !== 'contestadmin' && currentUser.role !== 'logadmin' && currentUser.role !== 'sysop') {
            document.getElementById('contestManagement').style.display = 'none';
            document.getElementById('accessDenied').style.display = 'block';
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = 'index.html';
    }
}

async function loadContests() {
    const sessionToken = localStorage.getItem('sessionToken');
    
    try {
        const response = await fetch(`${CONTEST_API_BASE}/contests`, {
            headers: {
                'X-Session-Token': sessionToken
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load contests');
        }

        const contests = await response.json();
        displayContests(contests);
    } catch (error) {
        console.error('Error loading contests:', error);
        document.getElementById('contestList').innerHTML = '<p>Error loading contests</p>';
    }
}

function displayContests(contests) {
    const container = document.getElementById('contestList');
    
    if (contests.length === 0) {
        container.innerHTML = '<p>No contests yet. Create your first contest!</p>';
        return;
    }

    container.innerHTML = contests.map(contest => `
        <div class="contest-card">
            <h3>${escapeHtml(contest.name)}</h3>
            <p>${escapeHtml(contest.description || 'No description')}</p>
            <div class="contest-dates">
                <div>Start: ${formatDate(contest.start_date)}</div>
                <div>End: ${formatDate(contest.end_date)}</div>
            </div>
            <div style="margin-top: 10px;">
                <span class="status-badge ${contest.is_active ? 'status-active' : 'status-inactive'}">
                    ${contest.is_active ? 'Active' : 'Inactive'}
                </span>
            </div>
            <div class="contest-actions">
                <button onclick="populateContest(${contest.id})" class="btn btn-success" style="font-size: 0.9em;">
                    Populate
                </button>
                <button onclick="editContest(${contest.id})" class="btn btn-primary" style="font-size: 0.9em;">
                    Edit
                </button>
                <button onclick="viewLeaderboard(${contest.id})" class="btn btn-secondary" style="font-size: 0.9em;">
                    Leaderboard
                </button>
                <button onclick="deleteContest(${contest.id})" class="btn btn-danger" style="font-size: 0.9em;">
                    Delete
                </button>
            </div>
        </div>
    `).join('');
}

function showCreateModal() {
    document.getElementById('modalTitle').textContent = 'Create New Contest';
    document.getElementById('contestForm').reset();
    document.getElementById('contestId').value = '';
    document.getElementById('contestModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('contestModal').style.display = 'none';
}

async function editContest(contestId) {
    const sessionToken = localStorage.getItem('sessionToken');
    
    try {
        const response = await fetch(`${CONTEST_API_BASE}/contests/${contestId}`, {
            headers: {
                'X-Session-Token': sessionToken
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load contest');
        }

        const contest = await response.json();
        
        // Populate form
        document.getElementById('modalTitle').textContent = 'Edit Contest';
        document.getElementById('contestId').value = contest.id;
        document.getElementById('contestName').value = contest.name;
        document.getElementById('contestDescription').value = contest.description || '';
        document.getElementById('startDate').value = formatDateForInput(contest.start_date);
        document.getElementById('endDate').value = formatDateForInput(contest.end_date);
        document.getElementById('qsoPoints').value = contest.scoring?.qso_points || 1;
        document.getElementById('isActive').value = contest.is_active ? 'true' : 'false';
        
        document.getElementById('contestModal').style.display = 'block';
    } catch (error) {
        console.error('Error loading contest:', error);
        alert('Failed to load contest details');
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const contestId = document.getElementById('contestId').value;
    const formData = {
        name: document.getElementById('contestName').value,
        description: document.getElementById('contestDescription').value,
        start_date: new Date(document.getElementById('startDate').value).toISOString(),
        end_date: new Date(document.getElementById('endDate').value).toISOString(),
        scoring: {
            qso_points: parseFloat(document.getElementById('qsoPoints').value)
        },
        is_active: document.getElementById('isActive').value === 'true'
    };

    const sessionToken = localStorage.getItem('sessionToken');
    const isEdit = !!contestId;
    const url = isEdit ? `${CONTEST_API_BASE}/contests/${contestId}` : `${CONTEST_API_BASE}/contests`;
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-Session-Token': sessionToken
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save contest');
        }

        alert(isEdit ? 'Contest updated successfully!' : 'Contest created successfully!');
        closeModal();
        await loadContests();
    } catch (error) {
        console.error('Error saving contest:', error);
        alert(error.message);
    }
}

async function deleteContest(contestId) {
    if (!confirm('Are you sure you want to delete this contest? This will also delete all entries.')) {
        return;
    }

    const sessionToken = localStorage.getItem('sessionToken');

    try {
        const response = await fetch(`${CONTEST_API_BASE}/contests/${contestId}`, {
            method: 'DELETE',
            headers: {
                'X-Session-Token': sessionToken
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete contest');
        }

        alert('Contest deleted successfully!');
        await loadContests();
    } catch (error) {
        console.error('Error deleting contest:', error);
        alert('Failed to delete contest');
    }
}

async function populateContest(contestId) {
    if (!confirm('This will scan all logs and populate contest entries based on the contest rules. Continue?')) {
        return;
    }

    const sessionToken = localStorage.getItem('sessionToken');

    try {
        const response = await fetch(`${CONTEST_API_BASE}/contests/${contestId}/populate`, {
            method: 'POST',
            headers: {
                'X-Session-Token': sessionToken
            }
        });

        if (!response.ok) {
            throw new Error('Failed to populate contest');
        }

        const result = await response.json();
        alert(`Contest populated! Added ${result.new_entries} new entries. Total: ${result.total_entries}`);
    } catch (error) {
        console.error('Error populating contest:', error);
        alert('Failed to populate contest');
    }
}

function viewLeaderboard(contestId) {
    window.location.href = `leaderboard.html?contest=${contestId}`;
}

function logout() {
    localStorage.removeItem('sessionToken');
    window.location.href = 'index.html';
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatDateForInput(dateString) {
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('contestModal');
    if (event.target === modal) {
        closeModal();
    }
}
