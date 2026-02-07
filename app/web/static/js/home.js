/**
 * Home Page JavaScript
 * Handles counter animations and fetches real statistics
 */

// ============================================
// DOM Elements
// ============================================
const statCards = document.querySelectorAll('.stat-card');

// ============================================
// State Management
// ============================================
let hasAnimatedStats = false;
let statsData = {
    totalUsers: 0,
    minutesPlayed: 0,
    eventsCompleted: 0
};

// ============================================
// API Functions
// ============================================

/**
 * Fetches real statistics from the API
 */
async function fetchRealStats() {
    try {
        // Fetch user statistics
        const userStatsResponse = await fetch('/api/statistics/summary');
        const userStats = await userStatsResponse.json();

        // Fetch gameplay statistics
        const gameplayStatsResponse = await fetch('/api/statistics/gameplay/summary');
        const gameplayStats = await gameplayStatsResponse.json();

        // Calculate total minutes from actividades progreso
        const minutesResponse = await fetch('/api/teacher/dashboard/summary?days=36500'); // All time
        const minutesData = await minutesResponse.json();

        // Update stats data
        statsData.totalUsers = userStats.total_users || 0;
        statsData.minutesPlayed = Math.round((minutesData.tiempo_total_minutos || 0));
        statsData.eventsCompleted = gameplayStats.actividades_completadas || 0;

        console.log('Real stats loaded:', statsData);
        return true;
    } catch (error) {
        console.error('Error fetching stats:', error);
        // Use fallback values if API fails
        statsData.totalUsers = 0;
        statsData.minutesPlayed = 0;
        statsData.eventsCompleted = 0;
        return false;
    }
}

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
            element.textContent = '+' + formatted;
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
 * Animates all stat counters with real data
 */
function animateStats() {
    const stats = [
        statsData.totalUsers,
        statsData.minutesPlayed,
        statsData.eventsCompleted
    ];

    statCards.forEach((card, index) => {
        const numberElement = card.querySelector('.stat-number');
        const target = stats[index];

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
async function init() {
    console.log('Home page initialized');

    // Fetch real statistics first
    await fetchRealStats();

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
