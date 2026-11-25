let isSoundMuted = false;
let itemsChart = null;

document.addEventListener('DOMContentLoaded', () => {
    // Sound toggle listener
    const soundBtn = document.getElementById('sound-btn');
    if (soundBtn) {
        soundBtn.addEventListener('click', () => {
            isSoundMuted = !isSoundMuted;
            soundBtn.classList.toggle('muted', isSoundMuted);
            soundBtn.innerHTML = isSoundMuted ? '<i class="fa-solid fa-volume-xmark"></i>' : '<i class="fa-solid fa-volume-high"></i>';
        });
    }

    // Initialize Chart and fetch data
    initChart();
    fetchDashboardData();
    
    // Auto-refresh stats every 10 seconds
    setInterval(fetchDashboardData, 10000);
});

// Play subtle web audio API sound effects
function playSound(type = 'pop') {
    if (isSoundMuted) return;
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        if (type === 'out') {
            osc.frequency.setValueAtTime(440, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.1);
            gain.gain.setValueAtTime(0.1, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
            osc.start();
            osc.stop(ctx.currentTime + 0.1);
        } else if (type === 'in') {
            osc.frequency.setValueAtTime(600, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.15);
            gain.gain.setValueAtTime(0.12, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
            osc.start();
            osc.stop(ctx.currentTime + 0.15);
        }
    } catch (e) {
        // AudioContext disabled or unsupported
    }
}

function scrollToSection(id) {
    const el = document.getElementById(id);
    if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
    }
}

// --- Chat Simulator Functions ---
function sendQuickMessage(text) {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.value = text;
        handleChatSubmit(new Event('submit'));
    }
}

async function handleChatSubmit(e) {
    if (e) e.preventDefault();
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    // Clear input
    input.value = '';

    // Append outgoing message
    appendChatMessage(text, 'out');
    playSound('out');

    // Append typing indicator
    const typingId = appendTypingIndicator();

    try {
        const response = await fetch('/api/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, sender: 'whatsapp:+923001234567' })
        });
        
        const data = await response.json();
        removeTypingIndicator(typingId);

        if (data.status === 'success') {
            appendChatMessage(data.reply, 'in');
            playSound('in');
            renderTable(data.records);
            fetchDashboardStats();
        } else {
            appendChatMessage('❌ Error processing request.', 'in');
        }
    } catch (err) {
        removeTypingIndicator(typingId);
        // Fallback offline simulator if backend Flask API isn't responding
        handleOfflineSimulate(text);
    }
}

function appendChatMessage(text, direction) {
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${direction}`;
    
    // Format basic markdown like *bold* or `code`
    let formatted = text
        .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');

    msgDiv.innerHTML = formatted;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function appendTypingIndicator() {
    const chatContainer = document.getElementById('chat-container');
    const id = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = id;
    typingDiv.className = 'message in';
    typingDiv.style.opacity = '0.7';
    typingDiv.innerHTML = '<em>Bot is typing...</em>';
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Offline fallback simulator if server API is down
function handleOfflineSimulate(text) {
    setTimeout(() => {
        appendChatMessage("✅ [Simulator Local] Recorded: " + text, 'in');
        playSound('in');
    }, 600);
}

// --- Dashboard & Analytics Data Engine ---
async function fetchDashboardData() {
    await fetchDashboardStats();
    await fetchDashboardRecords();
}

async function fetchDashboardRecords() {
    try {
        const res = await fetch('/api/records');
        const data = await res.json();
        if (data.status === 'success') {
            renderTable(data.records);
            
            // Update tag if Google Sheets connected
            const tag = document.getElementById('sync-mode-tag');
            if (tag) {
                if (data.google_sheets_connected) {
                    tag.innerHTML = 'Google Sheets Synced 🟢';
                    tag.style.background = 'rgba(16, 185, 129, 0.15)';
                    tag.style.color = 'var(--accent-green)';
                } else {
                    tag.innerHTML = 'SQLite Local Mode 🟡';
                }
            }
        }
    } catch (e) {
        console.log('Unable to reach /api/records');
    }
}

async function fetchDashboardStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        if (data.status === 'success') {
            document.getElementById('stat-sales-count').innerText = `${data.total_sales_count} units`;
            document.getElementById('stat-gross-revenue').innerText = `PKR ${data.gross_revenue.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('stat-expenses').innerText = `PKR ${data.expenses.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            
            const netElem = document.getElementById('stat-net-profit');
            netElem.innerText = `PKR ${data.net_profit.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            netElem.style.color = data.net_profit >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';

            // Update Chart
            updateChart(data.top_items);
        }
    } catch (e) {
        console.log('Unable to reach /api/stats');
    }
}

function renderTable(records) {
    const tbody = document.getElementById('table-body');
    if (!tbody) return;

    if (!records || records.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-msg">No transactions recorded yet. Send a message in the simulator above!</td></tr>';
        return;
    }

    tbody.innerHTML = records.map(r => {
        const isSale = r.type === 'Sale';
        const badgeClass = isSale ? 'type-badge sale' : 'type-badge expense';
        return `
            <tr>
                <td>#${r.id}</td>
                <td>${r.timestamp}</td>
                <td><code>${r.sender}</code></td>
                <td><span class="${badgeClass}">${r.type}</span></td>
                <td><strong>${r.item}</strong></td>
                <td>${r.quantity}</td>
                <td>PKR ${r.unit_price ? r.unit_price.toLocaleString() : '0.00'}</td>
                <td><strong>PKR ${r.total_price ? r.total_price.toLocaleString() : '0.00'}</strong></td>
            </tr>
        `;
    }).join('');
}

// Seed & Clear Controls
async function seedSampleData() {
    try {
        const res = await fetch('/api/seed', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
            renderTable(data.records);
            fetchDashboardStats();
            appendChatMessage("🌱 Demo sample dataset loaded!", 'in');
        }
    } catch (e) {
        alert("Failed to seed sample data.");
    }
}

async function clearData() {
    if (!confirm("Are you sure you want to reset all transaction history?")) return;
    try {
        const res = await fetch('/api/clear', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
            renderTable([]);
            fetchDashboardStats();
            appendChatMessage("🧹 Database cleared for clean demo.", 'in');
        }
    } catch (e) {
        alert("Failed to clear database.");
    }
}

// Chart.js Visualization
function initChart() {
    const ctx = document.getElementById('topItemsChart');
    if (!ctx) return;

    itemsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['No Data Yet'],
            datasets: [{
                label: 'Quantity Sold',
                data: [0],
                backgroundColor: [
                    'rgba(0, 210, 255, 0.7)',
                    'rgba(37, 211, 102, 0.7)',
                    'rgba(168, 85, 247, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(239, 68, 68, 0.7)'
                ],
                borderColor: [
                    '#00d2ff',
                    '#25D366',
                    '#a855f7',
                    '#f59e0b',
                    '#ef4444'
                ],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', precision: 0 },
                    beginAtZero: true
                }
            }
        }
    });
}

function updateChart(topItems) {
    if (!itemsChart) return;
    if (!topItems || topItems.length === 0) {
        itemsChart.data.labels = ['No Data Yet'];
        itemsChart.data.datasets[0].data = [0];
    } else {
        itemsChart.data.labels = topItems.map(item => item[0]);
        itemsChart.data.datasets[0].data = topItems.map(item => item[1]);
    }
    itemsChart.update();
}
