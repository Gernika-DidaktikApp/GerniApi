/**
 * Statistics Learning Page JavaScript
 * Handles Plotly charts for learning and performance metrics
 *
 * Dependencies: core-utils.js, api-utils.js, ui-utils.js, plotly-utils.js
 */

// ============================================
// Color Palette (matching the organic/natural design)
// ============================================
// ============================================
// API Configuration
// ============================================
const API_BASE = '/api/v1/statistics/learning';

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
    ['puntuacionMediaValue', 'aprobadosValue', 'tiempoMedioValue', 'actividadesEvaluadasValue'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = '--';
    });
}

async function fetchMostPlayedActivities() {
    try {
        return await window.apiFetch(`${API_BASE}/most-played-activities?limit=10`);
    } catch (error) {
        return null;
    }
}

async function fetchHighestScoringActivities() {
    try {
        return await window.apiFetch(`${API_BASE}/highest-scoring-activities?limit=10`);
    } catch (error) {
        return null;
    }
}

async function fetchClassPerformance() {
    try {
        return await window.apiFetch(`${API_BASE}/class-performance`);
    } catch (error) {
        return null;
    }
}

// ============================================

// ============================================
// Chart 1: Actividades Más Jugadas - Barras Horizontales
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
        textfont: { size: 11, color: window.CHART_COLORS.text, family: 'Inter, sans-serif' },
        hovertemplate: '<b>%{y}</b><br>%{x} veces jugada<extra></extra>'
    }];

    const layout = window.getCommonPlotlyLayout({
        margin: { t: 20, r: 60, b: 50, l: 180 },
        showlegend: false,
        xaxis: {
            
            title: { text: 'Veces Jugadas', font: { size: 12 } }
        },
        yaxis: {
            
            automargin: true,
            tickfont: { size: 11 }
        },
        height: 400
    });

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, window.getCommonPlotlyConfig());
}

// ============================================
// Chart 2: Actividades con Mayor Puntuación - Barras Horizontales
// ============================================
async function initChartHighestScoring() {
    const chartId = 'chartHighestScoring';
    window.showLoading(chartId);

    const apiData = await fetchHighestScoringActivities();
    if (!apiData) {
        window.showError(chartId, 'Error al cargar actividades con mayor puntuación');
        return;
    }

    const { activities, scores } = apiData;

    if (!activities || activities.length === 0) {
        window.showEmpty(chartId, 'No hay datos de actividades puntuadas');
        return;
    }

    // Calcular máximo dinámicamente
    const maxScore = Math.max(...scores, 0);
    const maxScoreRounded = Math.ceil(maxScore * 1.1); // 10% más para espacio

    // Umbrales proporcionales (80%, 60%, 50%)
    const thresholdHigh = maxScoreRounded * 0.8;
    const thresholdMed = maxScoreRounded * 0.6;
    const thresholdLow = maxScoreRounded * 0.5;

    const data = [{
        y: activities,
        x: scores,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: scores.map(score => {
                if (score >= thresholdHigh) return window.CHART_COLORS.olive;
                if (score >= thresholdMed) return window.CHART_COLORS.lime;
                if (score >= thresholdLow) return window.CHART_COLORS.yellow;
                return window.CHART_COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: scores.map(s => s.toFixed(1)),
        textposition: 'outside',
        textfont: { size: 11, color: window.CHART_COLORS.text, family: 'Inter, sans-serif' },
        hovertemplate: '<b>%{y}</b><br>Puntuación: %{x:.1f}<br>(promedio)<extra></extra>'
    }];

    const layout = window.getCommonPlotlyLayout({
        margin: { t: 20, r: 60, b: 50, l: 180 },
        showlegend: false,
        xaxis: {
            
            title: { text: 'Puntuación Media', font: { size: 12 } },
            range: [0, maxScoreRounded]
        },
        yaxis: {
            
            automargin: true,
            tickfont: { size: 11 }
        },
        shapes: [
            {
                type: 'line',
                x0: thresholdLow,
                x1: thresholdLow,
                y0: -0.5,
                y1: activities.length - 0.5,
                line: {
                    color: window.CHART_COLORS.brown,
                    width: 1,
                    dash: 'dash'
                }
            }
        ],
        height: 400
    });

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, window.getCommonPlotlyConfig());
}

// ============================================
// Chart 3: Rendimiento Medio por Clase - Barras Horizontales
// ============================================
async function initChartClassPerformance() {
    const chartId = 'chartClassPerformance';
    window.showLoading(chartId);

    const apiData = await fetchClassPerformance();
    if (!apiData) {
        window.showError(chartId, 'Error al cargar rendimiento por clase');
        return;
    }

    const { classes, scores, student_counts } = apiData;

    if (!classes || classes.length === 0) {
        window.showEmpty(chartId, 'No hay datos de clases');
        return;
    }

    // Calcular máximo dinámicamente
    const maxScore = Math.max(...scores, 0);
    const maxScoreRounded = Math.ceil(maxScore * 1.1); // 10% más para espacio

    // Umbrales proporcionales (80%, 60%, 50%)
    const thresholdHigh = maxScoreRounded * 0.8;
    const thresholdMed = maxScoreRounded * 0.6;
    const thresholdLow = maxScoreRounded * 0.5;

    const data = [{
        y: classes,
        x: scores,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: scores.map(score => {
                if (score >= thresholdHigh) return window.CHART_COLORS.olive;
                if (score >= thresholdMed) return window.CHART_COLORS.lime;
                if (score >= thresholdLow) return window.CHART_COLORS.yellow;
                return window.CHART_COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: scores.map(s => s.toFixed(1)),
        textposition: 'outside',
        textfont: { size: 11, color: window.CHART_COLORS.text, family: 'Inter, sans-serif' },
        customdata: student_counts,
        hovertemplate: '<b>%{y}</b><br>Puntuación Media: %{x:.1f}<br>%{customdata} estudiantes<extra></extra>'
    }];

    const layout = window.getCommonPlotlyLayout({
        margin: { t: 20, r: 60, b: 50, l: 180 },
        showlegend: false,
        xaxis: {
            
            title: { text: 'Puntuación Media', font: { size: 12 } },
            range: [0, maxScoreRounded]
        },
        yaxis: {
            
            automargin: true,
            tickfont: { size: 11 }
        },
        shapes: [
            {
                type: 'line',
                x0: thresholdLow,
                x1: thresholdLow,
                y0: -0.5,
                y1: classes.length - 0.5,
                line: {
                    color: window.CHART_COLORS.brown,
                    width: 1,
                    dash: 'dash'
                }
            }
        ],
        height: 400
    });

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, window.getCommonPlotlyConfig());
}

// ============================================
// Time Filter Functionality (Currently no-op as data is not time-filtered)
// ============================================
function initTimeFilter() {
    const filterBtns = document.querySelectorAll('.filter-btn');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const range = btn.dataset.range;
            console.log(`Filter changed to: ${range}`);

            // Note: Current API doesn't support time filtering for learning stats
            // Charts show all-time data
        });
    });
}

// ============================================

async function updateSummaryCards() {
    const summary = await fetchSummary();
    if (!summary) return;

    const puntuacionEl = document.getElementById('puntuacionMediaValue');
    if (puntuacionEl) window.animateValue(puntuacionEl, 0, summary.puntuacion_media, 1500, '', true);

    const aprobadosEl = document.getElementById('aprobadosValue');
    if (aprobadosEl) window.animateValue(aprobadosEl, 0, summary.aprobados_porcentaje, 1300, '%', true);

    const tiempoEl = document.getElementById('tiempoMedioValue');
    if (tiempoEl) window.animateValue(tiempoEl, 0, summary.tiempo_medio, 1200, ' min');

    const actividadesEl = document.getElementById('actividadesEvaluadasValue');
    if (actividadesEl) window.animateValue(actividadesEl, 0, summary.actividades_evaluadas, 1400);
}

// ============================================
// Window Resize Handler
// ============================================
function handleResize() {
    const charts = ['chartMostPlayed', 'chartHighestScoring', 'chartClassPerformance'];
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
    if (typeof Plotly !== 'undefined') {
        await Promise.all([
            initChartMostPlayed(),
            initChartHighestScoring(),
            initChartClassPerformance()
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
