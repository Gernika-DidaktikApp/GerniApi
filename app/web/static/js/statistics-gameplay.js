/**
 * Statistics Gameplay Page JavaScript
 * Handles Plotly charts for game usage metrics with real API data
 *
 * Dependencies: core-utils.js, api-utils.js, ui-utils.js, plotly-utils.js
 */

// ============================================
// API Configuration
// ============================================
const API_BASE = '/api/v1/statistics/gameplay';

// Current time range (days)
let currentDays = 7;

// ============================================
// API Functions
// ============================================

async function fetchSummary() {
    try {
        return await window.apiFetch(`${API_BASE}/summary`);
    } catch (error) {
        logger.log('error', 'Error fetching summary:', error);
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
        return await window.apiFetch(`${API_BASE}/partidas-by-day?days=${days}`);
    } catch (error) {
        logger.log('error', 'Error fetching partidas by day:', error);
        return null;
    }
}

async function fetchPartidasByStatus() {
    try {
        return await window.apiFetch(`${API_BASE}/partidas-by-status`);
    } catch (error) {
        logger.log('error', 'Error fetching partidas by status:', error);
        return null;
    }
}

async function fetchActividadesByStatusTimeline(days = 30) {
    try {
        return await window.apiFetch(`${API_BASE}/actividades-by-status-timeline?days=${days}`);
    } catch (error) {
        logger.log('error', 'Error fetching actividades timeline:', error);
        return null;
    }
}

async function fetchMostPlayedActivities() {
    try {
        return await window.apiFetch(`${API_BASE}/most-played-activities?limit=10`);
    } catch (error) {
        return null;
    }
}

// ============================================
// Chart 1: Partidas creadas por día - Barras
// ============================================
async function initChartPartidasDia() {
    const chartId = 'chartPartidasDia';
    window.showLoading(chartId);

    const apiData = await fetchPartidasByDay(currentDays);
    if (!apiData) {
        window.showError(chartId, 'Error al cargar partidas');
        return;
    }

    const { dates, counts } = apiData;

    if (!dates || dates.length === 0) {
        window.showEmpty(chartId, 'No hay datos de partidas');
        return;
    }

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

    const layout = window.getCommonPlotlyLayout({
        showlegend: false,
        bargap: 0.35,
        yaxis: {
            
            title: { text: 'Partidas', font: { size: 12 } }
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
// Chart 2: Partidas completadas vs abandonadas - Donut
// ============================================
async function initChartPartidasDonut() {
    const chartId = 'chartPartidasDonut';
    window.showLoading(chartId);

    const apiData = await fetchPartidasByStatus();
    if (!apiData) {
        window.showError(chartId, 'Error al cargar estados');
        return;
    }

    const { completadas, abandonadas, en_progreso, total } = apiData;

    if (total === 0) {
        window.showEmpty(chartId, 'No hay partidas registradas');
        return;
    }

    const data = [{
        values: [completadas, abandonadas, en_progreso],
        labels: ['Completadas', 'Abandonadas', 'En Progreso'],
        type: 'pie',
        hole: 0.6,
        marker: {
            colors: [window.CHART_COLORS.olive, window.CHART_COLORS.brown, window.CHART_COLORS.lime]
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
            color: window.CHART_COLORS.text
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
            font: { size: 16, color: window.CHART_COLORS.text },
            showarrow: false,
            x: 0.5,
            y: 0.5
        }]
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, window.getCommonPlotlyConfig());
}

// ============================================
// Chart 3: Actividades iniciadas vs completadas - Barras apiladas
// ============================================
async function initChartEventosStack() {
    const chartId = 'chartEventosStack';
    window.showLoading(chartId);

    const apiData = await fetchActividadesByStatusTimeline(currentDays);
    if (!apiData) {
        window.showError(chartId, 'Error al cargar actividades');
        return;
    }

    const { dates, completados, en_progreso, abandonados } = apiData;

    if (!dates || dates.length === 0) {
        window.showEmpty(chartId, 'No hay datos de actividades');
        return;
    }

    const data = [
        {
            x: dates,
            y: completados,
            type: 'bar',
            name: 'Completados',
            marker: { color: window.CHART_COLORS.olive },
            hovertemplate: '<b>Completados</b><br>%{x}<br>%{y} actividades<extra></extra>'
        },
        {
            x: dates,
            y: en_progreso,
            type: 'bar',
            name: 'En Progreso',
            marker: { color: window.CHART_COLORS.lime },
            hovertemplate: '<b>En Progreso</b><br>%{x}<br>%{y} actividades<extra></extra>'
        },
        {
            x: dates,
            y: abandonados,
            type: 'bar',
            name: 'Abandonados',
            marker: { color: window.CHART_COLORS.yellow },
            hovertemplate: '<b>Abandonados</b><br>%{x}<br>%{y} actividades<extra></extra>'
        }
    ];

    const layout = window.getCommonPlotlyLayout({
        barmode: 'stack',
        showlegend: false,
        yaxis: {
            
            title: { text: 'Actividades', font: { size: 12 } }
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
// Chart 4: Actividades Más Jugadas - Barras Horizontales
// ============================================
async function initChartMostPlayed() {
    const chartId = 'chartMostPlayed';
    window.showLoading(chartId);

    const apiData = await fetchMostPlayedActivities();
    if (!apiData) {
        window.showError(chartId, 'Error al cargar actividades más jugadas');
        return;
    }

    const { activities, counts } = apiData;

    if (!activities || activities.length === 0) {
        window.showEmpty(chartId, 'No hay datos de actividades jugadas');
        return;
    }

    // Find max count for color gradient
    const maxCount = Math.max(...counts);

    const data = [{
        y: activities,
        x: counts,
        type: 'bar',
        orientation: 'h',
        name: 'Veces Jugadas',
        marker: {
            color: counts.map(count => {
                const ratio = count / maxCount;
                if (ratio >= 0.8) return window.CHART_COLORS.olive;
                if (ratio >= 0.6) return window.CHART_COLORS.lime;
                if (ratio >= 0.4) return window.CHART_COLORS.yellow;
                return window.CHART_COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: counts.map(c => c),
        textposition: 'outside',
        textfont: {
            family: 'Inter, sans-serif',
            size: 11,
            color: window.CHART_COLORS.text
        },
        hovertemplate: '<b>%{y}</b><br>%{x} veces jugada<extra></extra>'
    }];

    const layout = window.getCommonPlotlyLayout({
        showlegend: false,
        margin: { t: 20, r: 60, b: 50, l: 180 },
        xaxis: {
            
            title: { text: 'Veces Jugadas', font: { size: 12 } }
        },
        yaxis: {
            
            automargin: true
        },
        height: 400
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
// Update Summary Cards
// ============================================
async function updateSummaryCards() {
    const summary = await fetchSummary();
    if (!summary) return;

    const partidasActivasEl = document.getElementById('partidasActivasValue');
    if (partidasActivasEl) window.animateValue(partidasActivasEl, 0, summary.partidas_en_progreso, 1500);

    const completionRateEl = document.getElementById('completionRateValue');
    if (completionRateEl) {
        const rate = summary.partidas_completadas && summary.total_partidas
            ? (summary.partidas_completadas / summary.total_partidas * 100).toFixed(1)
            : 0;
        window.animateValue(completionRateEl, 0, parseFloat(rate), 1200, '%');
    }

    const eventosEl = document.getElementById('eventosCompletadosValue');
    if (eventosEl) window.animateValue(eventosEl, 0, summary.eventos_completados || 0, 1300);

    const tiempoPromedioEl = document.getElementById('tiempoPromedioValue');
    if (tiempoPromedioEl) window.animateValue(tiempoPromedioEl, 0, summary.duracion_promedio, 1400, ' min');
}

// ============================================
// Window Resize Handler
// ============================================
function handleResize() {
    const charts = ['chartPartidasDia', 'chartPartidasDonut', 'chartEventosStack', 'chartMostPlayed'];
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
    console.log('Gameplay statistics page initialized');

    if (typeof Plotly !== 'undefined') {
        await Promise.all([
            initChartPartidasDia(),
            initChartPartidasDonut(),
            initChartEventosStack(),
            initChartMostPlayed()
        ]);
    } else {
        logger.log('error', 'Plotly is not loaded');
    }

    initTimeFilter();
    await updateSummaryCards();
    window.addEventListener('resize', window.debounce(handleResize, 250));
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
