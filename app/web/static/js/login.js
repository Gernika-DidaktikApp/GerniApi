/**
 * Login Page JavaScript
 * Handles form validation, password visibility toggle, and async form submission
 */

// ============================================
// DOM Elements
// ============================================
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const togglePasswordBtn = document.getElementById('togglePassword');
const submitBtn = document.getElementById('submitBtn');
const btnLoader = document.getElementById('btnLoader');
const usernameError = document.getElementById('usernameError');
const passwordError = document.getElementById('passwordError');
const logoIcon = document.getElementById('logoIcon');

// ============================================
// State Management
// ============================================
let isPasswordVisible = false;
let isSubmitting = false;

// ============================================
// Utility Functions
// ============================================

/**
 * Shows error message for a field
 * @param {HTMLElement} errorElement - Error message element
 * @param {string} message - Error message
 * @param {HTMLElement} inputWrapper - Input wrapper element
 */
function showError(errorElement, message, inputWrapper) {
    errorElement.textContent = message;
    errorElement.classList.add('show');
    inputWrapper.classList.add('error');
}

/**
 * Clears error message for a field
 * @param {HTMLElement} errorElement - Error message element
 * @param {HTMLElement} inputWrapper - Input wrapper element
 */
function clearError(errorElement, inputWrapper) {
    errorElement.textContent = '';
    errorElement.classList.remove('show');
    inputWrapper.classList.remove('error');
}

/**
 * Sets loading state for submit button
 * @param {boolean} loading - Loading state
 */
function setLoadingState(loading) {
    isSubmitting = loading;
    submitBtn.disabled = loading;

    if (loading) {
        submitBtn.classList.add('loading');
    } else {
        submitBtn.classList.remove('loading');
    }
}

/**
 * Animates logo on interaction
 */
function animateLogo() {
    logoIcon.style.transform = 'scale(1.1) rotate(5deg)';
    setTimeout(() => {
        logoIcon.style.transform = 'scale(1) rotate(0deg)';
    }, 300);
}

// ============================================
// Event Handlers
// ============================================

/**
 * Toggles password visibility
 */
function togglePasswordVisibility() {
    isPasswordVisible = !isPasswordVisible;

    if (isPasswordVisible) {
        passwordInput.type = 'text';
        togglePasswordBtn.setAttribute('aria-label', 'Ocultar contraseña');
    } else {
        passwordInput.type = 'password';
        togglePasswordBtn.setAttribute('aria-label', 'Mostrar contraseña');
    }

    // Add subtle animation
    togglePasswordBtn.style.transform = 'scale(0.9)';
    setTimeout(() => {
        togglePasswordBtn.style.transform = 'scale(1)';
    }, 150);
}

/**
 * Validates username field
 * @returns {boolean} - True if valid
 */
function validateUsername() {
    const username = usernameInput.value.trim();
    const inputWrapper = usernameInput.closest('.input-wrapper');

    if (!username) {
        showError(usernameError, 'El usuario es obligatorio', inputWrapper);
        return false;
    }

    if (username.length < 3) {
        showError(usernameError, 'El usuario debe tener al menos 3 caracteres', inputWrapper);
        return false;
    }

    clearError(usernameError, inputWrapper);
    return true;
}

/**
 * Validates password field
 * @returns {boolean} - True if valid
 */
function validatePassword() {
    const password = passwordInput.value;
    const inputWrapper = passwordInput.closest('.input-wrapper');

    if (!password) {
        showError(passwordError, 'La contraseña es obligatoria', inputWrapper);
        return false;
    }

    if (password.length < 6) {
        showError(passwordError, 'La contraseña debe tener al menos 6 caracteres', inputWrapper);
        return false;
    }

    clearError(passwordError, inputWrapper);
    return true;
}

/**
 * Handles form submission
 * @param {Event} event - Submit event
 */
async function handleSubmit(event) {
    event.preventDefault();

    // Prevent double submission
    if (isSubmitting) {
        return;
    }

    // Validate all fields
    const isUsernameValid = validateUsername();
    const isPasswordValid = validatePassword();

    if (!isUsernameValid || !isPasswordValid) {
        // Shake animation for invalid form
        loginForm.style.animation = 'none';
        setTimeout(() => {
            loginForm.style.animation = 'shake 0.5s';
        }, 10);
        return;
    }

    // Set loading state
    setLoadingState(true);
    animateLogo();

    // Prepare form data
    const formData = {
        username: usernameInput.value.trim(),
        password: passwordInput.value
    };

    try {
        const response = await fetch('/api/v1/auth/login-profesor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            // Success - redirect to dashboard
            console.log('Login successful:', data);

            // Store token if provided
            if (data.access_token) {
                localStorage.setItem('authToken', data.access_token);
            }

            // Redirect after short delay for better UX
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 500);
        } else {
            // Handle error response
            throw new Error(data.detail || 'Error al iniciar sesión');
        }
    } catch (error) {
        console.error('Login error:', error);

        // Show error message
        const inputWrapper = passwordInput.closest('.input-wrapper');
        showError(passwordError, error.message || 'Error de conexión. Por favor, inténtalo de nuevo.', inputWrapper);

        // Reset loading state
        setLoadingState(false);
    }
}

/**
 * Clears errors on input
 * @param {Event} event - Input event
 */
function handleInput(event) {
    const input = event.target;
    const inputWrapper = input.closest('.input-wrapper');

    if (input === usernameInput) {
        clearError(usernameError, inputWrapper);
    } else if (input === passwordInput) {
        clearError(passwordError, inputWrapper);
    }
}

// ============================================
// Event Listeners
// ============================================

// Form submission
loginForm.addEventListener('submit', handleSubmit);

// Password visibility toggle
togglePasswordBtn.addEventListener('click', togglePasswordVisibility);

// Input validation on blur
usernameInput.addEventListener('blur', validateUsername);
passwordInput.addEventListener('blur', validatePassword);

// Clear errors on input
usernameInput.addEventListener('input', handleInput);
passwordInput.addEventListener('input', handleInput);

// Logo interaction
logoIcon.addEventListener('click', animateLogo);

// ============================================
// Keyboard Shortcuts
// ============================================

document.addEventListener('keydown', (event) => {
    // Enter key submits form when focused on inputs
    if (event.key === 'Enter' && (document.activeElement === usernameInput || document.activeElement === passwordInput)) {
        handleSubmit(event);
    }
});

// ============================================
// Initialize
// ============================================

/**
 * Initializes the login page
 */
function init() {
    console.log('Login page initialized');

    // Focus username input on load
    setTimeout(() => {
        usernameInput.focus();
    }, 300);

    // Check if user is already logged in
    const authToken = localStorage.getItem('authToken');
    if (authToken) {
        // Verify token validity
        // TODO: Implement token verification
        console.log('User already has token, verifying...');
    }
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// ============================================
// Add shake animation to CSS dynamically
// ============================================
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

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
