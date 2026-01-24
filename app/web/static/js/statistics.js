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
// Sample Data Generation
// ============================================

/**
 * Generate dates for the last N days
 */
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

/**
 * Generate random data with optional trend
 */
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
// Chart 1: Usuarios Activos (DAU / WAU / MAU) - Línea
// go.Scatter(mode="lines")
// ============================================
function initChartActiveUsers() {
    const dates = generateDates(30);

    // DAU: ~800-1400
    const dauData = generateData(30, 800, 1400, 5);
    // WAU: ~3000-5000
    const wauData = generateData(30, 3000, 5000, 10);
    // MAU: ~8000-12000
    const mauData = generateData(30, 8000, 12000, 15);

    const data = [
        {
            x: dates,
            y: dauData,
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
            y: wauData,
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
            y: mauData,
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

    Plotly.newPlot('chartActiveUsers', data, layout, commonConfig);
}

// ============================================
// Chart 2: Nuevos Usuarios por Día - Barras
// go.Bar
// ============================================
function initChartNewUsers() {
    const dates = generateDates(14);
    const newUsersData = generateData(14, 50, 150, 2);

    const data = [{
        x: dates,
        y: newUsersData,
        type: 'bar',
        name: 'Nuevos Usuarios',
        marker: {
            color: newUsersData.map((_, i) => {
                const ratio = i / newUsersData.length;
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

    Plotly.newPlot('chartNewUsers', data, layout, commonConfig);
}

// ============================================
// Chart 3: Ratio Usuarios Activos / Totales - Área
// go.Scatter(fill="tozeroy")
// ============================================
function initChartRatio() {
    const dates = generateDates(30);
    // Ratio between 20% - 45%
    const ratioData = generateData(30, 20, 45, 0.3);

    const data = [{
        x: dates,
        y: ratioData,
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
            range: [0, 50],
            ticksuffix: '%'
        },
        xaxis: {
            ...commonLayout.xaxis,
            tickformat: '%d %b'
        }
    };

    Plotly.newPlot('chartRatio', data, layout, commonConfig);
}

// ============================================
// Chart 4: Logins por Día - Línea con Marcadores
// go.Scatter(mode="lines+markers")
// ============================================
function initChartLogins() {
    const dates = generateDates(30);
    const loginsData = generateData(30, 1500, 3000, 8);

    const data = [{
        x: dates,
        y: loginsData,
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

    Plotly.newPlot('chartLogins', data, layout, commonConfig);
}

// ============================================
// Time Filter Functionality
// ============================================
function initTimeFilter() {
    const filterBtns = document.querySelectorAll('.filter-btn');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');

            // Get the selected range
            const range = btn.dataset.range;
            console.log(`Filter changed to: ${range}`);

            // Reinitialize charts with new data range
            // In a real application, this would fetch new data from the API
            initChartActiveUsers();
            initChartNewUsers();
            initChartRatio();
            initChartLogins();
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

function animateSummaryCards() {
    // Animate DAU value
    const dauEl = document.getElementById('dauValue');
    if (dauEl) animateValue(dauEl, 0, 1247, 1500);

    // Animate New Users value
    const newUsersEl = document.getElementById('newUsersValue');
    if (newUsersEl) animateValue(newUsersEl, 0, 89, 1200);

    // Animate Ratio value
    const ratioEl = document.getElementById('ratioValue');
    if (ratioEl) animateValue(ratioEl, 0, 32.4, 1300, '%');

    // Animate Logins value
    const loginsEl = document.getElementById('loginsValue');
    if (loginsEl) animateValue(loginsEl, 0, 2156, 1400);
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
function init() {
    console.log('Statistics page initialized');

    // Initialize all charts
    if (typeof Plotly !== 'undefined') {
        initChartActiveUsers();
        initChartNewUsers();
        initChartRatio();
        initChartLogins();
    } else {
        console.error('Plotly is not loaded');
    }

    // Initialize time filter
    initTimeFilter();

    // Animate summary cards on load
    animateSummaryCards();

    // Add resize listener
    window.addEventListener('resize', debounce(handleResize, 250));
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
