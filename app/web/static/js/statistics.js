/**
 * Statistics Page JavaScript
 * Handles Plotly chart initialization for user activity metrics
 *
 * Dependencies: core-utils.js, api-utils.js, ui-utils.js, plotly-utils.js
 */

// ============================================
// API Configuration
// ============================================
const API_BASE = '/api/statistics/users';

// Current time range (days)
let currentDays = 7;

// ============================================
// API Functions
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
        logger.log('error', 'Error fetching summary', { error: error.message });
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
        logger.log('error', 'Error fetching active users timeline', { error: error.message });
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
        logger.log('error', 'Error fetching new users', { error: error.message });
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
        logger.log('error', 'Error fetching ratio timeline', { error: error.message });
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
        logger.log('error', 'Error fetching logins', { error: error.message });
        return null;
    }
}

// ============================================
// Chart 1: Usuarios Activos (DAU / WAU / MAU) - Línea
// ============================================
async function initChartActiveUsers() {
    const chartId = 'chartActiveUsers';
    window.showLoading(chartId);

    const apiData = await fetchActiveUsersTimeline(currentDays);
    if (!apiData) {
        window.showError(chartId, 'Error al cargar usuarios activos');
        return;
    }

    const { dates, dau, wau, mau } = apiData;

    if (!dates || dates.length === 0) {
        window.showEmpty(chartId, 'No hay datos de usuarios activos');
        return;
    }

    const data = [
        {
            x: dates,
            y: dau,
            type: 'scatter',
            mode: 'lines',
            name: 'DAU',
            line: {
                color: window.CHART_COLORS.olive,
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
                color: window.CHART_COLORS.lime,
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
                color: window.CHART_COLORS.oliveDark,
                width: 3,
                shape: 'spline'
            },
            hovertemplate: '<b>MAU</b><br>%{x}<br>%{y:,} usuarios<extra></extra>'
        }
    ];

    const layout = window.getCommonPlotlyLayout({
        showlegend: false,
        yaxis: {
            title: { text: 'Usuarios', font: { size: 12 } }
        },
        xaxis: {
            tickformat: '%d %b'
        }
    });

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, window.getCommonPlotlyConfig());
}

// ============================================
// Chart 2: Nuevos Usuarios por Día - Barras
// ============================================
async function initChartNewUsers() {
    const chartId = 'chartNewUsers';
    window.showLoading(chartId);

    const apiData = await fetchNewUsersByDay(currentDays);
    if (!apiData) {
        window.showError(chartId, 'Error al cargar nuevos usuarios');
        return;
    }

    const { dates, counts } = apiData;

    if (!dates || dates.length === 0) {
        window.showEmpty(chartId, 'No hay datos de nuevos usuarios');
        return;
    }

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
                color: window.CHART_COLORS.oliveDark,
                width: 0
            }
        },
        hovertemplate: '<b>Nuevos Usuarios</b><br>%{x}<br>%{y} nuevos<extra></extra>'
    }];

    const layout = window.getCommonPlotlyLayout({
        showlegend: false,
        bargap: 0.3,
        yaxis: {
            title: { text: 'Nuevos Usuarios', font: { size: 12 } }
        },
        xaxis: {
            tickformat: '%d %b'
        }
    });

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, window.getCommonPlotlyConfig());
}

// ============================================
// Chart 3: Ratio Usuarios Activos / Totales - Área
// ============================================
async function initChartRatio() {
    const chartId = 'chartRatio';
    window.showLoading(chartId);

    const apiData = await fetchActiveRatioTimeline(currentDays);
    if (!apiData) {
        window.showError(chartId, 'Error al cargar ratio de usuarios');
        return;
    }

    const { dates, ratios } = apiData;

    if (!dates || dates.length === 0) {
        window.showEmpty(chartId, 'No hay datos de ratio de usuarios');
        return;
    }

    const data = [{
        x: dates,
        y: ratios,
        type: 'scatter',
        mode: 'lines',
        name: 'Ratio',
        fill: 'tozeroy',
        fillcolor: 'rgba(184, 199, 74, 0.25)',
        line: {
            color: window.CHART_COLORS.lime,
            width: 2.5,
            shape: 'spline'
        },
        hovertemplate: '<b>Ratio Activos/Totales</b><br>%{x}<br>%{y:.1f}%<extra></extra>'
    }];

    const layout = window.getCommonPlotlyLayout({
        showlegend: false,
        yaxis: {
            title: { text: 'Ratio (%)', font: { size: 12 } },
            ticksuffix: '%'
        },
        xaxis: {
            tickformat: '%d %b'
        }
    });

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, window.getCommonPlotlyConfig());
}

// ============================================
// Chart 4: Logins por Día - Línea con Marcadores
// ============================================
async function initChartLogins() {
    const chartId = 'chartLogins';
    window.showLoading(chartId);

    const apiData = await fetchLoginsByDay(currentDays);
    if (!apiData) {
        window.showError(chartId, 'Error al cargar logins');
        return;
    }

    const { dates, counts } = apiData;

    if (!dates || dates.length === 0) {
        window.showEmpty(chartId, 'No hay datos de logins');
        return;
    }

    const data = [{
        x: dates,
        y: counts,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Logins',
        line: {
            color: window.CHART_COLORS.brown,
            width: 2.5,
            shape: 'spline'
        },
        marker: {
            color: window.CHART_COLORS.brown,
            size: 6,
            line: {
                color: '#FFFFFF',
                width: 2
            }
        },
        hovertemplate: '<b>Logins</b><br>%{x}<br>%{y:,} sesiones<extra></extra>'
    }];

    const layout = window.getCommonPlotlyLayout({
        showlegend: false,
        yaxis: {
            title: { text: 'Número de Logins', font: { size: 12 } }
        },
        xaxis: {
            tickformat: '%d %b'
        }
    });

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, window.getCommonPlotlyConfig());
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
// Update Summary Cards
// ============================================
async function updateSummaryCards() {
    const summary = await fetchSummary();
    if (!summary) return;

    // Animate DAU value
    const dauEl = document.getElementById('dauValue');
    if (dauEl) window.animateValue(dauEl, 0, summary.dau, 1500);

    // Animate New Users value
    const newUsersEl = document.getElementById('newUsersValue');
    if (newUsersEl) window.animateValue(newUsersEl, 0, summary.new_users_today, 1200);

    // Animate Ratio value
    const ratioEl = document.getElementById('ratioValue');
    if (ratioEl) window.animateValue(ratioEl, 0, summary.ratio_active_total, 1300, '%');

    // Animate Logins value
    const loginsEl = document.getElementById('loginsValue');
    if (loginsEl) window.animateValue(loginsEl, 0, summary.logins_today, 1400);
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
    window.addEventListener('resize', window.debounce(handleResize, 250));
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}


