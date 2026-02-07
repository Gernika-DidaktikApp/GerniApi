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
        const navbarMenu = document.getElementById('navbarMenu');
        const navbarUserSection = document.querySelector('.navbar-user');
        const navbarContact = document.querySelector('.navbar-contact');
        const navbarUserName = document.querySelector('.navbar-user-name');

        if (!navbarMenu) return;

        if (this.isAuthenticated) {
            // Remove login button
            if (navbarContact) {
                navbarContact.style.display = 'none';
            }

            // Add "Mis Clases" link if it doesn't exist
            const misClasesExists = Array.from(navbarMenu.querySelectorAll('a')).some(
                link => link.textContent.includes('Mi Clase') || link.href.includes('/dashboard/teacher')
            );

            if (!misClasesExists) {
                const misClasesLi = document.createElement('li');
                misClasesLi.className = 'navbar-menu-item';
                misClasesLi.innerHTML = `
                    <a href="/dashboard/teacher" class="navbar-menu-link">
                        Mis Clases
                    </a>
                `;
                navbarMenu.appendChild(misClasesLi);
            }

            // Update user name display
            if (navbarUserName && this.user) {
                navbarUserName.textContent = `Prof. ${this.user.nombre || this.user.username}`;
                navbarUserName.style.display = 'inline-block';
            }

            // Show/create logout button
            if (!navbarUserSection) {
                // Create user section if it doesn't exist
                const userSection = document.createElement('div');
                userSection.className = 'navbar-user';
                userSection.innerHTML = `
                    <a href="#" class="navbar-logout" id="logoutBtn">Salir</a>
                `;

                const navbarContainer = document.querySelector('.navbar-container');
                const navbarToggle = document.querySelector('.navbar-toggle');
                navbarContainer.insertBefore(userSection, navbarToggle);

                // Add logout event listener
                document.getElementById('logoutBtn').addEventListener('click', (e) => {
                    e.preventDefault();
                    this.logout();
                });
            } else {
                navbarUserSection.style.display = 'flex';

                // Ensure logout button has event listener
                const logoutBtn = navbarUserSection.querySelector('.navbar-logout');
                if (logoutBtn) {
                    logoutBtn.onclick = (e) => {
                        e.preventDefault();
                        this.logout();
                    };
                }
            }
        } else {
            // Show login button
            if (navbarContact) {
                navbarContact.style.display = 'inline-block';
            }

            // Hide user section
            if (navbarUserSection) {
                navbarUserSection.style.display = 'none';
            }

            // Hide user name
            if (navbarUserName) {
                navbarUserName.style.display = 'none';
            }

            // Remove "Mis Clases" link
            const misClasesLink = Array.from(navbarMenu.querySelectorAll('a')).find(
                link => link.textContent.includes('Mi Clase') || link.href.includes('/dashboard/teacher')
            );
            if (misClasesLink) {
                misClasesLink.parentElement.remove();
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
        authManager.updateUI();
    });
} else {
    authManager.updateUI();
}

console.log('🔐 Auth Manager initialized:', authManager.isAuthenticated ? 'Authenticated' : 'Not authenticated');
