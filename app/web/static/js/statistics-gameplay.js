/**
 * Statistics Gameplay Page JavaScript
 * Handles Plotly charts for game usage metrics
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

function generateDates(days) {
    const dates = [];
    const today = new Date();
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        dates.push(date.toISOString().split('T')[0]);
    }
    return dates;
}

function generateData(length, min, max, trend = 0) {
    const data = [];
    let value = Math.random() * (max - min) + min;
    for (let i = 0; i < length; i++) {
        value = Math.max(min, Math.min(max, value + (Math.random() - 0.5) * (max - min) * 0.2 + trend));
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
// Chart 1: Partidas creadas por día - Barras
// go.Bar
// ============================================
function initChartPartidasDia() {
    const dates = generateDates(14);
    const partidasData = generateData(14, 20, 60, 1);

    const data = [{
        x: dates,
        y: partidasData,
        type: 'bar',
        name: 'Partidas',
        marker: {
            color: partidasData.map((val, i) => {
                const ratio = i / partidasData.length;
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

    Plotly.newPlot('chartPartidasDia', data, layout, commonConfig);
}

// ============================================
// Chart 2: Partidas completadas vs abandonadas - Donut
// go.Pie(hole=0.6)
// ============================================
function initChartPartidasDonut() {
    const data = [{
        values: [68, 22, 10],
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
            text: '<b>342</b><br>Total',
            font: { size: 16, color: COLORS.text },
            showarrow: false,
            x: 0.5,
            y: 0.5
        }]
    };

    Plotly.newPlot('chartPartidasDonut', data, layout, commonConfig);
}

// ============================================
// Chart 3: Eventos iniciados vs completados - Barras apiladas
// go.Bar (stack)
// ============================================
function initChartEventosStack() {
    const dates = generateDates(10);
    const completados = generateData(10, 80, 150, 2);
    const enProgreso = generateData(10, 20, 50, 0);
    const abandonados = generateData(10, 10, 30, -0.5);

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
            y: enProgreso,
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

    Plotly.newPlot('chartEventosStack', data, layout, commonConfig);
}

// ============================================
// Chart 4: Completion rate por actividad - Barras horizontales
// go.Bar(orientation="h")
// ============================================
function initChartCompletionRate() {
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

    const completionRates = [92, 87, 84, 81, 78, 75, 71, 68];

    const data = [{
        y: actividades,
        x: completionRates,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: completionRates.map(rate => {
                if (rate >= 85) return COLORS.olive;
                if (rate >= 75) return COLORS.lime;
                return COLORS.yellow;
            }),
            line: { width: 0 }
        },
        text: completionRates.map(r => `${r}%`),
        textposition: 'outside',
        textfont: { size: 11, color: COLORS.text },
        hovertemplate: '<b>%{y}</b><br>Completion Rate: %{x}%<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 60, b: 40, l: 140 },
        showlegend: false,
        xaxis: {
            ...commonLayout.xaxis,
            title: { text: 'Completion Rate (%)', font: { size: 12 } },
            range: [0, 100],
            ticksuffix: '%'
        },
        yaxis: {
            ...commonLayout.yaxis,
            automargin: true,
            tickfont: { size: 11 }
        }
    };

    Plotly.newPlot('chartCompletionRate', data, layout, commonConfig);
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
            initChartPartidasDia();
            initChartPartidasDonut();
            initChartEventosStack();
            initChartCompletionRate();
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
    const partidasEl = document.getElementById('partidasActivasValue');
    if (partidasEl) animateValue(partidasEl, 0, 342, 1500);

    const completionEl = document.getElementById('completionRateValue');
    if (completionEl) animateValue(completionEl, 0, 78.5, 1300, '%', true);

    const eventosEl = document.getElementById('eventosCompletadosValue');
    if (eventosEl) animateValue(eventosEl, 0, 1892, 1400);

    const tiempoEl = document.getElementById('tiempoPromedioValue');
    if (tiempoEl) animateValue(tiempoEl, 0, 24, 1200, ' min');
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
function init() {
    console.log('Statistics Gameplay page initialized');

    if (typeof Plotly !== 'undefined') {
        initChartPartidasDia();
        initChartPartidasDonut();
        initChartEventosStack();
        initChartCompletionRate();
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
