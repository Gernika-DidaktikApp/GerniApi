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

async function fetchAverageScoreByActivity() {
    try {
        const response = await fetch(`${API_BASE}/average-score-by-activity`);
        if (!response.ok) throw new Error('Failed to fetch average score by activity');
        return await response.json();
    } catch (error) {
        console.error('Error fetching average score by activity:', error);
        return null;
    }
}

async function fetchScoreDistribution() {
    try {
        const response = await fetch(`${API_BASE}/score-distribution`);
        if (!response.ok) throw new Error('Failed to fetch score distribution');
        return await response.json();
    } catch (error) {
        console.error('Error fetching score distribution:', error);
        return null;
    }
}

async function fetchTimeBoxplotByActivity() {
    try {
        const response = await fetch(`${API_BASE}/time-boxplot-by-activity`);
        if (!response.ok) throw new Error('Failed to fetch time boxplot');
        return await response.json();
    } catch (error) {
        console.error('Error fetching time boxplot:', error);
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
// Chart 1: Puntuación media por actividad - Barras
// ============================================
async function initChartPuntuacionMedia() {
    const chartId = 'chartPuntuacionMedia';
    showLoading(chartId);

    const apiData = await fetchAverageScoreByActivity();
    if (!apiData) {
        showError(chartId, 'Error al cargar puntuaciones');
        return;
    }

    const { activities, scores } = apiData;

    if (!activities || activities.length === 0) {
        showError(chartId, 'No hay datos de puntuaciones disponibles');
        return;
    }

    const data = [{
        y: activities,
        x: scores,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: scores.map(p => {
                if (p >= 8) return COLORS.olive;
                if (p >= 7) return COLORS.lime;
                return COLORS.yellow;
            }),
            line: { width: 0 }
        },
        text: scores.map(p => p.toFixed(1)),
        textposition: 'outside',
        textfont: { size: 12, color: COLORS.text, family: 'Inter, sans-serif' },
        hovertemplate: '<b>%{y}</b><br>Puntuación media: %{x:.1f}<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 60, b: 50, l: 180 },
        showlegend: false,
        xaxis: {
            ...commonLayout.xaxis,
            title: { text: 'Puntuación (0-10)', font: { size: 12 } },
            range: [0, 10]
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
// Chart 2: Distribución de puntuaciones - Histograma
// ============================================
async function initChartDistribucion() {
    const chartId = 'chartDistribucion';
    showLoading(chartId);

    const apiData = await fetchScoreDistribution();
    if (!apiData) {
        showError(chartId, 'Error al cargar distribución');
        return;
    }

    const { scores, mean } = apiData;

    if (!scores || scores.length === 0) {
        showError(chartId, 'No hay datos de distribución disponibles');
        return;
    }

    const data = [{
        x: scores,
        type: 'histogram',
        marker: {
            color: COLORS.olive,
            line: {
                color: COLORS.oliveDark,
                width: 1
            }
        },
        opacity: 0.85,
        xbins: {
            start: 0,
            end: 10,
            size: 0.5
        },
        hovertemplate: 'Puntuación: %{x}<br>Frecuencia: %{y}<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        showlegend: false,
        bargap: 0.05,
        xaxis: {
            ...commonLayout.xaxis,
            title: { text: 'Puntuación', font: { size: 12 } },
            range: [0, 10],
            dtick: 1
        },
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Frecuencia', font: { size: 12 } }
        },
        shapes: [
            // Add vertical line for mean
            {
                type: 'line',
                x0: mean,
                x1: mean,
                y0: 0,
                y1: 1,
                yref: 'paper',
                line: {
                    color: COLORS.brown,
                    width: 2,
                    dash: 'dash'
                }
            }
        ],
        annotations: [
            {
                x: mean,
                y: 1,
                yref: 'paper',
                text: `Media: ${mean}`,
                showarrow: false,
                font: { size: 11, color: COLORS.brown },
                yshift: 10
            }
        ]
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 3: Tiempo por actividad - Boxplot
// ============================================
async function initChartTiempoBoxplot() {
    const chartId = 'chartTiempoBoxplot';
    showLoading(chartId);

    const apiData = await fetchTimeBoxplotByActivity();
    if (!apiData) {
        showError(chartId, 'Error al cargar tiempos');
        return;
    }

    const { activities, times } = apiData;

    if (!activities || activities.length === 0) {
        showError(chartId, 'No hay datos de tiempo disponibles');
        return;
    }

    // Create color palette for boxplots
    const colorPalette = [COLORS.olive, COLORS.lime, COLORS.brown, COLORS.oliveDark, COLORS.yellow];

    const data = activities.map((activity, index) => ({
        y: times[index],
        type: 'box',
        name: activity,
        marker: { color: colorPalette[index % colorPalette.length] },
        boxpoints: 'outliers',
        jitter: 0.3,
        hovertemplate: '%{y} min<extra></extra>'
    }));

    const layout = {
        ...commonLayout,
        showlegend: false,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Tiempo (minutos)', font: { size: 12 } }
        },
        xaxis: {
            ...commonLayout.xaxis,
            tickfont: { size: 10 }
        }
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
    const charts = ['chartPuntuacionMedia', 'chartDistribucion', 'chartTiempoBoxplot'];
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
    console.log('Statistics Learning page initialized');

    if (typeof Plotly !== 'undefined') {
        await Promise.all([
            initChartPuntuacionMedia(),
            initChartDistribucion(),
            initChartTiempoBoxplot()
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
