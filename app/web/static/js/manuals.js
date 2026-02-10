/**
 * Manuals and Tutorials Page JavaScript
 * Handles PDF downloads and video interactions
 */

// ============================================
// Logger Integration
// ============================================
const logger = {
    log: (level, message, ...args) => {
        if (window.logger && typeof window.logger.log === 'function') {
            window.logger.log(level, message, ...args);
        } else {
            const logMethod = level === 'error' ? 'error' : level === 'warn' ? 'warn' : 'log';
            console[logMethod](`[${level.toUpperCase()}] ${message}`, ...args);
        }
    }
};

// ============================================
// Download Tracking
// ============================================

/**
 * Track PDF downloads
 */
function trackDownload(filename) {
    logger.log('info', 'Manual downloaded', { filename });
}

/**
 * Handle download button clicks
 */
document.addEventListener('DOMContentLoaded', () => {
    const downloadButtons = document.querySelectorAll('.btn-download');

    downloadButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const href = button.getAttribute('href');
            if (href && !href.startsWith('http')) {
                const filename = href.split('/').pop();
                trackDownload(filename);
            }
        });
    });
});

// ============================================
// Video Player Enhancements
// ============================================

/**
 * Track video play events
 */
function trackVideoPlay(videoElement, videoTitle) {
    logger.log('info', 'Video tutorial played', { title: videoTitle });
}

/**
 * Initialize video players
 */
document.addEventListener('DOMContentLoaded', () => {
    const videos = document.querySelectorAll('.video-container video');

    videos.forEach(video => {
        // Track play events
        video.addEventListener('play', () => {
            const card = video.closest('.video-card');
            const title = card?.querySelector('.video-title')?.textContent || 'Unknown';
            trackVideoPlay(video, title);
        });

        // Add loading indicator
        video.addEventListener('loadstart', () => {
            video.style.opacity = '0.5';
        });

        video.addEventListener('loadeddata', () => {
            video.style.opacity = '1';
        });

        // Handle errors
        video.addEventListener('error', (e) => {
            logger.log('error', 'Video loading error', {
                src: video.currentSrc,
                error: e.message
            });

            // Show error message
            const container = video.closest('.video-container');
            if (container) {
                container.innerHTML = `
                    <div style="
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100%;
                        padding: 2rem;
                        background: #f8f9fa;
                        color: #6B7A5C;
                    ">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-bottom: 1rem; opacity: 0.5;">
                            <circle cx="12" cy="12" r="10" stroke-width="2"/>
                            <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round"/>
                            <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        <p style="text-align: center; font-weight: 500;">
                            ${t ? t('manuals.empty.videos') : 'Video no disponible'}
                        </p>
                    </div>
                `;
            }
        });
    });
});

// ============================================
// Handle Missing Files
// ============================================

/**
 * Check if PDF files exist and show placeholder if not
 */
document.addEventListener('DOMContentLoaded', () => {
    const downloadLinks = document.querySelectorAll('.btn-download');

    downloadLinks.forEach(link => {
        // Check if file exists by making a HEAD request
        const url = link.getAttribute('href');
        if (url && !url.startsWith('http')) {
            fetch(url, { method: 'HEAD' })
                .catch(() => {
                    // If file doesn't exist, disable button and show message
                    link.style.opacity = '0.5';
                    link.style.pointerEvents = 'none';
                    link.innerHTML = `
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <circle cx="12" cy="12" r="10" stroke-width="2"/>
                            <line x1="15" y1="9" x2="9" y2="15" stroke-width="2" stroke-linecap="round"/>
                            <line x1="9" y1="9" x2="15" y2="15" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        ${t ? t('manuals.empty.manuals') : 'Próximamente'}
                    `;
                    logger.log('warn', 'Manual file not found', { url });
                });
        }
    });
});

// ============================================
// Navbar Mobile Menu Toggle (if needed)
// ============================================
const navbarToggle = document.getElementById('navbarToggle');
const navbarMenu = document.getElementById('navbarMenu');

if (navbarToggle && navbarMenu) {
    navbarToggle.addEventListener('click', () => {
        navbarMenu.classList.toggle('active');
        navbarToggle.classList.toggle('active');
    });
}
