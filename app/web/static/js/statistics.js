/**
 * Statistics Page JavaScript
 * Handles navbar toggle and Plotly chart initialization for user activity metrics
 */

// ============================================
// Color Palette (matching the organic/natural design)
// ============================================
const COLORS = {
    olive: '#6B8E3A',
    oliveDark: '#4A5D23',
    lime: '#B8C74A',
    brown: '#8B6F47',
    beige: '#F5F3E8',
    text: '#2D3B1C',
    textSecondary: '#6B7A5C'
};

// ============================================
// API Configuration
// ============================================
const API_BASE = '/api/statistics/users';

// Current time range (days)
let currentDays = 7;

// ============================================
// Navbar Mobile Menu Toggle
// ============================================
const navbarToggle = document.getElementById('navbarToggle');
const navbarMenu = document.getElementById('navbarMenu');

if (navbarToggle && navbarMenu) {
    navbarToggle.addEventListener('click', () => {
        navbarMenu.classList.toggle('active');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.navbar')) {
            navbarMenu.classList.remove('active');
        }
    });
}

// ============================================
// Loading State Management
// ============================================

/**
 * Show loading spinner on a chart container
 */
function showLoading(chartId) {
    const container = document.getElementById(chartId);
    if (container) {
        container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; min-height: 300px;">
                <div style="text-align: center;">
                    <div style="border: 4px solid #f3f3f3; border-top: 4px solid #6B8E3A; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                    <p style="color: #6B7A5C; margin-top: 1rem; font-size: 0.875rem;">Cargando datos...</p>
                </div>
            </div>
        `;
    }
}

/**
 * Show error message on a chart container
 */
function showError(chartId, message = 'Error al cargar datos') {
    const container = document.getElementById(chartId);
    if (container) {
        container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; min-height: 300px;">
                <div style="text-align: center; color: #dc2626;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin: 0 auto;">
                        <circle cx="12" cy="12" r="10" stroke-width="2"/>
                        <line x1="12" y1="8" x2="12" y2="12" stroke-width="2"/>
                        <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2"/>
                    </svg>
                    <p style="margin-top: 1rem; font-size: 0.875rem;">${message}</p>
                    <button onclick="location.reload()" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: #6B8E3A; color: white; border: none; border-radius: 0.5rem; cursor: pointer;">
                        Reintentar
                    </button>
                </div>
            </div>
        `;
    }
}

// Add spinner animation to the page
if (!document.getElementById('spinner-style')) {
    const style = document.createElement('style');
    style.id = 'spinner-style';
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}

// ============================================
// API Functions with Loading States
// ============================================

/**
 * Fetch summary statistics from API
 */
async function fetchSummary() {
    try {
        const response = await fetch(`${API_BASE}/summary`);
        if (!response.ok) throw new Error('Failed to fetch summary');
        return await response.json();
    } catch (error) {
        console.error('Error fetching summary:', error);
        // Show error in summary cards
        showErrorInSummaryCards();
        return null;
    }
}

function showErrorInSummaryCards() {
    ['dauValue', 'newUsersValue', 'ratioValue', 'loginsValue'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = '--';
    });
}

/**
 * Fetch active users timeline (DAU/WAU/MAU)
 */
async function fetchActiveUsersTimeline(days = 30) {
    try {
        const response = await fetch(`${API_BASE}/active-timeline?days=${days}`);
        if (!response.ok) throw new Error('Failed to fetch active users timeline');
        return await response.json();
    } catch (error) {
        console.error('Error fetching active users timeline:', error);
        return null;
    }
}

/**
 * Fetch new users by day
 */
async function fetchNewUsersByDay(days = 30) {
    try {
        const response = await fetch(`${API_BASE}/new-by-day?days=${days}`);
        if (!response.ok) throw new Error('Failed to fetch new users');
        return await response.json();
    } catch (error) {
        console.error('Error fetching new users:', error);
        return null;
    }
}

/**
 * Fetch active ratio timeline
 */
async function fetchActiveRatioTimeline(days = 30) {
    try {
        const response = await fetch(`${API_BASE}/active-ratio-timeline?days=${days}`);
        if (!response.ok) throw new Error('Failed to fetch ratio timeline');
        return await response.json();
    } catch (error) {
        console.error('Error fetching ratio timeline:', error);
        return null;
    }
}

/**
 * Fetch logins by day
 */
async function fetchLoginsByDay(days = 30) {
    try {
        const response = await fetch(`${API_BASE}/logins-by-day?days=${days}`);
        if (!response.ok) throw new Error('Failed to fetch logins');
        return await response.json();
    } catch (error) {
        console.error('Error fetching logins:', error);
        return null;
    }
}

// ============================================
// Plotly Chart Configuration
// ============================================

const commonLayout = {
    margin: { t: 20, r: 30, b: 50, l: 60 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: {
        family: 'Inter, sans-serif',
        color: COLORS.text
    },
    xaxis: {
        gridcolor: 'rgba(107, 142, 58, 0.08)',
        linecolor: 'rgba(107, 142, 58, 0.15)',
        tickfont: { size: 11 }
    },
    yaxis: {
        gridcolor: 'rgba(107, 142, 58, 0.08)',
        linecolor: 'rgba(107, 142, 58, 0.15)',
        tickfont: { size: 11 }
    },
    hoverlabel: {
        bgcolor: '#FFFFFF',
        bordercolor: COLORS.olive,
        font: { family: 'Inter, sans-serif', color: COLORS.text }
    }
};

const commonConfig = {
    responsive: true,
    displayModeBar: false
};

// ============================================
// Chart 1: Usuarios Activos (DAU / WAU / MAU) - Línea
// ============================================
async function initChartActiveUsers() {
    const chartId = 'chartActiveUsers';
    showLoading(chartId);

    const apiData = await fetchActiveUsersTimeline(currentDays);
    if (!apiData) {
        showError(chartId, 'Error al cargar usuarios activos');
        return;
    }

    const { dates, dau, wau, mau } = apiData;

    const data = [
        {
            x: dates,
            y: dau,
            type: 'scatter',
            mode: 'lines',
            name: 'DAU',
            line: {
                color: COLORS.olive,
                width: 3,
                shape: 'spline'
            },
            hovertemplate: '<b>DAU</b><br>%{x}<br>%{y:,} usuarios<extra></extra>'
        },
        {
            x: dates,
            y: wau,
            type: 'scatter',
            mode: 'lines',
            name: 'WAU',
            line: {
                color: COLORS.lime,
                width: 3,
                shape: 'spline'
            },
            hovertemplate: '<b>WAU</b><br>%{x}<br>%{y:,} usuarios<extra></extra>'
        },
        {
            x: dates,
            y: mau,
            type: 'scatter',
            mode: 'lines',
            name: 'MAU',
            line: {
                color: COLORS.oliveDark,
                width: 3,
                shape: 'spline'
            },
            hovertemplate: '<b>MAU</b><br>%{x}<br>%{y:,} usuarios<extra></extra>'
        }
    ];

    const layout = {
        ...commonLayout,
        showlegend: false,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Usuarios', font: { size: 12 } }
        },
        xaxis: {
            ...commonLayout.xaxis,
            tickformat: '%d %b'
        }
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 2: Nuevos Usuarios por Día - Barras
// ============================================
async function initChartNewUsers() {
    const chartId = 'chartNewUsers';
    showLoading(chartId);

    const apiData = await fetchNewUsersByDay(currentDays);
    if (!apiData) {
        showError(chartId, 'Error al cargar nuevos usuarios');
        return;
    }

    const { dates, counts } = apiData;

    const data = [{
        x: dates,
        y: counts,
        type: 'bar',
        name: 'Nuevos Usuarios',
        marker: {
            color: counts.map((_, i) => {
                const ratio = i / counts.length;
                return `rgba(107, 142, 58, ${0.6 + ratio * 0.4})`;
            }),
            line: {
                color: COLORS.oliveDark,
                width: 0
            }
        },
        hovertemplate: '<b>Nuevos Usuarios</b><br>%{x}<br>%{y} nuevos<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        showlegend: false,
        bargap: 0.3,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Nuevos Usuarios', font: { size: 12 } }
        },
        xaxis: {
            ...commonLayout.xaxis,
            tickformat: '%d %b'
        }
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 3: Ratio Usuarios Activos / Totales - Área
// ============================================
async function initChartRatio() {
    const chartId = 'chartRatio';
    showLoading(chartId);

    const apiData = await fetchActiveRatioTimeline(currentDays);
    if (!apiData) {
        showError(chartId, 'Error al cargar ratio de usuarios');
        return;
    }

    const { dates, ratios } = apiData;

    const data = [{
        x: dates,
        y: ratios,
        type: 'scatter',
        mode: 'lines',
        name: 'Ratio',
        fill: 'tozeroy',
        fillcolor: 'rgba(184, 199, 74, 0.25)',
        line: {
            color: COLORS.lime,
            width: 2.5,
            shape: 'spline'
        },
        hovertemplate: '<b>Ratio Activos/Totales</b><br>%{x}<br>%{y:.1f}%<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        showlegend: false,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Ratio (%)', font: { size: 12 } },
            ticksuffix: '%'
        },
        xaxis: {
            ...commonLayout.xaxis,
            tickformat: '%d %b'
        }
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 4: Logins por Día - Línea con Marcadores
// ============================================
async function initChartLogins() {
    const chartId = 'chartLogins';
    showLoading(chartId);

    const apiData = await fetchLoginsByDay(currentDays);
    if (!apiData) {
        showError(chartId, 'Error al cargar logins');
        return;
    }

    const { dates, counts } = apiData;

    const data = [{
        x: dates,
        y: counts,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Logins',
        line: {
            color: COLORS.brown,
            width: 2.5,
            shape: 'spline'
        },
        marker: {
            color: COLORS.brown,
            size: 6,
            line: {
                color: '#FFFFFF',
                width: 2
            }
        },
        hovertemplate: '<b>Logins</b><br>%{x}<br>%{y:,} sesiones<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        showlegend: false,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Número de Logins', font: { size: 12 } }
        },
        xaxis: {
            ...commonLayout.xaxis,
            tickformat: '%d %b'
        }
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Time Filter Functionality
// ============================================
function initTimeFilter() {
    const filterBtns = document.querySelectorAll('.filter-btn');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');

            // Get the selected range and convert to days
            const range = btn.dataset.range;
            const daysMap = {
                '7d': 7,
                '30d': 30,
                '90d': 90,
                '1y': 365
            };

            currentDays = daysMap[range] || 30;
            console.log(`Filter changed to: ${currentDays} days`);

            // Reinitialize charts with new data range
            await Promise.all([
                initChartActiveUsers(),
                initChartNewUsers(),
                initChartRatio(),
                initChartLogins()
            ]);
        });
    });
}

// ============================================
// Animate Summary Values
// ============================================
function animateValue(element, start, end, duration, suffix = '') {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function (ease-out-cubic)
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (end - start) * eased);

        if (element) {
            element.textContent = current.toLocaleString() + suffix;
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

async function updateSummaryCards() {
    const summary = await fetchSummary();
    if (!summary) return;

    // Animate DAU value
    const dauEl = document.getElementById('dauValue');
    if (dauEl) animateValue(dauEl, 0, summary.dau, 1500);

    // Animate New Users value
    const newUsersEl = document.getElementById('newUsersValue');
    if (newUsersEl) animateValue(newUsersEl, 0, summary.new_users_today, 1200);

    // Animate Ratio value
    const ratioEl = document.getElementById('ratioValue');
    if (ratioEl) animateValue(ratioEl, 0, summary.ratio_active_total, 1300, '%');

    // Animate Logins value
    const loginsEl = document.getElementById('loginsValue');
    if (loginsEl) animateValue(loginsEl, 0, summary.logins_today, 1400);
}

// ============================================
// Window Resize Handler
// ============================================
function handleResize() {
    // Resize all Plotly charts
    const charts = ['chartActiveUsers', 'chartNewUsers', 'chartRatio', 'chartLogins'];
    charts.forEach(chartId => {
        const chartEl = document.getElementById(chartId);
        if (chartEl && chartEl.data) {
            Plotly.Plots.resize(chartEl);
        }
    });
}

// Debounce function for resize
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================
// Initialize
// ============================================
async function init() {
    console.log('Statistics page initialized');

    // Initialize all charts
    if (typeof Plotly !== 'undefined') {
        await Promise.all([
            initChartActiveUsers(),
            initChartNewUsers(),
            initChartRatio(),
            initChartLogins()
        ]);
    } else {
        console.error('Plotly is not loaded');
    }

    // Initialize time filter
    initTimeFilter();

    // Update summary cards with real data
    await updateSummaryCards();

    // Add resize listener
    window.addEventListener('resize', debounce(handleResize, 250));
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
