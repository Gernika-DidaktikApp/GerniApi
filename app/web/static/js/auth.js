/**
 * Global Authentication Manager
 * Handles user authentication state across all pages
 */

// ============================================
// Authentication State Management
// ============================================

class AuthManager {
    constructor() {
        this.token = null;
        this.user = null;
        this.isAuthenticated = false;
        this.init();
    }

    /**
     * Initialize authentication from localStorage
     */
    init() {
        // Load from localStorage
        this.token = localStorage.getItem('authToken');
        const userName = localStorage.getItem('userName');
        const userUsername = localStorage.getItem('userUsername');
        const userId = localStorage.getItem('userId');

        if (this.token) {
            this.user = {
                nombre: userName,
                username: userUsername,
                id: userId
            };
            this.isAuthenticated = true;
        }

        // Update UI after loading auth state
        this.updateUI();
    }

    /**
     * Check if user is authenticated
     */
    checkAuth() {
        return this.isAuthenticated && this.token;
    }

    /**
     * Get current user
     */
    getUser() {
        return this.user;
    }

    /**
     * Get auth token
     */
    getToken() {
        return this.token;
    }

    /**
     * Set authentication data
     * @param {Object} authData - Authentication data from /auth/login-profesor
     */
    setAuth(authData) {
        this.token = authData.access_token;
        this.user = {
            nombre: authData.nombre,
            username: authData.username,
            id: authData.profesor_id
        };
        this.isAuthenticated = true;

        // Save to localStorage
        localStorage.setItem('authToken', authData.access_token);
        localStorage.setItem('userName', authData.nombre || '');
        localStorage.setItem('userUsername', authData.username || '');
        localStorage.setItem('userId', authData.profesor_id || '');

        this.updateUI();
    }

    /**
     * Clear authentication (logout)
     */
    clearAuth() {
        this.token = null;
        this.user = null;
        this.isAuthenticated = false;

        // Clear localStorage
        localStorage.removeItem('authToken');
        localStorage.removeItem('userName');
        localStorage.removeItem('userUsername');
        localStorage.removeItem('userId');

        this.updateUI();
    }

    /**
     * Logout and redirect
     */
    logout() {
        this.clearAuth();
        window.location.href = '/login';
    }

    /**
     * Update UI based on authentication state
     */
    updateUI() {
        // Update navbar
        this.updateNavbar();

        // Update user display
        this.updateUserDisplay();
    }

    /**
     * Update navbar based on auth state
     */
    updateNavbar() {
        const navbarContact = document.querySelector('.navbar-contact');
        const navbarLogout = document.querySelector('.navbar-logout');
        const navbarUserName = document.querySelector('.navbar-user-name');
        const adminOnlyItems = document.querySelectorAll('.navbar-admin-only');

        // Debug logging
        console.log('🔄 Updating navbar. Auth state:', this.isAuthenticated);
        console.log('   Admin items found:', adminOnlyItems.length);

        if (this.isAuthenticated) {
            console.log('   ✓ User is authenticated - showing admin options');

            // Hide login button, show logout button
            if (navbarContact) {
                navbarContact.classList.add('hidden');
            }
            if (navbarLogout) {
                navbarLogout.classList.remove('hidden');

                // Ensure logout button has event listener
                navbarLogout.onclick = (e) => {
                    e.preventDefault();
                    this.logout();
                };
            }

            // Show admin-only menu items
            adminOnlyItems.forEach(item => {
                item.classList.remove('hidden');
            });

            // Update user name display
            if (navbarUserName && this.user) {
                navbarUserName.textContent = this.user.nombre || this.user.username;
                navbarUserName.classList.remove('hidden');
            }
        } else {
            console.log('   ✗ User is NOT authenticated - hiding admin options');

            // Show login button, hide logout button
            if (navbarContact) {
                navbarContact.classList.remove('hidden');
            }
            if (navbarLogout) {
                navbarLogout.classList.add('hidden');
            }

            // Hide admin-only menu items
            adminOnlyItems.forEach(item => {
                item.classList.add('hidden');
            });

            // Hide user name
            if (navbarUserName) {
                navbarUserName.classList.add('hidden');
            }
        }
    }

    /**
     * Update user display elements
     */
    updateUserDisplay() {
        const userDisplays = document.querySelectorAll('[data-user-name]');
        if (this.user && userDisplays.length > 0) {
            userDisplays.forEach(el => {
                el.textContent = this.user.nombre || this.user.username;
            });
        }
    }

    /**
     * Protect a page - redirect to login if not authenticated
     * Note: Only professors can login to the web interface via /auth/login-profesor
     */
    protectPage() {
        if (!this.checkAuth()) {
            window.location.href = '/login';
        }
    }

    /**
     * Make authenticated API request
     * @param {string} url - API endpoint
     * @param {Object} options - Fetch options
     */
    async fetch(url, options = {}) {
        if (!this.token) {
            throw new Error('No authentication token');
        }

        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${this.token}`
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        // If unauthorized, clear auth and redirect
        if (response.status === 401) {
            this.clearAuth();
            window.location.href = '/login';
            throw new Error('Session expired');
        }

        return response;
    }
}

// ============================================
// Create Global Instance
// ============================================

const authManager = new AuthManager();

// ============================================
// Export for use in other scripts
// ============================================

window.authManager = authManager;

// ============================================
// Auto-initialize on DOM ready
// ============================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('📱 DOM ready - initializing auth UI');
        authManager.updateUI();
    });
} else {
    // DOM already loaded
    console.log('📱 DOM already ready - initializing auth UI');
    authManager.updateUI();
}

console.log('🔐 Auth Manager initialized:', authManager.isAuthenticated ? 'Authenticated' : 'Not authenticated');
