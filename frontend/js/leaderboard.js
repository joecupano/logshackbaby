// Leaderboard JavaScript

const CONTEST_API_BASE = 'http://localhost:5001/api';
const APP_API_BASE = 'http://localhost:5000/api';

let currentUser = null;
let contests = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    await loadContests();
    
    // Check if a specific contest is requested via URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const contestId = urlParams.get('contest');
    if (contestId) {
        document.getElementById('contestSelect').value = contestId;
        await loadLeaderboard();
    }
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

        // Show contest management link for contestadmin and higher
        if (currentUser.role === 'contestadmin' || currentUser.role === 'logadmin' || currentUser.role === 'sysop') {
            document.getElementById('contestManageLink').style.display = 'inline';
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

        contests = await response.json();
        
        if (contests.length === 0) {
            document.getElementById('emptyState').style.display = 'block';
            document.querySelector('.contest-selector').style.display = 'none';
            return;
        }

        // Populate contest selector
        const select = document.getElementById('contestSelect');
        select.innerHTML = '<option value="">Select a contest...</option>' +
            contests.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');
    } catch (error) {
        console.error('Error loading contests:', error);
        document.getElementById('emptyState').style.display = 'block';
        document.querySelector('.contest-selector').style.display = 'none';
    }
}

async function loadLeaderboard() {
    const contestId = document.getElementById('contestSelect').value;
    
    if (!contestId) {
        document.getElementById('leaderboardContainer').style.display = 'none';
        return;
    }

    const contest = contests.find(c => c.id == contestId);
    if (!contest) return;

    // Show contest info
    document.getElementById('contestName').textContent = contest.name;
    document.getElementById('contestDescription').textContent = contest.description || 'No description available';
    document.getElementById('contestDates').textContent = 
        `${formatDate(contest.start_date)} to ${formatDate(contest.end_date)}`;
    document.getElementById('leaderboardContainer').style.display = 'block';

    // Load leaderboard data
    const sessionToken = localStorage.getItem('sessionToken');
    
    try {
        const response = await fetch(`${CONTEST_API_BASE}/contests/${contestId}/leaderboard`, {
            headers: {
                'X-Session-Token': sessionToken
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load leaderboard');
        }

        const data = await response.json();
        displayLeaderboard(data.leaderboard, contestId);
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        document.getElementById('leaderboardBody').innerHTML = 
            '<tr><td colspan="4" class="empty-state">Error loading leaderboard</td></tr>';
    }
}

function displayLeaderboard(leaderboard, contestId) {
    const tbody = document.getElementById('leaderboardBody');
    
    if (leaderboard.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No entries yet</td></tr>';
        return;
    }

    tbody.innerHTML = leaderboard.map((entry, index) => {
        let rankClass = '';
        let medal = '';
        
        if (entry.rank === 1) {
            rankClass = 'rank-1';
            medal = '<span class="medal">🥇</span>';
        } else if (entry.rank === 2) {
            rankClass = 'rank-2';
            medal = '<span class="medal">🥈</span>';
        } else if (entry.rank === 3) {
            rankClass = 'rank-3';
            medal = '<span class="medal">🥉</span>';
        }

        return `
            <tr class="${rankClass}" onclick="showDetails(${contestId}, ${entry.user_id}, '${escapeHtml(entry.callsign)}')">
                <td>${medal}${entry.rank}</td>
                <td><strong>${escapeHtml(entry.callsign)}</strong></td>
                <td>${entry.qso_count}</td>
                <td>${entry.total_points.toFixed(1)}</td>
            </tr>
        `;
    }).join('');
}

async function showDetails(contestId, userId, callsign) {
    const sessionToken = localStorage.getItem('sessionToken');
    
    try {
        const response = await fetch(`${CONTEST_API_BASE}/contests/${contestId}/leaderboard/${userId}`, {
            headers: {
                'X-Session-Token': sessionToken
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load details');
        }

        const data = await response.json();
        
        document.getElementById('detailCallsign').textContent = callsign;
        document.getElementById('detailQsoCount').textContent = data.qso_count;
        document.getElementById('detailTotalPoints').textContent = data.total_points.toFixed(1);
        
        const qsoList = document.getElementById('detailQsoList');
        if (data.entries.length === 0) {
            qsoList.innerHTML = '<p class="empty-state">No QSOs found</p>';
        } else {
            qsoList.innerHTML = `
                <div style="font-weight: bold; padding: 10px; border-bottom: 2px solid #ddd;" class="qso-item">
                    <div>Date/Time</div>
                    <div>Call</div>
                    <div>Band</div>
                    <div>Mode</div>
                    <div>Points</div>
                </div>
            ` + data.entries.map(entry => `
                <div class="qso-item">
                    <div>${formatQSODateTime(entry.qso_date, entry.time_on)}</div>
                    <div><strong>${escapeHtml(entry.call)}</strong></div>
                    <div>${escapeHtml(entry.band || 'N/A')}</div>
                    <div>${escapeHtml(entry.mode || 'N/A')}</div>
                    <div>${entry.points.toFixed(1)}</div>
                </div>
            `).join('');
        }
        
        document.getElementById('detailModal').style.display = 'block';
    } catch (error) {
        console.error('Error loading details:', error);
        alert('Failed to load contest details');
    }
}

function closeDetailModal() {
    document.getElementById('detailModal').style.display = 'none';
}

function logout() {
    localStorage.removeItem('sessionToken');
    window.location.href = 'index.html';
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function formatQSODateTime(date, time) {
    // date format: YYYYMMDD, time format: HHMMSS
    const year = date.substring(0, 4);
    const month = date.substring(4, 6);
    const day = date.substring(6, 8);
    const hour = time.substring(0, 2);
    const minute = time.substring(2, 4);
    
    return `${year}-${month}-${day} ${hour}:${minute}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('detailModal');
    if (event.target === modal) {
        closeDetailModal();
    }
}
