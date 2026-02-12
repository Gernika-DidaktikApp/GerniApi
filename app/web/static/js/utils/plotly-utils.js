/**
 * Plotly Utilities - Shared Plotly chart configuration
 * Extracted from dashboard-teacher.js, statistics.js, etc.
 */

/**
 * Standard color palette for the project
 */
window.CHART_COLORS = {
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

/**
 * Get common Plotly layout with optional overrides
 * @param {Object} overrides - Layout properties to override defaults
 * @returns {Object} Plotly layout configuration
 */
window.getCommonPlotlyLayout = function(overrides = {}) {
    const baseLayout = {
        margin: { t: 20, r: 30, b: 50, l: 60 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            family: 'Inter, sans-serif',
            color: window.CHART_COLORS.text
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
            bordercolor: window.CHART_COLORS.olive,
            font: { family: 'Inter, sans-serif', color: window.CHART_COLORS.text }
        }
    };

    // Deep merge overrides with base layout
    return mergeDeep(baseLayout, overrides);
};

/**
 * Get common Plotly config
 * @param {Object} overrides - Config properties to override defaults
 * @returns {Object} Plotly config
 */
window.getCommonPlotlyConfig = function(overrides = {}) {
    return {
        responsive: true,
        displayModeBar: false,
        ...overrides
    };
};

/**
 * Create a Plotly chart with standard configuration
 * @param {string} chartId - ID of the chart container
 * @param {Array} data - Plotly data array
 * @param {Object} layoutOverrides - Layout overrides
 * @param {Object} configOverrides - Config overrides
 */
window.createPlotlyChart = function(chartId, data, layoutOverrides = {}, configOverrides = {}) {
    const layout = window.getCommonPlotlyLayout(layoutOverrides);
    const config = window.getCommonPlotlyConfig(configOverrides);

    // Clear container before rendering
    const container = document.getElementById(chartId);
    if (container) container.innerHTML = '';

    Plotly.newPlot(chartId, data, layout, config);
};

/**
 * Deep merge utility for objects
 * @param {Object} target - Target object
 * @param {Object} source - Source object
 * @returns {Object} Merged object
 */
function mergeDeep(target, source) {
    const output = { ...target };
    if (isObject(target) && isObject(source)) {
        Object.keys(source).forEach(key => {
            if (isObject(source[key])) {
                if (!(key in target)) {
                    output[key] = source[key];
                } else {
                    output[key] = mergeDeep(target[key], source[key]);
                }
            } else {
                output[key] = source[key];
            }
        });
    }
    return output;
}

function isObject(item) {
    return item && typeof item === 'object' && !Array.isArray(item);
}
