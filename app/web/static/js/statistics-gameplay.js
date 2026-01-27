/**
 * Statistics Gameplay Page JavaScript
 * Handles Plotly charts for game usage metrics with real API data
 */

// ============================================
// Color Palette (matching the organic/natural design)
// ============================================
const COLORS = {
    olive: '#6B8E3A',
    oliveDark: '#4A5D23',
    lime: '#B8C74A',
    limeLight: '#D4E15A',
    brown: '#8B6F47',
    yellow: '#E8C74A',
    beige: '#F5F3E8',
    text: '#2D3B1C',
    textSecondary: '#6B7A5C'
};

// ============================================
// API Configuration
// ============================================
const API_BASE = '/api/statistics/gameplay';

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

    document.addEventListener('click', (event) => {
        if (!event.target.closest('.navbar')) {
            navbarMenu.classList.remove('active');
        }
    });
}

// ============================================
// Loading State Management
// ============================================

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

// Add spinner animation
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
// API Functions
// ============================================

async function fetchSummary() {
    try {
        const response = await fetch(`${API_BASE}/summary`);
        if (!response.ok) throw new Error('Failed to fetch summary');
        return await response.json();
    } catch (error) {
        console.error('Error fetching summary:', error);
        showErrorInSummaryCards();
        return null;
    }
}

function showErrorInSummaryCards() {
    ['partidasActivasValue', 'completionRateValue', 'eventosCompletadosValue', 'tiempoPromedioValue'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = '--';
    });
}

async function fetchPartidasByDay(days = 30) {
    try {
        const response = await fetch(`${API_BASE}/partidas-by-day?days=${days}`);
        if (!response.ok) throw new Error('Failed to fetch partidas by day');
        return await response.json();
    } catch (error) {
        console.error('Error fetching partidas by day:', error);
        return null;
    }
}

async function fetchPartidasByStatus() {
    try {
        const response = await fetch(`${API_BASE}/partidas-by-status`);
        if (!response.ok) throw new Error('Failed to fetch partidas by status');
        return await response.json();
    } catch (error) {
        console.error('Error fetching partidas by status:', error);
        return null;
    }
}

async function fetchEventosByStatusTimeline(days = 30) {
    try {
        const response = await fetch(`${API_BASE}/eventos-by-status-timeline?days=${days}`);
        if (!response.ok) throw new Error('Failed to fetch eventos timeline');
        return await response.json();
    } catch (error) {
        console.error('Error fetching eventos timeline:', error);
        return null;
    }
}

async function fetchCompletionRateByActivity() {
    try {
        const response = await fetch(`${API_BASE}/completion-rate-by-activity`);
        if (!response.ok) throw new Error('Failed to fetch completion rate by activity');
        return await response.json();
    } catch (error) {
        console.error('Error fetching completion rate by activity:', error);
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
// Chart 1: Partidas creadas por día - Barras
// ============================================
async function initChartPartidasDia() {
    const chartId = 'chartPartidasDia';
    showLoading(chartId);

    const apiData = await fetchPartidasByDay(currentDays);
    if (!apiData) {
        showError(chartId, 'Error al cargar partidas');
        return;
    }

    const { dates, counts } = apiData;

    const data = [{
        x: dates,
        y: counts,
        type: 'bar',
        name: 'Partidas',
        marker: {
            color: counts.map((val, i) => {
                const ratio = i / counts.length;
                return `rgba(107, 142, 58, ${0.5 + ratio * 0.5})`;
            }),
            line: { width: 0 }
        },
        hovertemplate: '<b>Partidas Creadas</b><br>%{x}<br>%{y} partidas<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        showlegend: false,
        bargap: 0.35,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Partidas', font: { size: 12 } }
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
// Chart 2: Partidas completadas vs abandonadas - Donut
// ============================================
async function initChartPartidasDonut() {
    const chartId = 'chartPartidasDonut';
    showLoading(chartId);

    const apiData = await fetchPartidasByStatus();
    if (!apiData) {
        showError(chartId, 'Error al cargar estados');
        return;
    }

    const { completadas, abandonadas, en_progreso, total } = apiData;

    const data = [{
        values: [completadas, abandonadas, en_progreso],
        labels: ['Completadas', 'Abandonadas', 'En Progreso'],
        type: 'pie',
        hole: 0.6,
        marker: {
            colors: [COLORS.olive, COLORS.brown, COLORS.lime]
        },
        textinfo: 'percent',
        textposition: 'outside',
        textfont: {
            family: 'Inter, sans-serif',
            size: 12
        },
        hovertemplate: '<b>%{label}</b><br>%{value} partidas<br>%{percent}<extra></extra>'
    }];

    const layout = {
        margin: { t: 30, r: 30, b: 30, l: 30 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: {
            family: 'Inter, sans-serif',
            color: COLORS.text
        },
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.1,
            x: 0.5,
            xanchor: 'center',
            font: { size: 11 }
        },
        annotations: [{
            text: `<b>${total}</b><br>Total`,
            font: { size: 16, color: COLORS.text },
            showarrow: false,
            x: 0.5,
            y: 0.5
        }]
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 3: Eventos iniciados vs completados - Barras apiladas
// ============================================
async function initChartEventosStack() {
    const chartId = 'chartEventosStack';
    showLoading(chartId);

    const apiData = await fetchEventosByStatusTimeline(currentDays);
    if (!apiData) {
        showError(chartId, 'Error al cargar eventos');
        return;
    }

    const { dates, completados, en_progreso, abandonados } = apiData;

    const data = [
        {
            x: dates,
            y: completados,
            type: 'bar',
            name: 'Completados',
            marker: { color: COLORS.olive },
            hovertemplate: '<b>Completados</b><br>%{x}<br>%{y} eventos<extra></extra>'
        },
        {
            x: dates,
            y: en_progreso,
            type: 'bar',
            name: 'En Progreso',
            marker: { color: COLORS.lime },
            hovertemplate: '<b>En Progreso</b><br>%{x}<br>%{y} eventos<extra></extra>'
        },
        {
            x: dates,
            y: abandonados,
            type: 'bar',
            name: 'Abandonados',
            marker: { color: COLORS.yellow },
            hovertemplate: '<b>Abandonados</b><br>%{x}<br>%{y} eventos<extra></extra>'
        }
    ];

    const layout = {
        ...commonLayout,
        barmode: 'stack',
        showlegend: false,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Eventos', font: { size: 12 } }
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
// Chart 4: Completion Rate por Actividad - Barras Horizontales
// ============================================
async function initChartCompletionRate() {
    const chartId = 'chartCompletionRate';
    showLoading(chartId);

    const apiData = await fetchCompletionRateByActivity();
    if (!apiData) {
        showError(chartId, 'Error al cargar completion rate');
        return;
    }

    const { activities, rates } = apiData;

    const data = [{
        y: activities,
        x: rates,
        type: 'bar',
        orientation: 'h',
        name: 'Completion Rate',
        marker: {
            color: rates.map(rate => {
                if (rate >= 80) return COLORS.olive;
                if (rate >= 60) return COLORS.lime;
                if (rate >= 40) return COLORS.yellow;
                return COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: rates.map(r => `${r.toFixed(1)}%`),
        textposition: 'outside',
        textfont: {
            family: 'Inter, sans-serif',
            size: 11,
            color: COLORS.text
        },
        hovertemplate: '<b>%{y}</b><br>%{x:.1f}% completado<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        showlegend: false,
        margin: { t: 20, r: 60, b: 50, l: 180 },
        xaxis: {
            ...commonLayout.xaxis,
            title: { text: 'Completion Rate (%)', font: { size: 12 } },
            range: [0, 100]
        },
        yaxis: {
            ...commonLayout.yaxis,
            automargin: true
        },
        height: 400
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
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const range = btn.dataset.range;
            const daysMap = {
                '7d': 7,
                '30d': 30,
                '90d': 90,
                '1y': 365
            };

            currentDays = daysMap[range] || 30;
            console.log(`Filter changed to: ${currentDays} days`);

            // Reinitialize time-based charts (not completion rate)
            await Promise.all([
                initChartPartidasDia(),
                initChartEventosStack()
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

    const partidasActivasEl = document.getElementById('partidasActivasValue');
    if (partidasActivasEl) animateValue(partidasActivasEl, 0, summary.partidas_en_progreso, 1500);

    const completionRateEl = document.getElementById('completionRateValue');
    if (completionRateEl) {
        const rate = summary.partidas_completadas && summary.total_partidas
            ? (summary.partidas_completadas / summary.total_partidas * 100).toFixed(1)
            : 0;
        animateValue(completionRateEl, 0, parseFloat(rate), 1200, '%');
    }

    const eventosEl = document.getElementById('eventosCompletadosValue');
    if (eventosEl) animateValue(eventosEl, 0, summary.eventos_completados || 0, 1300);

    const tiempoPromedioEl = document.getElementById('tiempoPromedioValue');
    if (tiempoPromedioEl) animateValue(tiempoPromedioEl, 0, summary.duracion_promedio, 1400, ' min');
}

// ============================================
// Window Resize Handler
// ============================================
function handleResize() {
    const charts = ['chartPartidasDia', 'chartPartidasDonut', 'chartEventosStack', 'chartCompletionRate'];
    charts.forEach(chartId => {
        const chartEl = document.getElementById(chartId);
        if (chartEl && chartEl.data) {
            Plotly.Plots.resize(chartEl);
        }
    });
}

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
    console.log('Gameplay statistics page initialized');

    if (typeof Plotly !== 'undefined') {
        await Promise.all([
            initChartPartidasDia(),
            initChartPartidasDonut(),
            initChartEventosStack(),
            initChartCompletionRate()
        ]);
    } else {
        console.error('Plotly is not loaded');
    }

    initTimeFilter();
    await updateSummaryCards();
    window.addEventListener('resize', debounce(handleResize, 250));
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
