/**
 * Statistics Learning Page JavaScript
 * Handles Plotly charts for learning and performance metrics
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
// Sample Data Generation
// ============================================

function generateNormalDistribution(mean, stdDev, count) {
    const data = [];
    for (let i = 0; i < count; i++) {
        // Box-Muller transform for normal distribution
        const u1 = Math.random();
        const u2 = Math.random();
        const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        let value = mean + z * stdDev;
        // Clamp between 0 and 10
        value = Math.max(0, Math.min(10, value));
        data.push(parseFloat(value.toFixed(1)));
    }
    return data;
}

function generateBoxplotData(min, q1, median, q3, max, count) {
    const data = [];
    for (let i = 0; i < count; i++) {
        const rand = Math.random();
        let value;
        if (rand < 0.1) {
            value = min + Math.random() * (q1 - min) * 0.5;
        } else if (rand < 0.25) {
            value = q1 + Math.random() * (median - q1);
        } else if (rand < 0.75) {
            value = median + (Math.random() - 0.5) * (q3 - q1);
        } else if (rand < 0.9) {
            value = median + Math.random() * (q3 - median);
        } else {
            value = q3 + Math.random() * (max - q3) * 0.5;
        }
        data.push(Math.round(value));
    }
    return data;
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
// go.Bar
// ============================================
function initChartPuntuacionMedia() {
    const actividades = [
        'Árbol del Gernika',
        'Museo de la Paz',
        'Refugio Antiaéreo',
        'Casa de Juntas',
        'Parque de los Pueblos',
        'Iglesia Santa María',
        'Plaza de los Fueros',
        'Mercado Municipal'
    ];

    const puntuaciones = [8.7, 8.2, 7.9, 7.6, 7.4, 7.1, 6.8, 6.5];

    const data = [{
        y: actividades,
        x: puntuaciones,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: puntuaciones.map(p => {
                if (p >= 8) return COLORS.olive;
                if (p >= 7) return COLORS.lime;
                return COLORS.yellow;
            }),
            line: { width: 0 }
        },
        text: puntuaciones.map(p => p.toFixed(1)),
        textposition: 'outside',
        textfont: { size: 12, color: COLORS.text, family: 'Inter, sans-serif' },
        hovertemplate: '<b>%{y}</b><br>Puntuación media: %{x:.1f}<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 60, b: 50, l: 150 },
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
        }
    };

    Plotly.newPlot('chartPuntuacionMedia', data, layout, commonConfig);
}

// ============================================
// Chart 2: Distribución de puntuaciones - Histograma
// go.Histogram
// ============================================
function initChartDistribucion() {
    // Generate sample scores with normal distribution around 7.5
    const scores = generateNormalDistribution(7.5, 1.5, 500);

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
                x0: 7.5,
                x1: 7.5,
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
                x: 7.5,
                y: 1,
                yref: 'paper',
                text: 'Media: 7.5',
                showarrow: false,
                font: { size: 11, color: COLORS.brown },
                yshift: 10
            }
        ]
    };

    Plotly.newPlot('chartDistribucion', data, layout, commonConfig);
}

// ============================================
// Chart 3: Tiempo por actividad - Boxplot
// go.Box
// ============================================
function initChartTiempoBoxplot() {
    const actividades = [
        'Árbol del<br>Gernika',
        'Museo de<br>la Paz',
        'Refugio<br>Antiaéreo',
        'Casa de<br>Juntas',
        'Plaza de<br>los Fueros'
    ];

    // Generate sample data for each activity
    const tiempoArbol = generateBoxplotData(8, 14, 18, 24, 35, 100);
    const tiempoMuseo = generateBoxplotData(10, 18, 25, 32, 45, 100);
    const tiempoRefugio = generateBoxplotData(5, 10, 15, 20, 30, 100);
    const tiempoCasa = generateBoxplotData(12, 16, 22, 28, 40, 100);
    const tiempoPlaza = generateBoxplotData(6, 12, 16, 22, 32, 100);

    const data = [
        {
            y: tiempoArbol,
            type: 'box',
            name: actividades[0],
            marker: { color: COLORS.olive },
            boxpoints: 'outliers',
            jitter: 0.3,
            hovertemplate: '%{y} min<extra></extra>'
        },
        {
            y: tiempoMuseo,
            type: 'box',
            name: actividades[1],
            marker: { color: COLORS.lime },
            boxpoints: 'outliers',
            jitter: 0.3,
            hovertemplate: '%{y} min<extra></extra>'
        },
        {
            y: tiempoRefugio,
            type: 'box',
            name: actividades[2],
            marker: { color: COLORS.brown },
            boxpoints: 'outliers',
            jitter: 0.3,
            hovertemplate: '%{y} min<extra></extra>'
        },
        {
            y: tiempoCasa,
            type: 'box',
            name: actividades[3],
            marker: { color: COLORS.oliveDark },
            boxpoints: 'outliers',
            jitter: 0.3,
            hovertemplate: '%{y} min<extra></extra>'
        },
        {
            y: tiempoPlaza,
            type: 'box',
            name: actividades[4],
            marker: { color: COLORS.yellow },
            boxpoints: 'outliers',
            jitter: 0.3,
            hovertemplate: '%{y} min<extra></extra>'
        }
    ];

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

    Plotly.newPlot('chartTiempoBoxplot', data, layout, commonConfig);
}

// ============================================
// Time Filter Functionality
// ============================================
function initTimeFilter() {
    const filterBtns = document.querySelectorAll('.filter-btn');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const range = btn.dataset.range;
            console.log(`Filter changed to: ${range}`);

            // Reinitialize charts with new data range
            initChartPuntuacionMedia();
            initChartDistribucion();
            initChartTiempoBoxplot();
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

function animateSummaryCards() {
    const puntuacionEl = document.getElementById('puntuacionMediaValue');
    if (puntuacionEl) animateValue(puntuacionEl, 0, 7.8, 1500, '', true);

    const aprobadosEl = document.getElementById('aprobadosValue');
    if (aprobadosEl) animateValue(aprobadosEl, 0, 84.2, 1300, '%', true);

    const tiempoEl = document.getElementById('tiempoMedioValue');
    if (tiempoEl) animateValue(tiempoEl, 0, 18, 1200, ' min');

    const actividadesEl = document.getElementById('actividadesEvaluadasValue');
    if (actividadesEl) animateValue(actividadesEl, 0, 2847, 1400);
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
function init() {
    console.log('Statistics Learning page initialized');

    if (typeof Plotly !== 'undefined') {
        initChartPuntuacionMedia();
        initChartDistribucion();
        initChartTiempoBoxplot();
    } else {
        console.error('Plotly is not loaded');
    }

    initTimeFilter();
    animateSummaryCards();
    window.addEventListener('resize', debounce(handleResize, 250));
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
