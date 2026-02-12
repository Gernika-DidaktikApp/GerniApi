/**
 * UI Utilities - Shared UI helper functions
 * Extracted from dashboard-teacher.js, statistics.js, etc.
 */

/**
 * Show loading spinner on a chart container
 * @param {string} chartId - ID of the chart container
 */
window.showLoading = function(chartId) {
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
};

/**
 * Show error message on a chart container
 * @param {string} chartId - ID of the chart container
 * @param {string} message - Error message to display (optional)
 */
window.showError = function(chartId, message = null) {
    if (!message) message = 'Error al cargar datos';
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
};

/**
 * Show empty state message on a chart container
 * @param {string} chartId - ID of the chart container
 * @param {string} message - Empty state message to display (optional)
 */
window.showEmpty = function(chartId, message = null) {
    if (!message) message = 'No hay datos disponibles';
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
};

// Add spinner animation to the page (auto-execute)
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

/**
 * Initialize navbar mobile menu toggle (auto-execute)
 */
(function initNavbarToggle() {
    // Use DOMContentLoaded to ensure elements are available
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupNavbar);
    } else {
        setupNavbar();
    }

    function setupNavbar() {
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
    }
})();
