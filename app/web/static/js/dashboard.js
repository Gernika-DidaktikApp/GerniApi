/**
 * Dashboard JavaScript
 * Handles navbar toggle and Plotly chart initialization
 */

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
// Plotly Chart Placeholders
// ============================================

/**
 * Example function to initialize a Plotly chart
 * Uncomment and customize when ready to add real data
 */

/*
function initChart1() {
    const data = [{
        x: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        y: [20, 35, 30, 45, 50, 60],
        type: 'scatter',
        mode: 'lines+markers',
        marker: { color: '#6B8E6F' },
        line: { color: '#6B8E6F', width: 3 }
    }];

    const layout = {
        title: '',
        margin: { t: 20, r: 20, b: 40, l: 40 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter, sans-serif' },
        xaxis: { gridcolor: 'rgba(0,0,0,0.05)' },
        yaxis: { gridcolor: 'rgba(0,0,0,0.05)' }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('chart1', data, layout, config);
}

function initChart2() {
    const data = [{
        values: [45, 30, 25],
        labels: ['Completado', 'En Progreso', 'Pendiente'],
        type: 'pie',
        marker: {
            colors: ['#6B8E6F', '#B8C74A', '#8B6F47']
        }
    }];

    const layout = {
        margin: { t: 20, r: 20, b: 20, l: 20 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter, sans-serif' },
        showlegend: true,
        legend: { orientation: 'h', y: -0.1 }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('chart2', data, layout, config);
}

function initChart3() {
    const data = [{
        x: ['A', 'B', 'C', 'D'],
        y: [12, 19, 15, 25],
        type: 'bar',
        marker: { color: '#B8C74A' }
    }];

    const layout = {
        margin: { t: 20, r: 20, b: 40, l: 40 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter, sans-serif' },
        xaxis: { gridcolor: 'rgba(0,0,0,0.05)' },
        yaxis: { gridcolor: 'rgba(0,0,0,0.05)' }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('chart3', data, layout, config);
}

function initChart4() {
    const data = [{
        x: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
        y: [30, 45, 40, 55],
        type: 'scatter',
        fill: 'tozeroy',
        fillcolor: 'rgba(107, 142, 111, 0.2)',
        line: { color: '#6B8E6F', width: 2 }
    }];

    const layout = {
        margin: { t: 20, r: 20, b: 40, l: 40 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter, sans-serif' },
        xaxis: { gridcolor: 'rgba(0,0,0,0.05)' },
        yaxis: { gridcolor: 'rgba(0,0,0,0.05)' }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('chart4', data, layout, config);
}

function initChart5() {
    const data = [{
        type: 'indicator',
        mode: 'gauge+number',
        value: 75,
        gauge: {
            axis: { range: [0, 100] },
            bar: { color: '#6B8E6F' },
            bgcolor: 'rgba(0,0,0,0.05)',
            borderwidth: 0,
            steps: [
                { range: [0, 50], color: 'rgba(184, 199, 74, 0.2)' },
                { range: [50, 100], color: 'rgba(107, 142, 111, 0.2)' }
            ]
        }
    }];

    const layout = {
        margin: { t: 20, r: 20, b: 20, l: 20 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter, sans-serif' }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('chart5', data, layout, config);
}
*/

// ============================================
// Initialize
// ============================================

function init() {
    console.log('Dashboard initialized');

    // Uncomment to initialize example charts
    /*
    if (typeof Plotly !== 'undefined') {
        initChart1();
        initChart2();
        initChart3();
        initChart4();
        initChart5();
    }
    */
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
