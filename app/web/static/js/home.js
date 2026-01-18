/**
 * Home Page JavaScript
 * Handles counter animations and basic interactions
 */

// ============================================
// DOM Elements
// ============================================
const statCards = document.querySelectorAll('.stat-card');

// ============================================
// State Management
// ============================================
let hasAnimatedStats = false;

// ============================================
// Utility Functions
// ============================================

/**
 * Formats number with thousands separator
 * @param {number} num - Number to format
 * @returns {string} - Formatted number
 */
function formatNumber(num) {
    if (num >= 1000) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }
    return num.toString();
}

/**
 * Animates counter from 0 to target value
 * @param {HTMLElement} element - Element to animate
 * @param {number} target - Target number
 * @param {number} duration - Animation duration in ms
 */
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;

        if (current >= target) {
            current = target;
            clearInterval(timer);
        }

        // Format based on size
        if (target >= 1000) {
            const formatted = formatNumber(Math.floor(current));
            element.textContent = target >= 100000 ? formatted + 'k+' : '+' + formatted;
        } else {
            element.textContent = formatNumber(Math.floor(current));
        }
    }, 16);
}

/**
 * Checks if element is partially in viewport
 * @param {HTMLElement} element - Element to check
 * @param {number} offset - Offset from bottom
 * @returns {boolean} - True if partially in viewport
 */
function isPartiallyInViewport(element, offset = 100) {
    const rect = element.getBoundingClientRect();
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;

    return (
        rect.top <= windowHeight - offset &&
        rect.bottom >= offset
    );
}

// ============================================
// Stats Animation
// ============================================

/**
 * Animates all stat counters
 */
function animateStats() {
    statCards.forEach((card, index) => {
        const numberElement = card.querySelector('.stat-number');
        const target = parseInt(numberElement.getAttribute('data-target'));

        // Stagger animation
        setTimeout(() => {
            animateCounter(numberElement, target, 2000);
        }, index * 150);
    });
}

/**
 * Checks if stats should be animated
 */
function checkStatsAnimation() {
    if (!hasAnimatedStats && statCards.length > 0) {
        const firstCard = statCards[0];
        if (isPartiallyInViewport(firstCard, 150)) {
            animateStats();
            hasAnimatedStats = true;
        }
    }
}

// ============================================
// Event Listeners
// ============================================

// Check stats on scroll
window.addEventListener('scroll', checkStatsAnimation);

// ============================================
// Initialize
// ============================================

/**
 * Initializes the home page
 */
function init() {
    console.log('Home page initialized');

    // Check if stats are already in viewport
    checkStatsAnimation();
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
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
