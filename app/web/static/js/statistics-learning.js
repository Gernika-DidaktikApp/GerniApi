/**
 * Statistics Learning Page JavaScript
 * Handles Plotly charts for learning and performance metrics with real API data
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
const API_BASE = '/api/statistics/learning';

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

function showEmpty(chartId, message = 'No hay datos disponibles') {
    const container = document.getElementById(chartId);
    if (container) {
        container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; min-height: 300px;">
                <div style="text-align: center; color: #6B7A5C;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin: 0 auto; opacity: 0.5;">
                        <circle cx="12" cy="12" r="10" stroke-width="2"/>
                        <path d="M12 8V12M12 16H12.01" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <p style="margin-top: 1rem; font-size: 0.875rem;">${message}</p>
                    <p style="margin-top: 0.5rem; font-size: 0.75rem; opacity: 0.7;">Genera datos de prueba para ver estadísticas</p>
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
    ['puntuacionMediaValue', 'aprobadosValue', 'tiempoMedioValue', 'actividadesEvaluadasValue'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = '--';
    });
}

async function fetchMostPlayedActivities() {
    try {
        const response = await fetch(`${API_BASE}/most-played-activities?limit=10`);
        if (!response.ok) throw new Error('Failed to fetch most played activities');
        return await response.json();
    } catch (error) {
        return null;
    }
}

async function fetchHighestScoringActivities() {
    try {
        const response = await fetch(`${API_BASE}/highest-scoring-activities?limit=10`);
        if (!response.ok) throw new Error('Failed to fetch highest scoring activities');
        return await response.json();
    } catch (error) {
        return null;
    }
}

async function fetchClassPerformance() {
    try {
        const response = await fetch(`${API_BASE}/class-performance`);
        if (!response.ok) throw new Error('Failed to fetch class performance');
        return await response.json();
    } catch (error) {
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
// Chart 1: Actividades Más Jugadas - Barras Horizontales
// ============================================
async function initChartMostPlayed() {
    const chartId = 'chartMostPlayed';
    showLoading(chartId);

    const apiData = await fetchMostPlayedActivities();
    if (!apiData) {
        showError(chartId, 'Error al cargar actividades más jugadas');
        return;
    }

    const { activities, counts } = apiData;

    if (!activities || activities.length === 0) {
        showEmpty(chartId, 'No hay datos de actividades jugadas');
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
                if (ratio >= 0.8) return COLORS.olive;
                if (ratio >= 0.6) return COLORS.lime;
                if (ratio >= 0.4) return COLORS.yellow;
                return COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: counts.map(c => c),
        textposition: 'outside',
        textfont: { size: 11, color: COLORS.text, family: 'Inter, sans-serif' },
        hovertemplate: '<b>%{y}</b><br>%{x} veces jugada<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 60, b: 50, l: 180 },
        showlegend: false,
        xaxis: {
            ...commonLayout.xaxis,
            title: { text: 'Veces Jugadas', font: { size: 12 } }
        },
        yaxis: {
            ...commonLayout.yaxis,
            automargin: true,
            tickfont: { size: 11 }
        },
        height: 400
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 2: Actividades con Mayor Puntuación - Barras Horizontales
// ============================================
async function initChartHighestScoring() {
    const chartId = 'chartHighestScoring';
    showLoading(chartId);

    const apiData = await fetchHighestScoringActivities();
    if (!apiData) {
        showError(chartId, 'Error al cargar actividades con mayor puntuación');
        return;
    }

    const { activities, scores } = apiData;

    if (!activities || activities.length === 0) {
        showEmpty(chartId, 'No hay datos de actividades puntuadas');
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
                if (score >= thresholdHigh) return COLORS.olive;
                if (score >= thresholdMed) return COLORS.lime;
                if (score >= thresholdLow) return COLORS.yellow;
                return COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: scores.map(s => s.toFixed(1)),
        textposition: 'outside',
        textfont: { size: 11, color: COLORS.text, family: 'Inter, sans-serif' },
        hovertemplate: '<b>%{y}</b><br>Puntuación: %{x:.1f}<br>(promedio)<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 60, b: 50, l: 180 },
        showlegend: false,
        xaxis: {
            ...commonLayout.xaxis,
            title: { text: 'Puntuación Media', font: { size: 12 } },
            range: [0, maxScoreRounded]
        },
        yaxis: {
            ...commonLayout.yaxis,
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
                    color: COLORS.brown,
                    width: 1,
                    dash: 'dash'
                }
            }
        ],
        height: 400
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 3: Rendimiento Medio por Clase - Barras Horizontales
// ============================================
async function initChartClassPerformance() {
    const chartId = 'chartClassPerformance';
    showLoading(chartId);

    const apiData = await fetchClassPerformance();
    if (!apiData) {
        showError(chartId, 'Error al cargar rendimiento por clase');
        return;
    }

    const { classes, scores, student_counts } = apiData;

    if (!classes || classes.length === 0) {
        showEmpty(chartId, 'No hay datos de clases');
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
                if (score >= thresholdHigh) return COLORS.olive;
                if (score >= thresholdMed) return COLORS.lime;
                if (score >= thresholdLow) return COLORS.yellow;
                return COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: scores.map(s => s.toFixed(1)),
        textposition: 'outside',
        textfont: { size: 11, color: COLORS.text, family: 'Inter, sans-serif' },
        customdata: student_counts,
        hovertemplate: '<b>%{y}</b><br>Puntuación Media: %{x:.1f}<br>%{customdata} estudiantes<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 60, b: 50, l: 180 },
        showlegend: false,
        xaxis: {
            ...commonLayout.xaxis,
            title: { text: 'Puntuación Media', font: { size: 12 } },
            range: [0, maxScoreRounded]
        },
        yaxis: {
            ...commonLayout.yaxis,
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
                    color: COLORS.brown,
                    width: 1,
                    dash: 'dash'
                }
            }
        ],
        height: 400
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
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
// Animate Summary Values
// ============================================
function animateValue(element, start, end, duration, suffix = '', isFloat = false) {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);

        let current;
        if (isFloat) {
            current = (start + (end - start) * eased).toFixed(1);
        } else {
            current = Math.floor(start + (end - start) * eased);
        }

        if (element) {
            if (typeof current === 'number' && current >= 1000) {
                element.textContent = current.toLocaleString() + suffix;
            } else {
                element.textContent = current + suffix;
            }
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

    const puntuacionEl = document.getElementById('puntuacionMediaValue');
    if (puntuacionEl) animateValue(puntuacionEl, 0, summary.puntuacion_media, 1500, '', true);

    const aprobadosEl = document.getElementById('aprobadosValue');
    if (aprobadosEl) animateValue(aprobadosEl, 0, summary.aprobados_porcentaje, 1300, '%', true);

    const tiempoEl = document.getElementById('tiempoMedioValue');
    if (tiempoEl) animateValue(tiempoEl, 0, summary.tiempo_medio, 1200, ' min');

    const actividadesEl = document.getElementById('actividadesEvaluadasValue');
    if (actividadesEl) animateValue(actividadesEl, 0, summary.actividades_evaluadas, 1400);
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
    if (typeof Plotly !== 'undefined') {
        await Promise.all([
            initChartMostPlayed(),
            initChartHighestScoring(),
            initChartClassPerformance()
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
