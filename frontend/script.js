// API Configuration
const API_BASE = '/api';

// State
let currentPage = 'dashboard';
let sidebarCollapsed = false;

// DOM Elements
const sidebar = document.getElementById('sidebar');
const main = document.querySelector('.main');
const content = document.getElementById('content');
const pageTitle = document.getElementById('pageTitle');
const sidebarToggle = document.getElementById('sidebarToggle');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const themeToggle = document.getElementById('themeToggle');
const navItems = document.querySelectorAll('.nav-item');
const modal = document.getElementById('modal');
const apiStatus = document.getElementById('apiStatus');

// ========== INITIALIZATION ==========
async function init() {
    await checkAPIStatus();
    loadPage('dashboard');
    setupEventListeners();
    loadTheme();
}

function setupEventListeners() {
    // Navigation
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            loadPage(page);
            
            navItems.forEach(ni => ni.classList.remove('active'));
            item.classList.add('active');
        });
    });
    
    // Sidebar toggle
    sidebarToggle?.addEventListener('click', toggleSidebar);
    mobileMenuBtn?.addEventListener('click', () => sidebar.classList.add('active'));
    
    // Theme toggle
    themeToggle?.addEventListener('click', toggleTheme);
    
    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !mobileMenuBtn?.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
}

// ========== API CALLS ==========
async function checkAPIStatus() {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        
        const statusDot = apiStatus?.querySelector('.status-dot');
        const statusText = apiStatus?.querySelector('span:last-child');
        
        if (data.success) {
            statusDot?.classList.add('online');
            if (statusText) statusText.textContent = 'API Online';
        } else {
            statusDot?.classList.add('offline');
            if (statusText) statusText.textContent = 'API Offline';
        }
    } catch {
        const statusDot = apiStatus?.querySelector('.status-dot');
        statusDot?.classList.add('offline');
    }
}

async function searchInstagram(username) {
    showLoading();
    try {
        const res = await fetch(`${API_BASE}/ig/profile/${username}`);
        const data = await res.json();
        hideLoading();
        
        if (data.success) {
            displayIGProfile(data.data);
        } else {
            showError(data.error);
        }
    } catch (error) {
        hideLoading();
        showError('Gagal terhubung ke server');
    }
}

async function searchTikTok(username) {
    showLoading();
    try {
        const res = await fetch(`${API_BASE}/tt/profile/${username}`);
        const data = await res.json();
        hideLoading();
        
        if (data.success) {
            displayTTProfile(data.data);
        } else {
            showError(data.error);
        }
    } catch (error) {
        hideLoading();
        showError('Gagal terhubung ke server');
    }
}

// ========== PAGE LOADERS ==========
function loadPage(page) {
    currentPage = page;
    
    const titles = {
        dashboard: 'Dashboard',
        instagram: 'Instagram OSINT',
        tiktok: 'TikTok OSINT',
        compare: 'Compare Profiles',
        batch: 'Batch Processing',
        favorites: 'Favorites',
        history: 'Search History',
        stats: 'Statistics'
    };
    
    pageTitle.textContent = titles[page] || page;
    
    switch(page) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'instagram':
            loadInstagramPage();
            break;
        case 'tiktok':
            loadTikTokPage();
            break;
        case 'compare':
            loadComparePage();
            break;
        case 'batch':
            loadBatchPage();
            break;
        case 'favorites':
            loadFavoritesPage();
            break;
        case 'history':
            loadHistoryPage();
            break;
        case 'stats':
            loadStatsPage();
            break;
    }
}

function loadDashboard() {
    content.innerHTML = `
        <div class="welcome-card card">
            <h2>🔥 El Cienco Stalker Pro</h2>
            <p>Two-in-One OSINT Tool untuk Instagram & TikTok</p>
            <div class="quick-actions">
                <button class="btn" onclick="loadPage('instagram')">
                    <i class="fab fa-instagram"></i> Instagram OSINT
                </button>
                <button class="btn" onclick="loadPage('tiktok')">
                    <i class="fab fa-tiktok"></i> TikTok OSINT
                </button>
            </div>
        </div>
        <div class="stats-grid" id="dashboardStats">
            <!-- Stats will be loaded here -->
        </div>
        <div class="recent-activity card">
            <h3>Recent Activity</h3>
            <div id="recentHistory"></div>
        </div>
    `;
    
    loadDashboardStats();
    loadRecentHistory();
}

function loadInstagramPage() {
    content.innerHTML = `
        <div class="card">
            <h2><i class="fab fa-instagram"></i> Instagram Profile OSINT</h2>
            <p>Masukkan username Instagram untuk mendapatkan informasi lengkap</p>
            
            <div class="search-box">
                <input type="text" id="igUsername" placeholder="Masukkan username (tanpa @)" />
                <button class="btn" onclick="searchIG()">
                    <i class="fas fa-search"></i> Search
                </button>
            </div>
            
            <div id="igResult"></div>
        </div>
        
        <div class="card">
            <h3>Fitur Instagram OSINT</h3>
            <ul class="feature-list">
                <li><i class="fas fa-check"></i> Info profil lengkap</li>
                <li><i class="fas fa-check"></i> Engagement rate analysis</li>
                <li><i class="fas fa-check"></i> Download recent posts</li>
                <li><i class="fas fa-check"></i> Stories viewer (public)</li>
                <li><i class="fas fa-check"></i> Bio keyword analysis</li>
            </ul>
        </div>
    `;
}

// ========== UTILITY FUNCTIONS ==========
function formatNumber(num) {
    if (num >= 1000000) return (num/1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num/1000).toFixed(1) + 'K';
    return num.toString();
}

function showLoading() {
    const loader = document.createElement('div');
    loader.className = 'loading-overlay';
    loader.innerHTML = '<div class="spinner"></div>';
    loader.id = 'globalLoader';
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('globalLoader');
    if (loader) loader.remove();
}

function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast error';
    toast.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast success';
    toast.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ========== GLOBAL FUNCTIONS ==========
window.searchIG = () => {
    const username = document.getElementById('igUsername')?.value.trim();
    if (username) searchInstagram(username);
};

window.searchTT = () => {
    const username = document.getElementById('ttUsername')?.value.trim();
    if (username) searchTikTok(username);
};

window.closeModal = () => {
    modal.classList.remove('active');
};

window.toggleSidebar = () => {
    sidebar.classList.toggle('collapsed');
    main.classList.toggle('expanded');
};

window.toggleTheme = () => {
    document.body.classList.toggle('dark-theme');
    const icon = themeToggle.querySelector('i');
    icon.className = document.body.classList.contains('dark-theme') ? 'fas fa-sun' : 'fas fa-moon';
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
};

// Initialize
init();
