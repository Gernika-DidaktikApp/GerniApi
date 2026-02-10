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
        },
        dashboard: {
            applying: "Aplicando...",
            all_classes: "Todas las clases",
            no_students: "No hay alumnos en esta clase",
            no_data: "No hay datos disponibles",
            no_time_data: "No hay datos de tiempo disponibles",
            no_activities: "No hay actividades disponibles",
            no_evolution_data: "No hay datos de evolución disponibles",
            error_load_data: "Error al cargar datos",
            error_load_student_progress: "Error al cargar progreso de alumnos",
            error_load_student_time: "Error al cargar tiempo de alumnos",
            error_load_activities: "Error al cargar actividades",
            error_load_evolution: "Error al cargar evolución de clase",
            error_export_csv: "Error al exportar CSV. Por favor, inténtalo de nuevo.",
            error_export_excel: "Error al exportar Excel. Por favor, inténtalo de nuevo.",
            students: "Alumnos",
            students_singular: "alumno",
            students_plural: "alumnos"
        },
        dashboard_teacher: {
            loading_classes: "Cargando clases...",
            loading_students: "Cargando alumnos...",
            no_classes: "No tienes clases asignadas",
            no_classes_hint: "Crea tu primera clase usando el botón \"Crear Clase\"",
            no_students: "No hay alumnos en esta clase",
            select_class: "Selecciona una clase",
            creating: "Creando...",
            importing: "Importando...",
            validating: "Validando datos...",
            sending: "Enviando datos al servidor...",
            import_completed: "Importación completada",
            import_error: "Error en la importación",
            class_created: "Clase creada exitosamente",
            class_deleted: "Clase eliminada exitosamente",
            student_removed: "Alumno removido de la clase",
            code_copied: "Código copiado al portapapeles",
            csv_downloaded: "CSV descargado exitosamente",
            excel_downloaded: "Excel descargado exitosamente",
            template_downloaded: "Plantilla descargada",
            please_select_class: "Por favor selecciona una clase primero",
            please_select_csv: "Por favor selecciona un archivo CSV",
            please_enter_name: "Por favor ingresa un nombre para la clase",
            imported_successfully: "importado(s) exitosamente",
            session_expired: "Sesión expirada",
            error_load_classes: "Error al cargar las clases",
            error_load_students: "Error al cargar los alumnos",
            error_create_class: "Error al crear la clase",
            error_delete_class: "Error al eliminar la clase",
            error_remove_student: "Error al remover alumno",
            error_export_csv: "Error al exportar CSV",
            error_export_excel: "Error al exportar Excel",
            error_import_students: "Error al importar alumnos",
            error_clear_cache: "Error al limpiar cache del dashboard",
            error_no_teacher_info: "No se encontró información del profesor. Por favor, inicia sesión nuevamente.",
            error_csv_columns: "El CSV debe tener las columnas: nombre, apellido, username",
            error_csv_required_fields: "Todos los campos (nombre, apellido, username) son obligatorios",
            error_no_valid_users: "No se encontraron usuarios válidos en el CSV",
            confirm_delete_class: "¿Estás seguro de que quieres eliminar la clase \"{name}\"?\n\nLos alumnos NO se eliminarán, solo quedarán sin clase asignada.",
            confirm_remove_student: "¿Remover a \"{name}\" de esta clase?\n\nEl alumno NO se eliminará, solo quedará sin clase asignado."
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
        },
        dashboard: {
            applying: "Aplikatzen...",
            all_classes: "Klase guztiak",
            no_students: "Ez dago ikaslerik klase honetan",
            no_data: "Ez dago daturik eskuragarri",
            no_time_data: "Ez dago denboraren daturik eskuragarri",
            no_activities: "Ez dago jarduerarik eskuragarri",
            no_evolution_data: "Ez dago bilakaerarako daturik eskuragarri",
            error_load_data: "Errorea datuak kargatzean",
            error_load_student_progress: "Errorea ikasleen aurrerapena kargatzean",
            error_load_student_time: "Errorea ikasleen denbora kargatzean",
            error_load_activities: "Errorea jarduerak kargatzean",
            error_load_evolution: "Errorea klasearen bilakaera kargatzean",
            error_export_csv: "Errorea CSV esportatzean. Mesedez, saiatu berriro.",
            error_export_excel: "Errorea Excel esportatzean. Mesedez, saiatu berriro.",
            students: "Ikasleak",
            students_singular: "ikasle",
            students_plural: "ikasle"
        },
        dashboard_teacher: {
            loading_classes: "Klaseak kargatzen...",
            loading_students: "Ikasleak kargatzen...",
            no_classes: "Ez dituzu klaseak esleituta",
            no_classes_hint: "Sortu zure lehen klasea \"Klasea Sortu\" botoia erabiliz",
            no_students: "Ez dago ikaslerik klase honetan",
            select_class: "Hautatu klase bat",
            creating: "Sortzen...",
            importing: "Inportatzen...",
            validating: "Datuak balidatzen...",
            sending: "Datuak zerbitzarira bidaltzen...",
            import_completed: "Inportazioa bukatuta",
            import_error: "Errorea inportazioan",
            class_created: "Klasea ondo sortu da",
            class_deleted: "Klasea ondo ezabatu da",
            student_removed: "Ikaslea klasetik kendu da",
            code_copied: "Kodea arbelean kopiatu da",
            csv_downloaded: "CSV ondo deskargatu da",
            excel_downloaded: "Excel ondo deskargatu da",
            template_downloaded: "Txantiloia deskargatuta",
            please_select_class: "Mesedez, hautatu klase bat lehenik",
            please_select_csv: "Mesedez, hautatu CSV fitxategi bat",
            please_enter_name: "Mesedez, sartu klasearentzako izen bat",
            imported_successfully: "ondo inportatuta",
            session_expired: "Saioa iraungi da",
            error_load_classes: "Errorea klaseak kargatzean",
            error_load_students: "Errorea ikasleak kargatzean",
            error_create_class: "Errorea klasea sortzean",
            error_delete_class: "Errorea klasea ezabatzean",
            error_remove_student: "Errorea ikaslea kentzean",
            error_export_csv: "Errorea CSV esportatzean",
            error_export_excel: "Errorea Excel esportatzean",
            error_import_students: "Errorea ikasleak inportatzean",
            error_clear_cache: "Errorea aginte-panelaren cachea garbitzean",
            error_no_teacher_info: "Ez da irakaslearen informaziorik aurkitu. Mesedez, hasi saioa berriro.",
            error_csv_columns: "CSV fitxategiak honako zutabeak izan behar ditu: izena, abizena, erabiltzailea",
            error_csv_required_fields: "Eremu guztiak (izena, abizena, erabiltzailea) derrigorrezkoak dira",
            error_no_valid_users: "Ez da erabiltzaile baliozkorik aurkitu CSV fitxategian",
            confirm_delete_class: "Ziur zaude \"{name}\" klasea ezabatu nahi duzula?\n\nIkasleak EZ dira ezabatuko, bakarrik klaserik gabe geratuko dira.",
            confirm_remove_student: "\"{name}\" klase honetatik kendu?\n\nIkaslea EZ da ezabatuko, bakarrik klaserik gabe geratuko da."
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
