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

// Color palette loaded from plotly-utils.js (window.CHART_COLORS)

// ============================================
// API Configuration
// ============================================
const API_BASE = '/api/teacher/dashboard';

// Current filters
let currentFilters = {
    claseId: null  // Will be set from dropdown
};

// ============================================
// API Helper Functions
// ============================================
// getAuthHeaders() loaded from api-utils.js

async function fetchClasses() {
    try {
        const response = await fetch(`${API_BASE}/classes`, {
            headers: window.getAuthHeaders()
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
        logger.log('error', 'Error fetching classes', error);
        return [];
    }
}

async function fetchSummary() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const response = await fetch(`${API_BASE}/summary?${params}`, {
            headers: window.getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch summary');
        return await response.json();
    } catch (error) {
        logger.log('error', 'Error fetching summary', error);
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
            headers: window.getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch student progress');
        return await response.json();
    } catch (error) {
        logger.log('error', 'Error fetching student progress', error);
        return null;
    }
}

async function fetchStudentTime() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const response = await fetch(`${API_BASE}/student-time?${params}`, {
            headers: window.getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch student time');
        return await response.json();
    } catch (error) {
        logger.log('error', 'Error fetching student time', error);
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
            headers: window.getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch activities');
        return await response.json();
    } catch (error) {
        logger.log('error', 'Error fetching activities', error);
        return null;
    }
}

async function fetchClassEvolution() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.claseId) {
            params.append('clase_id', currentFilters.claseId);
        }

        const response = await fetch(`${API_BASE}/class-evolution?${params}`, {
            headers: window.getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch class evolution');
        return await response.json();
    } catch (error) {
        logger.log('error', 'Error fetching class evolution', error);
        return null;
    }
}

// ============================================
// Loading State Management
// ============================================
// showLoading(), showError(), showEmpty() loaded from ui-utils.js

// ============================================
// Plotly Chart Configuration
// ============================================
// commonLayout, commonConfig, COLORS loaded from plotly-utils.js

// ============================================
// Chart 1: Progreso por alumno - Barras horizontales
// ============================================
async function initChartProgresoAlumno() {
    const chartId = 'chartProgresoAlumno';
    window.showLoading(chartId);

    const apiData = await fetchStudentProgress();
    if (!apiData) {
        window.showError(chartId, t('dashboard.error_load_student_progress'));
        return;
    }

    const { students, progress } = apiData;

    if (!students || students.length === 0) {
        window.showEmpty(chartId, t('dashboard.no_students'));
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
                if (p >= 75) return window.CHART_COLORS.olive;
                if (p >= 50) return window.CHART_COLORS.lime;
                if (p >= 30) return window.CHART_COLORS.yellow;
                return window.CHART_COLORS.brown;
            }),
            line: { width: 0 }
        },
        text: sortedProgress.map(p => `${p}%`),
        textposition: 'outside',
        textfont: { size: 10, color: window.CHART_COLORS.text },
        hovertemplate: '<b>%{y}</b><br>Progreso: %{x}%<extra></extra>'
    }];

    const layout = window.getCommonPlotlyLayout({
        margin: { t: 10, r: 50, b: 40, l: 140 },
        showlegend: false,
        xaxis: {
            title: { text: 'Progreso (%)', font: { size: 12 } },
            range: [0, 105]
        },
        yaxis: {
            automargin: true,
            tickfont: { size: 10 }
        }
    });

    window.createPlotlyChart(chartId, data, layout);
}

// ============================================
// Chart 2: Tiempo dedicado por alumno - Barras
// ============================================
async function initChartTiempoAlumno() {
    const chartId = 'chartTiempoAlumno';
    window.showLoading(chartId);

    const apiData = await fetchStudentTime();
    if (!apiData) {
        window.showError(chartId, t('dashboard.error_load_student_time'));
        return;
    }

    const { students, time } = apiData;

    if (!students || students.length === 0) {
        window.showEmpty(chartId, t('dashboard.no_time_data'));
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

    const layout = window.getCommonPlotlyLayout({
        margin: { t: 20, r: 20, b: 60, l: 50 },
        showlegend: false,
        yaxis: {
            title: { text: 'Minutos', font: { size: 12 } }
        },
        xaxis: {
            tickangle: -45
        }
    });

    window.createPlotlyChart(chartId, data, layout);
}

// ============================================
// Chart 3: Actividades completadas por clase - Barras apiladas
// ============================================
async function initChartActividadesClase() {
    const chartId = 'chartActividadesClase';
    window.showLoading(chartId);

    const apiData = await fetchActivitiesByClass();
    if (!apiData) {
        window.showError(chartId, t('dashboard.error_load_activities'));
        return;
    }

    const { activities, completed, in_progress, not_started } = apiData;

    if (!activities || activities.length === 0) {
        window.showEmpty(chartId, t('dashboard.no_activities'));
        return;
    }

    // Translate activity names
    const translatedActivities = activities.map(name => translateActivity(name));

    const data = [
        {
            x: translatedActivities,
            y: completed,
            type: 'bar',
            name: 'Completadas',
            marker: { color: window.CHART_COLORS.olive },
            hovertemplate: '<b>%{x}</b><br>Completadas: %{y} alumnos<extra></extra>'
        },
        {
            x: translatedActivities,
            y: in_progress,
            type: 'bar',
            name: 'En Progreso',
            marker: { color: window.CHART_COLORS.lime },
            hovertemplate: '<b>%{x}</b><br>En Progreso: %{y} alumnos<extra></extra>'
        },
        {
            x: translatedActivities,
            y: not_started,
            type: 'bar',
            name: 'Sin Empezar',
            marker: { color: window.CHART_COLORS.yellow },
            hovertemplate: '<b>%{x}</b><br>Sin Empezar: %{y} alumnos<extra></extra>'
        }
    ];

    const layout = window.getCommonPlotlyLayout({
        margin: { t: 20, r: 20, b: 80, l: 50 },
        barmode: 'stack',
        showlegend: false,
        yaxis: {
            title: { text: 'Alumnos', font: { size: 12 } }
        },
        xaxis: {
            tickangle: -30,
            tickfont: { size: 9 }
        }
    });

    window.createPlotlyChart(chartId, data, layout);
}

// ============================================
// Chart 4: Evolución de la clase - Línea
// ============================================
async function initChartEvolucionClase() {
    const chartId = 'chartEvolucionClase';
    window.showLoading(chartId);

    const apiData = await fetchClassEvolution();
    if (!apiData) {
        window.showError(chartId, t('dashboard.error_load_evolution'));
        return;
    }

    const { dates, progress, grades } = apiData;

    if (!dates || dates.length === 0) {
        window.showEmpty(chartId, t('dashboard.no_evolution_data'));
        return;
    }

    // Calcular el máximo de notas para ajustar el eje Y
    const maxGrade = Math.max(...grades, 0);
    const maxGradeRounded = Math.ceil(maxGrade * 1.1); // 10% más para espacio superior

    const data = [
        {
            x: dates,
            y: progress,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Progreso (%)',
            line: { color: window.CHART_COLORS.olive, width: 3 },
            marker: { size: 6, color: window.CHART_COLORS.olive },
            hovertemplate: '<b>Progreso</b><br>%{x}<br>%{y:.1f}%<extra></extra>'
        },
        {
            x: dates,
            y: grades,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Nota Media',
            yaxis: 'y2',
            line: { color: window.CHART_COLORS.brown, width: 3, dash: 'dot' },
            marker: { size: 6, color: window.CHART_COLORS.brown, symbol: 'square' },
            hovertemplate: '<b>Nota Media</b><br>%{x}<br>%{y:.1f}<extra></extra>'
        }
    ];

    const layout = window.getCommonPlotlyLayout({
        margin: { t: 20, r: 60, b: 60, l: 60 },
        showlegend: false,
        yaxis: {
            title: { text: 'Progreso (%)', font: { size: 12 }, standoff: 10 },
            range: [0, 105]
        },
        yaxis2: {
            title: { text: 'Nota Media', font: { size: 12 }, standoff: 10 },
            overlaying: 'y',
            side: 'right',
            range: [0, maxGradeRounded],
            showgrid: false
        },
        xaxis: {
            tickangle: -45,
            tickformat: '%d %b'
        }
    });

    window.createPlotlyChart(chartId, data, layout);
}

// ============================================
// Update Summary Cards
// ============================================
// animateValue() loaded from core-utils.js

async function updateSummaryCards() {
    const summary = await fetchSummary();
    if (!summary) return;

    const alumnosEl = document.getElementById('alumnosValue');
    if (alumnosEl) window.animateValue(alumnosEl, 0, summary.total_alumnos, 1200);

    const progresoEl = document.getElementById('progresoValue');
    if (progresoEl) window.animateValue(progresoEl, 0, summary.progreso_medio, 1300, '%', true);

    const tiempoEl = document.getElementById('tiempoValue');
    if (tiempoEl) window.animateValue(tiempoEl, 0, summary.tiempo_promedio, 1400, ' min');

    const notaEl = document.getElementById('notaValue');
    if (notaEl) window.animateValue(notaEl, 0, summary.nota_media, 1500, '', true);

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
        claseSelect.innerHTML = `<option value="">${t('dashboard.all_classes')}</option>`;

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
                ${t('dashboard.applying')}
            `;

            const claseSelect = document.getElementById('filterClase');

            if (claseSelect) {
                currentFilters.claseId = claseSelect.value || null;
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
                    ${t('dashboard.applied')}
                `;
                setTimeout(() => {
                    applyBtn.innerHTML = originalText;
                    applyBtn.disabled = false;
                }, 1500);
            } catch (error) {
                logger.log('error', 'Error applying filters', error);
                applyBtn.innerHTML = originalText;
                applyBtn.disabled = false;
            }
        });
    }
}

// ============================================
// Window Resize Handler
// ============================================
// debounce() loaded from core-utils.js

function handleResize() {
    const charts = ['chartProgresoAlumno', 'chartTiempoAlumno', 'chartActividadesClase', 'chartEvolucionClase'];
    charts.forEach(chartId => {
        const chartEl = document.getElementById(chartId);
        if (chartEl && chartEl.data) {
            Plotly.Plots.resize(chartEl);
        }
    });
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
            headers: window.getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch students list');
        return await response.json();
    } catch (error) {
        logger.log('error', 'Error fetching students list', error);
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
                    ${t('dashboard.no_students')}
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
    const params = new URLSearchParams();
    if (currentFilters.claseId) {
        params.append('clase_id', currentFilters.claseId);
    }

    const filename = `alumnos_${new Date().toISOString().split('T')[0]}.csv`;
    await window.downloadFile(
        `${API_BASE}/export-students-csv?${params}`,
        filename,
        t('dashboard.error_export_csv')
    );
}

async function exportToExcel() {
    const params = new URLSearchParams();
    if (currentFilters.claseId) {
        params.append('clase_id', currentFilters.claseId);
    }

    const filename = `alumnos_${new Date().toISOString().split('T')[0]}.xlsx`;
    await window.downloadFile(
        `${API_BASE}/export-students-excel?${params}`,
        filename,
        t('dashboard.error_export_excel')
    );
}

// ============================================
// Navbar Mobile Menu Toggle
// ============================================
// Navbar toggle initialized automatically in ui-utils.js

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

    window.addEventListener('resize', window.debounce(handleResize, 250));
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
