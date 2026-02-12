/**
 * Core Utilities - Shared utility functions
 * Extracted from dashboard-teacher.js, statistics.js, etc.
 */

/**
 * Animate a numeric value with easing
 * @param {HTMLElement} element - Target element to update
 * @param {number} start - Starting value
 * @param {number} end - Ending value
 * @param {number} duration - Animation duration in milliseconds
 * @param {string} suffix - Optional suffix (e.g., '%', ' min')
 * @param {boolean} isFloat - Whether to use decimal formatting (e.g., 7.5)
 */
window.animateValue = function(element, start, end, duration, suffix = '', isFloat = false) {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic

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
};

/**
 * Debounce function - delays execution until after wait time has elapsed
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
window.debounce = function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

/**
 * Format time in minutes to readable format (e.g., "2h 30min")
 * @param {number} minutes - Time in minutes
 * @returns {string} Formatted time string
 */
window.formatTime = function(minutes) {
    if (!minutes || minutes === 0) return '0 min';

    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);

    if (hours === 0) return `${mins} min`;
    if (mins === 0) return `${hours}h`;
    return `${hours}h ${mins}min`;
};
