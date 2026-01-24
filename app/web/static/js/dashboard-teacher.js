/**
 * Dashboard Teacher Page JavaScript
 * Handles Plotly charts for teacher/class view
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
// Sample Student Data
// ============================================
const STUDENTS = [
    { name: 'Aitor Etxebarria', progress: 92, time: 45 },
    { name: 'Ane Ugarte', progress: 88, time: 52 },
    { name: 'Mikel Aguirre', progress: 85, time: 38 },
    { name: 'Leire Mendizabal', progress: 82, time: 41 },
    { name: 'Unai Goikoetxea', progress: 78, time: 35 },
    { name: 'Nerea Arrieta', progress: 75, time: 48 },
    { name: 'Jon Zabala', progress: 72, time: 29 },
    { name: 'Irati Elizondo', progress: 68, time: 33 },
    { name: 'Eneko Arana', progress: 65, time: 42 },
    { name: 'Maialen Berasategui', progress: 62, time: 36 },
    { name: 'Gorka Uriarte', progress: 58, time: 28 },
    { name: 'Nahia Olaizola', progress: 55, time: 44 },
    { name: 'Andoni Larrea', progress: 52, time: 31 },
    { name: 'Izaro Garitano', progress: 48, time: 26 },
    { name: 'Asier Iturriaga', progress: 42, time: 22 },
    { name: 'Miren Arteaga', progress: 38, time: 40 },
    { name: 'Pablo López', progress: 35, time: 18 },
    { name: 'María González', progress: 25, time: 15 }
];

const ACTIVITIES = [
    'Árbol del Gernika',
    'Museo de la Paz',
    'Refugio Antiaéreo',
    'Casa de Juntas',
    'Parque de los Pueblos'
];

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
// Plotly Chart Configuration
// ============================================

const commonLayout = {
    margin: { t: 20, r: 30, b: 50, l: 120 },
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
// Chart 1: Progreso por alumno - Barras horizontales
// go.Bar
// ============================================
function initChartProgresoAlumno() {
    const sortedStudents = [...STUDENTS].sort((a, b) => b.progress - a.progress);
    const names = sortedStudents.map(s => s.name);
    const progress = sortedStudents.map(s => s.progress);

    const data = [{
        y: names,
        x: progress,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: progress.map(p => {
                if (p >= 75) return COLORS.olive;
                if (p >= 50) return COLORS.lime;
                if (p >= 30) return COLORS.yellow;
                return COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: progress.map(p => `${p}%`),
        textposition: 'outside',
        textfont: { size: 10, color: COLORS.text },
        hovertemplate: '<b>%{y}</b><br>Progreso: %{x}%<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        margin: { t: 10, r: 50, b: 40, l: 140 },
        showlegend: false,
        xaxis: {
            ...commonLayout.xaxis,
            title: { text: 'Progreso (%)', font: { size: 12 } },
            range: [0, 105]
        },
        yaxis: {
            ...commonLayout.yaxis,
            automargin: true,
            tickfont: { size: 10 }
        }
    };

    Plotly.newPlot('chartProgresoAlumno', data, layout, commonConfig);
}

// ============================================
// Chart 2: Tiempo dedicado por alumno - Barras
// go.Bar
// ============================================
function initChartTiempoAlumno() {
    const sortedStudents = [...STUDENTS].sort((a, b) => b.time - a.time).slice(0, 10);
    const names = sortedStudents.map(s => s.name.split(' ')[0]); // First name only
    const time = sortedStudents.map(s => s.time);

    const data = [{
        x: names,
        y: time,
        type: 'bar',
        marker: {
            color: time.map((t, i) => {
                const ratio = i / time.length;
                return `rgba(107, 142, 58, ${0.4 + (1 - ratio) * 0.6})`;
            }),
            line: { width: 0 }
        },
        hovertemplate: '<b>%{x}</b><br>Tiempo: %{y} min<extra></extra>'
    }];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 20, b: 60, l: 50 },
        showlegend: false,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Minutos', font: { size: 12 } }
        },
        xaxis: {
            ...commonLayout.xaxis,
            tickangle: -45
        }
    };

    Plotly.newPlot('chartTiempoAlumno', data, layout, commonConfig);
}

// ============================================
// Chart 3: Actividades completadas por clase - Barras apiladas
// go.Bar (stack)
// ============================================
function initChartActividadesClase() {
    const completed = [18, 15, 12, 10, 8];
    const inProgress = [4, 6, 7, 8, 6];
    const notStarted = [2, 3, 5, 6, 10];

    const data = [
        {
            x: ACTIVITIES,
            y: completed,
            type: 'bar',
            name: 'Completadas',
            marker: { color: COLORS.olive },
            hovertemplate: '<b>%{x}</b><br>Completadas: %{y} alumnos<extra></extra>'
        },
        {
            x: ACTIVITIES,
            y: inProgress,
            type: 'bar',
            name: 'En Progreso',
            marker: { color: COLORS.lime },
            hovertemplate: '<b>%{x}</b><br>En Progreso: %{y} alumnos<extra></extra>'
        },
        {
            x: ACTIVITIES,
            y: notStarted,
            type: 'bar',
            name: 'Sin Empezar',
            marker: { color: COLORS.yellow },
            hovertemplate: '<b>%{x}</b><br>Sin Empezar: %{y} alumnos<extra></extra>'
        }
    ];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 20, b: 80, l: 50 },
        barmode: 'stack',
        showlegend: false,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Alumnos', font: { size: 12 } }
        },
        xaxis: {
            ...commonLayout.xaxis,
            tickangle: -30,
            tickfont: { size: 9 }
        }
    };

    Plotly.newPlot('chartActividadesClase', data, layout, commonConfig);
}

// ============================================
// Chart 4: Evolución de la clase - Línea
// go.Scatter(lines)
// ============================================
function initChartEvolucionClase() {
    const dates = [];
    const today = new Date();
    for (let i = 13; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        dates.push(date.toISOString().split('T')[0]);
    }

    // Simulated progress evolution (trending upward)
    const progressData = [42, 45, 48, 51, 53, 55, 58, 60, 62, 64, 65, 66, 67, 68];
    // Simulated grade evolution
    const gradeData = [6.2, 6.4, 6.5, 6.6, 6.8, 6.9, 7.0, 7.1, 7.0, 7.2, 7.3, 7.3, 7.4, 7.4];
    // Normalize grade to percentage scale for dual axis
    const gradeNormalized = gradeData.map(g => g * 10);

    const data = [
        {
            x: dates,
            y: progressData,
            type: 'scatter',
            mode: 'lines',
            name: 'Progreso (%)',
            line: {
                color: COLORS.olive,
                width: 3,
                shape: 'spline'
            },
            fill: 'tozeroy',
            fillcolor: 'rgba(107, 142, 58, 0.1)',
            hovertemplate: '<b>Progreso</b><br>%{x}<br>%{y}%<extra></extra>'
        },
        {
            x: dates,
            y: gradeNormalized,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Nota Media (×10)',
            line: {
                color: COLORS.lime,
                width: 2,
                dash: 'dot'
            },
            marker: {
                size: 6,
                color: COLORS.lime
            },
            yaxis: 'y2',
            hovertemplate: '<b>Nota Media</b><br>%{x}<br>%{customdata:.1f}<extra></extra>',
            customdata: gradeData
        }
    ];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 60, b: 50, l: 60 },
        showlegend: false,
        xaxis: {
            ...commonLayout.xaxis,
            tickformat: '%d %b'
        },
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Progreso (%)', font: { size: 11, color: COLORS.olive } },
            range: [0, 100]
        },
        yaxis2: {
            title: { text: 'Nota Media', font: { size: 11, color: COLORS.lime } },
            overlaying: 'y',
            side: 'right',
            range: [0, 100],
            tickvals: [0, 25, 50, 75, 100],
            ticktext: ['0', '2.5', '5', '7.5', '10'],
            gridcolor: 'rgba(0,0,0,0)',
            tickfont: { size: 11, color: COLORS.lime }
        }
    };

    Plotly.newPlot('chartEvolucionClase', data, layout, commonConfig);
}

// ============================================
// Filter Functionality
// ============================================
function initFilters() {
    const applyBtn = document.getElementById('applyFilters');
    const filterClase = document.getElementById('filterClase');
    const filterFechas = document.getElementById('filterFechas');
    const filterActividad = document.getElementById('filterActividad');

    if (applyBtn) {
        applyBtn.addEventListener('click', () => {
            console.log('Filters applied:', {
                clase: filterClase?.value,
                fechas: filterFechas?.value,
                actividad: filterActividad?.value
            });

            // Reinitialize charts with new filter values
            initChartProgresoAlumno();
            initChartTiempoAlumno();
            initChartActividadesClase();
            initChartEvolucionClase();

            // Show feedback
            applyBtn.textContent = '✓ Aplicado';
            setTimeout(() => {
                applyBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M22 3H2L10 12.46V19L14 21V12.46L22 3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Aplicar
                `;
            }, 1500);
        });
    }
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
            element.textContent = current + suffix;
        }

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

function animateSummaryCards() {
    const alumnosEl = document.getElementById('alumnosValue');
    if (alumnosEl) animateValue(alumnosEl, 0, 24, 1000);

    const progresoEl = document.getElementById('progresoValue');
    if (progresoEl) animateValue(progresoEl, 0, 68, 1200, '%');

    const tiempoEl = document.getElementById('tiempoValue');
    if (tiempoEl) animateValue(tiempoEl, 0, 32, 1100, ' min');

    const notaEl = document.getElementById('notaValue');
    if (notaEl) {
        const startTime = performance.now();
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / 1300, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = (7.4 * eased).toFixed(1);
            notaEl.textContent = current;
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }
}

// ============================================
// Window Resize Handler
// ============================================
function handleResize() {
    const charts = ['chartProgresoAlumno', 'chartTiempoAlumno', 'chartActividadesClase', 'chartEvolucionClase'];
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
    console.log('Dashboard Teacher page initialized');

    if (typeof Plotly !== 'undefined') {
        initChartProgresoAlumno();
        initChartTiempoAlumno();
        initChartActividadesClase();
        initChartEvolucionClase();
    } else {
        console.error('Plotly is not loaded');
    }

    initFilters();
    animateSummaryCards();
    window.addEventListener('resize', debounce(handleResize, 250));
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
