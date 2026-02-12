/**
 * API Utilities - Shared API helper functions
 * Extracted from dashboard-teacher.js, dashboard-teacher-classes.js
 */

/**
 * Get authentication headers with JWT token
 * @returns {Object} Headers object with Authorization and Content-Type
 */
window.getAuthHeaders = function() {
    const token = localStorage.getItem('authToken');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
};

/**
 * Generic fetch wrapper with error handling
 * @param {string} url - URL to fetch
 * @param {Object} options - Fetch options (method, headers, body, etc.)
 * @returns {Promise<any>} Response data
 */
window.apiFetch = async function(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...window.getAuthHeaders(),
                ...options.headers
            }
        });

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                // Session expired - redirect to login
                localStorage.removeItem('authToken');
                localStorage.removeItem('userName');
                localStorage.removeItem('userUsername');
                window.location.href = '/login';
                throw new Error('Session expired');
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }

        return response;
    } catch (error) {
        logger.log('error', `API Fetch Error: ${url}`, error);
        throw error;
    }
};

/**
 * Download file helper (CSV, Excel, etc.)
 * @param {string} url - URL to download from
 * @param {string} filename - Name for downloaded file
 * @param {string} errorMessage - Error message to show on failure
 */
window.downloadFile = async function(url, filename, errorMessage = 'Error al descargar archivo') {
    try {
        const token = localStorage.getItem('authToken');
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to download file');
        }

        // Get the blob from response
        const blob = await response.blob();

        // Create download link
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
        logger.log('error', 'Download file error', error);
        alert(errorMessage);
    }
};
