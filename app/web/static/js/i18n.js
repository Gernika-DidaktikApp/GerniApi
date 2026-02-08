/**
 * Sistema de internacionalización (i18n) para JavaScript
 *
 * Proporciona traducciones para contenido dinámico y manejo del selector de idioma.
 *
 * @author Gernibide
 */

const translations = {
    es: {
        errors: {
            generic: "Ha ocurrido un error",
            network: "Error de conexión. Por favor, inténtalo de nuevo.",
            unauthorized: "No autorizado",
            not_found: "No encontrado",
            server_error: "Error del servidor",
            login_failed: "Error al iniciar sesión"
        },
        messages: {
            success: "Operación exitosa",
            loading: "Cargando...",
            no_data: "No hay datos disponibles",
            saving: "Guardando...",
            deleting: "Eliminando...",
            confirm_delete: "¿Estás seguro de que deseas eliminar este elemento?"
        },
        validation: {
            username_required: "El usuario es obligatorio",
            username_min_length: "El usuario debe tener al menos 3 caracteres",
            password_required: "La contraseña es obligatoria",
            password_min_length: "La contraseña debe tener al menos 6 caracteres"
        },
        accessibility: {
            show_password: "Mostrar contraseña",
            hide_password: "Ocultar contraseña"
        },
        charts: {
            days: "días",
            minutes: "minutos",
            min: "min",
            students: "estudiantes",
            completed: "completados",
            in_progress: "en progreso",
            abandoned: "abandonados",
            score: "Puntuación",
            count: "Cantidad",
            avg: "Promedio",
            times_played: "veces jugada",
            average_score: "promedio"
        },
        time: {
            seconds: "segundos",
            minutes: "minutos",
            hours: "horas",
            days: "días",
            weeks: "semanas",
            months: "meses"
        }
    },
    eu: {
        errors: {
            generic: "Errore bat gertatu da",
            network: "Konexio errorea. Mesedez, saiatu berriz.",
            unauthorized: "Baimenik gabe",
            not_found: "Ez da aurkitu",
            server_error: "Zerbitzariaren errorea",
            login_failed: "Saioa hastean errorea"
        },
        messages: {
            success: "Eragiketa arrakastatsua",
            loading: "Kargatzen...",
            no_data: "Ez dago daturik eskuragarri",
            saving: "Gordetzen...",
            deleting: "Ezabatzen...",
            confirm_delete: "Ziur zaude elementu hau ezabatu nahi duzula?"
        },
        validation: {
            username_required: "Erabiltzailea beharrezkoa da",
            username_min_length: "Erabiltzaileak gutxienez 3 karaktere izan behar ditu",
            password_required: "Pasahitza beharrezkoa da",
            password_min_length: "Pasahitzak gutxienez 6 karaktere izan behar ditu"
        },
        accessibility: {
            show_password: "Erakutsi pasahitza",
            hide_password: "Ezkutatu pasahitza"
        },
        charts: {
            days: "egunak",
            minutes: "minutuak",
            min: "min",
            students: "ikasleak",
            completed: "bukatuta",
            in_progress: "abian",
            abandoned: "utzita",
            score: "Puntuazioa",
            count: "Kopurua",
            avg: "Batez bestekoa",
            times_played: "aldiz jolastu",
            average_score: "batez bestekoa"
        },
        time: {
            seconds: "segunduak",
            minutes: "minutuak",
            hours: "orduak",
            days: "egunak",
            weeks: "asteak",
            months: "hilabeteak"
        }
    }
};

/**
 * Get current language from cookie or localStorage
 * @returns {string} Language code ('es' or 'eu')
 */
function getCurrentLanguage() {
    // Priority: cookie > localStorage > default
    const cookieLang = document.cookie
        .split('; ')
        .find(row => row.startsWith('language='))
        ?.split('=')[1];

    return cookieLang || localStorage.getItem('language') || 'es';
}

/**
 * Translate a key to the current language
 * @param {string} key - Dot-separated key (e.g., 'errors.network')
 * @returns {string} Translated string or key if not found
 */
function t(key) {
    const lang = getCurrentLanguage();
    const keys = key.split('.');
    let value = translations[lang];

    for (const k of keys) {
        value = value?.[k];
    }

    return value || key;
}

/**
 * Initialize language switcher
 */
function initLanguageSwitcher() {
    const langSelect = document.getElementById('languageSelect');
    if (!langSelect) return;

    // Set current language as selected
    const currentLang = getCurrentLanguage();
    langSelect.value = currentLang;

    // Handle language change
    langSelect.addEventListener('change', async (e) => {
        const newLang = e.target.value;

        // Save to localStorage
        localStorage.setItem('language', newLang);

        try {
            // Set cookie via API
            await fetch('/api/set-language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ language: newLang })
            });

            // Reload page to apply new language
            window.location.reload();
        } catch (error) {
            console.error('Error setting language:', error);
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLanguageSwitcher);
} else {
    initLanguageSwitcher();
}
