/**
 * Gallery and Message Wall JavaScript
 * Handles loading and displaying student images and messages
 */

const API_BASE = '/api/teacher/dashboard';
let currentClassFilter = '';

// DOM Elements
const classFilter = document.getElementById('classFilter');
const galleryGrid = document.getElementById('galleryGrid');
const messagesWall = document.getElementById('messagesWall');
const galleryCount = document.getElementById('galleryCount');
const messagesCount = document.getElementById('messagesCount');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalInfo = document.getElementById('modalInfo');
const modalClose = document.getElementById('modalClose');
const modalBackdrop = document.getElementById('modalBackdrop');

// Get JWT token
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadClasses();
    loadGallery();
    loadMessages();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Tab switching
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });

    // Class filter
    classFilter.addEventListener('change', (e) => {
        currentClassFilter = e.target.value;
        loadGallery();
        loadMessages();
    });

    // Modal close
    modalClose.addEventListener('click', closeModal);
    modalBackdrop.addEventListener('click', closeModal);

    // Keyboard navigation for modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && imageModal.classList.contains('active')) {
            closeModal();
        }
    });
}

// Switch Tabs
function switchTab(tabName) {
    // Update buttons
    tabButtons.forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Update content
    tabContents.forEach(content => {
        if (content.id === `${tabName}Content`) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

// Load Classes for Filter
async function loadClasses() {
    const token = getAuthToken();
    if (!token) {
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/classes`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load classes');

        const classes = await response.json();

        // Populate class filter
        classFilter.innerHTML = `<option value="">${window.i18n.filter.all_classes}</option>`;
        classes.forEach(clase => {
            const option = document.createElement('option');
            option.value = clase.id;
            option.textContent = clase.nombre;
            classFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading classes:', error);
    }
}

// Load Gallery Images
async function loadGallery() {
    const token = getAuthToken();
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Show loading state
    galleryGrid.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>${window.i18n.gallery.loading}</p>
        </div>
    `;

    try {
        const url = currentClassFilter
            ? `${API_BASE}/gallery?clase_id=${currentClassFilter}`
            : `${API_BASE}/gallery`;

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load gallery');

        const images = await response.json();

        // Update count
        galleryCount.textContent = `${images.length} ${images.length === 1 ? window.i18n.gallery.count_singular : window.i18n.gallery.count_plural}`;

        // Render gallery
        if (images.length === 0) {
            galleryGrid.innerHTML = `
                <div class="empty-state">
                    <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke-width="2"/>
                        <circle cx="8.5" cy="8.5" r="1.5"/>
                        <polyline points="21 15 16 10 5 21" stroke-width="2"/>
                    </svg>
                    <h3 class="empty-state-title">${window.i18n.gallery.empty_title}</h3>
                    <p class="empty-state-description">${window.i18n.gallery.empty_description}</p>
                </div>
            `;
        } else {
            galleryGrid.innerHTML = images.map(img => createGalleryItem(img)).join('');

            // Add click handlers
            document.querySelectorAll('.gallery-item').forEach((item, index) => {
                item.addEventListener('click', () => openModal(images[index]));
            });
        }
    } catch (error) {
        console.error('Error loading gallery:', error);
        galleryGrid.innerHTML = `
            <div class="empty-state">
                <h3 class="empty-state-title">${window.i18n.gallery.error_title}</h3>
                <p class="empty-state-description">${window.i18n.gallery.error_description}</p>
            </div>
        `;
    }
}

// Create Gallery Item HTML
function createGalleryItem(image) {
    return `
        <div class="gallery-item">
            <img src="${escapeHtml(image.url)}" alt="Imagen de ${escapeHtml(image.alumno)}" class="gallery-item-image" loading="lazy">
            <div class="gallery-item-info">
                <div class="gallery-item-student">${escapeHtml(image.alumno)}</div>
                <div class="gallery-item-meta">
                    <div class="gallery-item-class">📚 ${escapeHtml(image.clase)}</div>
                    <div class="gallery-item-activity">📝 ${escapeHtml(image.actividad)}</div>
                    <div class="gallery-item-date">📅 ${formatDate(image.fecha)}</div>
                </div>
            </div>
        </div>
    `;
}

// Load Messages
async function loadMessages() {
    const token = getAuthToken();
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Show loading state
    messagesWall.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>${window.i18n.messages.loading}</p>
        </div>
    `;

    try {
        const url = currentClassFilter
            ? `${API_BASE}/message-wall?clase_id=${currentClassFilter}`
            : `${API_BASE}/message-wall`;

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Failed to load messages');

        const messages = await response.json();

        // Update count
        messagesCount.textContent = `${messages.length} ${messages.length === 1 ? window.i18n.messages.count_singular : window.i18n.messages.count_plural}`;

        // Render messages
        if (messages.length === 0) {
            messagesWall.innerHTML = `
                <div class="empty-state">
                    <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <h3 class="empty-state-title">${window.i18n.messages.empty_title}</h3>
                    <p class="empty-state-description">${window.i18n.messages.empty_description}</p>
                </div>
            `;
        } else {
            messagesWall.innerHTML = messages.map(msg => createMessageCard(msg)).join('');
        }
    } catch (error) {
        console.error('Error loading messages:', error);
        messagesWall.innerHTML = `
            <div class="empty-state">
                <h3 class="empty-state-title">${window.i18n.messages.error_title}</h3>
                <p class="empty-state-description">${window.i18n.messages.error_description}</p>
            </div>
        `;
    }
}

// Create Message Card HTML
function createMessageCard(message) {
    return `
        <div class="message-card">
            <div class="message-text">"${escapeHtml(message.mensaje)}"</div>
            <div class="message-footer">
                <div class="message-student">— ${escapeHtml(message.alumno)}</div>
                <div class="message-meta">
                    <div>📚 ${escapeHtml(message.clase)}</div>
                    <div>📝 ${escapeHtml(message.actividad)}</div>
                    <div>📅 ${formatDate(message.fecha)}</div>
                </div>
            </div>
        </div>
    `;
}

// Open Image Modal
function openModal(image) {
    modalImage.src = image.url;
    modalImage.alt = `Imagen de ${image.alumno}`;

    modalInfo.innerHTML = `
        <div style="font-weight: 600; font-size: 1.125rem; margin-bottom: 0.5rem;">${escapeHtml(image.alumno)}</div>
        <div style="color: #6B7A5C; margin-bottom: 0.75rem;">
            📚 ${escapeHtml(image.clase)} • 📝 ${escapeHtml(image.actividad)}
        </div>
        <div style="font-size: 0.875rem; color: #9BA88E;">
            📅 ${formatDate(image.fecha)}
        </div>
    `;

    imageModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Close Modal
function closeModal() {
    imageModal.classList.remove('active');
    document.body.style.overflow = '';
}

// Utility: Format Date
function formatDate(dateString) {
    if (!dateString) return 'Fecha desconocida';

    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Hoy';
    if (diffDays === 1) return 'Ayer';
    if (diffDays < 7) return `Hace ${diffDays} días`;

    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Utility: Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
