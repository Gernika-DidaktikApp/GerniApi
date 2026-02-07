/**
 * Dashboard Teacher Page JavaScript
 * Handles Plotly charts for teacher/class view with authentication and real API data
 */

// Note: Authentication is handled by authManager.protectPage() loaded from auth.js

// ============================================
// Logout Handler
// ============================================
function handleLogout() {
    // Clear authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userUsername');

    console.log('User logged out successfully');

    // Redirect to login page
    window.location.href = '/login';
}

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
const API_BASE = '/api/teacher/dashboard';

// Current filters
let currentFilters = {
    claseId: null,  // Will be set from dropdown
    days: 7
};

// ============================================
// API Helper Functions
// ============================================

function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

async function fetchClasses() {
    try {
        const response = await fetch(`${API_BASE}/classes`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                handleLogout();
                throw new Error('Session expired');
            }
            throw new Error('Failed to fetch classes');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching classes:', error);
        return [];
    }
}

async function fetchSummary() {
    try {
        const params = new URLSearchParams({
            days: currentFilters.days
        });
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const response = await fetch(`${API_BASE}/summary?${params}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch summary');
        return await response.json();
    } catch (error) {
        console.error('Error fetching summary:', error);
        return null;
    }
}

async function fetchStudentProgress() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const response = await fetch(`${API_BASE}/student-progress?${params}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch student progress');
        return await response.json();
    } catch (error) {
        console.error('Error fetching student progress:', error);
        return null;
    }
}

async function fetchStudentTime() {
    try {
        const params = new URLSearchParams({
            days: currentFilters.days
        });
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const response = await fetch(`${API_BASE}/student-time?${params}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch student time');
        return await response.json();
    } catch (error) {
        console.error('Error fetching student time:', error);
        return null;
    }
}

async function fetchActivitiesByClass() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const response = await fetch(`${API_BASE}/activities-by-class?${params}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch activities');
        return await response.json();
    } catch (error) {
        console.error('Error fetching activities:', error);
        return null;
    }
}

async function fetchClassEvolution() {
    try {
        const params = new URLSearchParams({
            days: 14  // Always 14 days for evolution chart
        });
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const response = await fetch(`${API_BASE}/class-evolution?${params}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch class evolution');
        return await response.json();
    } catch (error) {
        console.error('Error fetching class evolution:', error);
        return null;
    }
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
                        <line x1="8" y1="12" x2="16" y2="12" stroke-width="2"/>
                    </svg>
                    <p style="margin-top: 1rem; font-size: 0.875rem;">${message}</p>
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
// ============================================
async function initChartProgresoAlumno() {
    const chartId = 'chartProgresoAlumno';
    showLoading(chartId);

    const apiData = await fetchStudentProgress();
    if (!apiData) {
        showError(chartId, 'Error al cargar progreso de alumnos');
        return;
    }

    const { students, progress } = apiData;

    if (!students || students.length === 0) {
        showEmpty(chartId, 'No hay alumnos en esta clase');
        return;
    }

    // Sort by progress descending
    const sorted = students.map((name, i) => ({ name, progress: progress[i] }))
        .sort((a, b) => b.progress - a.progress);

    const sortedNames = sorted.map(s => s.name);
    const sortedProgress = sorted.map(s => s.progress);

    const data = [{
        y: sortedNames,
        x: sortedProgress,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: sortedProgress.map(p => {
                if (p >= 75) return COLORS.olive;
                if (p >= 50) return COLORS.lime;
                if (p >= 30) return COLORS.yellow;
                return COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: sortedProgress.map(p => `${p}%`),
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

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 2: Tiempo dedicado por alumno - Barras
// ============================================
async function initChartTiempoAlumno() {
    const chartId = 'chartTiempoAlumno';
    showLoading(chartId);

    const apiData = await fetchStudentTime();
    if (!apiData) {
        showError(chartId, 'Error al cargar tiempo de alumnos');
        return;
    }

    const { students, time } = apiData;

    if (!students || students.length === 0) {
        showEmpty(chartId, 'No hay datos de tiempo disponibles');
        return;
    }

    // Sort by time descending and take top 10
    const sorted = students.map((name, i) => ({ name, time: time[i] }))
        .sort((a, b) => b.time - a.time)
        .slice(0, 10);

    const names = sorted.map(s => s.name);
    const timeValues = sorted.map(s => s.time);

    const data = [{
        x: names,
        y: timeValues,
        type: 'bar',
        marker: {
            color: timeValues.map((t, i) => {
                const ratio = i / timeValues.length;
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

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 3: Actividades completadas por clase - Barras apiladas
// ============================================
async function initChartActividadesClase() {
    const chartId = 'chartActividadesClase';
    showLoading(chartId);

    const apiData = await fetchActivitiesByClass();
    if (!apiData) {
        showError(chartId, 'Error al cargar actividades');
        return;
    }

    const { activities, completed, in_progress, not_started } = apiData;

    if (!activities || activities.length === 0) {
        showEmpty(chartId, 'No hay actividades disponibles');
        return;
    }

    const data = [
        {
            x: activities,
            y: completed,
            type: 'bar',
            name: 'Completadas',
            marker: { color: COLORS.olive },
            hovertemplate: '<b>%{x}</b><br>Completadas: %{y} alumnos<extra></extra>'
        },
        {
            x: activities,
            y: in_progress,
            type: 'bar',
            name: 'En Progreso',
            marker: { color: COLORS.lime },
            hovertemplate: '<b>%{x}</b><br>En Progreso: %{y} alumnos<extra></extra>'
        },
        {
            x: activities,
            y: not_started,
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

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Chart 4: Evolución de la clase - Línea
// ============================================
async function initChartEvolucionClase() {
    const chartId = 'chartEvolucionClase';
    showLoading(chartId);

    const apiData = await fetchClassEvolution();
    if (!apiData) {
        showError(chartId, 'Error al cargar evolución de clase');
        return;
    }

    const { dates, progress, grades } = apiData;

    if (!dates || dates.length === 0) {
        showEmpty(chartId, 'No hay datos de evolución disponibles');
        return;
    }

    // Normalize grades to percentage scale for dual axis
    const gradesNormalized = grades.map(g => g * 10);

    const data = [
        {
            x: dates,
            y: progress,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Progreso (%)',
            line: { color: COLORS.olive, width: 3 },
            marker: { size: 6, color: COLORS.olive },
            hovertemplate: '<b>Progreso</b><br>%{x}<br>%{y:.1f}%<extra></extra>'
        },
        {
            x: dates,
            y: gradesNormalized,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Nota Media',
            yaxis: 'y2',
            line: { color: COLORS.brown, width: 3, dash: 'dot' },
            marker: { size: 6, color: COLORS.brown, symbol: 'square' },
            hovertemplate: '<b>Nota Media</b><br>%{x}<br>' + grades.map(g => g.toFixed(1)).join(',') + '<extra></extra>',
            customdata: grades,
            hovertemplate: '<b>Nota Media</b><br>%{x}<br>%{customdata:.1f}/10<extra></extra>'
        }
    ];

    const layout = {
        ...commonLayout,
        margin: { t: 20, r: 60, b: 60, l: 60 },
        showlegend: false,
        yaxis: {
            ...commonLayout.yaxis,
            title: { text: 'Progreso (%)', font: { size: 12 }, standoff: 10 },
            range: [0, 100]
        },
        yaxis2: {
            title: { text: 'Nota (0-10)', font: { size: 12 }, standoff: 10 },
            overlaying: 'y',
            side: 'right',
            range: [0, 100],
            showgrid: false,
            tickvals: [0, 25, 50, 75, 100],
            ticktext: ['0', '2.5', '5', '7.5', '10']
        },
        xaxis: {
            ...commonLayout.xaxis,
            tickangle: -45,
            tickformat: '%d %b'
        }
    };

    // Clear loading spinner before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, commonConfig);
}

// ============================================
// Update Summary Cards
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
            element.textContent = current + suffix;
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

    const alumnosEl = document.getElementById('alumnosValue');
    if (alumnosEl) animateValue(alumnosEl, 0, summary.total_alumnos, 1200);

    const progresoEl = document.getElementById('progresoValue');
    if (progresoEl) animateValue(progresoEl, 0, summary.progreso_medio, 1300, '%', true);

    const tiempoEl = document.getElementById('tiempoValue');
    if (tiempoEl) animateValue(tiempoEl, 0, summary.tiempo_promedio, 1400, ' min');

    const notaEl = document.getElementById('notaValue');
    if (notaEl) animateValue(notaEl, 0, summary.nota_media, 1500, '', true);

    // Update class name in the summary
    const trendEl = document.querySelector('#alumnosValue').parentElement.querySelector('.summary-trend');
    if (trendEl) {
        trendEl.textContent = summary.clase_nombre;
        trendEl.classList.remove('positive', 'negative');
        trendEl.classList.add('neutral');
    }
}

// ============================================
// Filter Functionality
// ============================================
async function initFilters() {
    // Load classes for dropdown
    const classes = await fetchClasses();
    const claseSelect = document.getElementById('filterClase');

    if (claseSelect && classes.length > 0) {
        // Clear existing options
        claseSelect.innerHTML = '<option value="">Todas las clases</option>';

        // Add classes
        classes.forEach(clase => {
            const option = document.createElement('option');
            option.value = clase.id;
            option.textContent = clase.nombre;
            claseSelect.appendChild(option);
        });

        // Set first class as default
        if (classes.length > 0) {
            claseSelect.value = classes[0].id;
            currentFilters.claseId = classes[0].id;
        }
    }

    // Apply filters button
    const applyBtn = document.getElementById('applyFilters');
    if (applyBtn) {
        applyBtn.addEventListener('click', async () => {
            // Show loading state
            applyBtn.disabled = true;
            const originalText = applyBtn.innerHTML;
            applyBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="animation: spin 1s linear infinite;">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" opacity="0.3"/>
                    <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="2"/>
                </svg>
                Aplicando...
            `;

            const claseSelect = document.getElementById('filterClase');
            const fechasSelect = document.getElementById('filterFechas');

            if (claseSelect) {
                currentFilters.claseId = claseSelect.value || null;
            }

            if (fechasSelect) {
                const value = fechasSelect.value;
                const daysMap = {
                    '7d': 7,
                    '14d': 14,
                    '30d': 30,
                    'trimestre': 90,
                    'curso': 365
                };
                currentFilters.days = daysMap[value] || 7;
            }

            console.log('Applying filters:', currentFilters);

            try {
                // Reload all charts, summary, and students list
                const studentsList = await fetchStudentsList();
                renderStudentsTable(studentsList);

                await Promise.all([
                    updateSummaryCards(),
                    initChartProgresoAlumno(),
                    initChartTiempoAlumno(),
                    initChartActividadesClase(),
                    initChartEvolucionClase()
                ]);

                // Show success feedback
                applyBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    Aplicado
                `;
                setTimeout(() => {
                    applyBtn.innerHTML = originalText;
                    applyBtn.disabled = false;
                }, 1500);
            } catch (error) {
                console.error('Error applying filters:', error);
                applyBtn.innerHTML = originalText;
                applyBtn.disabled = false;
            }
        });
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
// Students List Management
// ============================================

let currentStudentsData = [];

async function fetchStudentsList() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const response = await fetch(`${API_BASE}/students-list?${params}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch students list');
        return await response.json();
    } catch (error) {
        console.error('Error fetching students list:', error);
        return [];
    }
}

function renderStudentsTable(students) {
    currentStudentsData = students;
    const tbody = document.getElementById('studentsTableBody');

    if (!students || students.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="loading-message">
                    No hay alumnos en esta clase
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = students.map(student => {
        const progressClass = student.progreso >= 75 ? 'progress-excellent' :
                             student.progreso >= 50 ? 'progress-good' :
                             student.progreso >= 25 ? 'progress-fair' : 'progress-low';

        const gradeClass = student.nota_media >= 7 ? 'grade-excellent' :
                          student.nota_media >= 5 ? 'grade-good' : 'grade-low';

        return `
            <tr>
                <td><strong>${student.nombre}</strong></td>
                <td>${student.username}</td>
                <td>
                    <div class="progress-wrapper">
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill ${progressClass}" style="width: ${student.progreso}%;"></div>
                        </div>
                        <span class="progress-text ${progressClass}">${student.progreso}%</span>
                    </div>
                </td>
                <td class="text-center">${student.actividades_completadas}</td>
                <td class="text-center">${student.tiempo_total} min</td>
                <td class="text-center grade-cell ${gradeClass}">
                    ${student.nota_media > 0 ? student.nota_media.toFixed(1) : '-'}
                </td>
                <td class="text-center text-muted text-small">
                    ${student.ultima_actividad}
                </td>
            </tr>
        `;
    }).join('');
}

async function exportToCSV() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const token = localStorage.getItem('authToken');
        const response = await fetch(`${API_BASE}/export-students-csv?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to export CSV');
        }

        // Get the blob from response
        const blob = await response.blob();

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `alumnos_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting CSV:', error);
        alert('Error al exportar CSV. Por favor, inténtalo de nuevo.');
    }
}

async function exportToExcel() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const token = localStorage.getItem('authToken');
        const response = await fetch(`${API_BASE}/export-students-excel?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to export Excel');
        }

        // Get the blob from response
        const blob = await response.blob();

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `alumnos_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting Excel:', error);
        alert('Error al exportar Excel. Por favor, inténtalo de nuevo.');
    }
}

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
// Initialize
// ============================================
async function init() {
    // Check authentication first
    if (window.authManager) {
        window.authManager.protectPage();
    }

    console.log('Dashboard Teacher page initialized');

    // Set up logout button
    const logoutButton = document.querySelector('.navbar-logout');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }

    // Display user name in navbar
    const userName = localStorage.getItem('userName');
    const userNameEl = document.querySelector('.navbar-user-name');
    if (userNameEl && userName) {
        userNameEl.textContent = `¡Hola ${userName}!`;
    }

    // Initialize filters first
    await initFilters();

    // Set up export buttons
    const exportCSVBtn = document.getElementById('exportCSV');
    if (exportCSVBtn) {
        exportCSVBtn.addEventListener('click', exportToCSV);
    }

    const exportExcelBtn = document.getElementById('exportExcel');
    if (exportExcelBtn) {
        exportExcelBtn.addEventListener('click', exportToExcel);
    }

    // Load students list
    const studentsList = await fetchStudentsList();
    renderStudentsTable(studentsList);

    // Load all data
    if (typeof Plotly !== 'undefined') {
        await Promise.all([
            updateSummaryCards(),
            initChartProgresoAlumno(),
            initChartTiempoAlumno(),
            initChartActividadesClase(),
            initChartEvolucionClase()
        ]);
    } else {
        console.error('Plotly is not loaded');
    }

    window.addEventListener('resize', debounce(handleResize, 250));
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
