/**
 * Dashboard Teacher Classes - JavaScript
 * Gestión de clases y alumnos para profesores
 */

// ============================================
// Configuration
// ============================================
const API_BASE = '/api/teacher/dashboard';
const CLASES_API = '/api/v1/clases';
const USUARIOS_API = '/api/v1/usuarios';

// State
let selectedClassId = null;
let allClasses = [];
let currentStudents = [];

// ============================================
// Authentication Helper
// ============================================
function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// ============================================
// API Calls
// ============================================

/**
 * Limpiar cache del dashboard
 */
async function clearDashboardCache() {
    try {
        const response = await fetch(`${API_BASE}/cache/clear`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            logger.log('warn', 'No se pudo limpiar el cache del dashboard');
        }
    } catch (error) {
        logger.log('warn', 'Error al limpiar cache del dashboard', error);
    }
}

/**
 * Obtener todas las clases del profesor
 */
async function fetchClasses() {
    try {
        const response = await fetch(`${API_BASE}/classes`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                handleLogout();
                throw new Error('Sesión expirada');
            }
            throw new Error('Error al cargar clases');
        }

        allClasses = await response.json();
        return allClasses;
    } catch (error) {
        showNotification('Error al cargar las clases', 'error');
        return [];
    }
}

/**
 * Obtener lista detallada de alumnos de una clase
 */
async function fetchStudents(claseId = null) {
    try {
        const params = claseId ? `?clase_id=${claseId}` : '';
        const response = await fetch(`${API_BASE}/students-list${params}`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Error al cargar alumnos');
        }

        currentStudents = await response.json();
        return currentStudents;
    } catch (error) {
        showNotification('Error al cargar los alumnos', 'error');
        return [];
    }
}

/**
 * Crear nueva clase
 */
async function createClass(nombre) {
    try {
        // Obtener profesor_id del localStorage (guardado como userId)
        const profesorId = localStorage.getItem('userId');

        if (!profesorId) {
            throw new Error('No se encontró información del profesor. Por favor, inicia sesión nuevamente.');
        }

        const response = await fetch(CLASES_API, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                nombre: nombre,
                id_profesor: profesorId
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al crear la clase');
        }

        const newClass = await response.json();
        showNotification('Clase creada exitosamente', 'success');
        return newClass;
    } catch (error) {
        showNotification(error.message, 'error');
        throw error;
    }
}

/**
 * Crear múltiples usuarios desde CSV (transaccional)
 */
async function importStudentsFromCSV(csvData, claseId) {
    try {
        const lines = csvData.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());

        // Validar headers
        const requiredHeaders = ['nombre', 'apellido', 'username'];
        const hasAllHeaders = requiredHeaders.every(h => headers.includes(h));

        if (!hasAllHeaders) {
            throw new Error(`El CSV debe tener las columnas: ${requiredHeaders.join(', ')}`);
        }

        // Procesar todas las líneas
        const usuarios = [];
        for (let i = 1; i < lines.length; i++) {
            if (!lines[i].trim()) continue;

            const values = lines[i].split(',').map(v => v.trim());
            const student = {};

            headers.forEach((header, index) => {
                student[header] = values[index];
            });

            // Validar que los campos requeridos no estén vacíos
            if (!student.nombre || !student.apellido || !student.username) {
                throw new Error(`Línea ${i + 1}: Todos los campos (nombre, apellido, username) son obligatorios`);
            }

            usuarios.push({
                nombre: student.nombre,
                apellido: student.apellido,
                username: student.username,
                password: student.username // Password por defecto = username
            });
        }

        if (usuarios.length === 0) {
            throw new Error('No se encontraron usuarios válidos en el CSV');
        }

        // Enviar bulk request (transaccional: todo o nada)
        const response = await fetch(`${USUARIOS_API}/bulk`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                usuarios: usuarios,
                id_clase: claseId || null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            // Formatear mensaje de error de forma legible
            let errorMessage = 'Error al importar alumnos';
            if (error.detail) {
                if (typeof error.detail === 'string') {
                    errorMessage = error.detail;
                } else if (Array.isArray(error.detail)) {
                    errorMessage = error.detail.map(e => e.msg || e).join(', ');
                }
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        return {
            success: result.usuarios_creados.map(u => u.username),
            total: result.total,
            errors: result.errores
        };
    } catch (error) {
        throw error;
    }
}

/**
 * Descargar plantilla CSV para importar alumnos
 */
function downloadCSVTemplate() {
    // Plantilla con ejemplos y nota sobre contraseñas
    const template = `nombre,apellido,username,password
Juan,Pérez,jperez,jperez
María,García,mgarcia,contraseña123
Carlos,López,clopez,clopez

NOTA: La columna 'password' es OPCIONAL
- Si NO incluyes password, se usará el username como contraseña por defecto
- Si SÍ incluyes password, se usará la contraseña que especifiques
- Los alumnos pueden cambiar su contraseña después del primer login`;

    const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'plantilla_alumnos.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    showNotification('Plantilla descargada', 'success');
}

/**
 * Exportar alumnos a CSV
 */
async function exportStudentsCSV(claseId = null) {
    try {
        const params = claseId ? `?clase_id=${claseId}` : '';
        const response = await fetch(`${API_BASE}/export-students-csv${params}`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Error al exportar CSV');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `alumnos_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showNotification('CSV descargado exitosamente', 'success');
    } catch (error) {
        showNotification('Error al exportar CSV', 'error');
    }
}

/**
 * Exportar alumnos a Excel
 */
async function exportStudentsExcel(claseId = null) {
    try {
        const params = claseId ? `?clase_id=${claseId}` : '';
        const response = await fetch(`${API_BASE}/export-students-excel${params}`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Error al exportar Excel');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `alumnos_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showNotification('Excel descargado exitosamente', 'success');
    } catch (error) {
        showNotification('Error al exportar Excel', 'error');
    }
}

// ============================================
// UI Functions
// ============================================

/**
 * Cargar y renderizar clases en la barra lateral
 */
async function loadClasses(skipFetch = false) {
    const container = document.getElementById('classesListContainer');

    if (!container) return;

    // Solo hacer fetch si no se indica lo contrario
    if (!skipFetch) {
        container.innerHTML = '<div class="loading-message">Cargando clases...</div>';
        await fetchClasses();
    }

    const classes = allClasses;

    if (classes.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M12 6.5v6M12 16.5h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <p>No tienes clases asignadas</p>
                <p style="font-size: 0.875rem;">Crea tu primera clase usando el botón "Crear Clase"</p>
            </div>
        `;
        return;
    }

    container.innerHTML = classes.map(cls => `
        <div class="class-card ${cls.id === selectedClassId ? 'active' : ''}">
            <div onclick="selectClass('${cls.id}')" style="flex: 1; cursor: pointer;">
                <div class="class-card-header">
                    <div class="class-card-icon">${cls.nombre.substring(0, 2).toUpperCase()}</div>
                    <div class="class-card-info">
                        <h3>${cls.nombre}</h3>
                        <p>Código: ${cls.codigo || cls.id.substring(0, 8)}</p>
                    </div>
                </div>
                <div class="class-card-stats">
                    <div class="stat-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8z" stroke-width="2"/>
                        </svg>
                        <span class="stat-value" id="student-count-${cls.id}">0</span> alumnos
                    </div>
                </div>
            </div>
            <button class="btn-delete-class" onclick="event.stopPropagation(); confirmDeleteClass('${cls.id}', '${cls.nombre.replace(/'/g, "\\'")}');" title="Eliminar clase">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                    <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
    `).join('');

    // Actualizar contadores de estudiantes solo si es necesario
    if (classes.length > 0 && classes.length <= 10) {
        // Solo actualizar contadores si hay pocas clases (para mejor performance)
        classes.forEach(async (cls) => {
            const students = await fetchStudents(cls.id);
            const countElement = document.getElementById(`student-count-${cls.id}`);
            if (countElement) {
                countElement.textContent = students.length;
            }
        });
    }
}

/**
 * Seleccionar una clase
 */
async function selectClass(classId) {
    selectedClassId = classId;
    const selectedClass = allClasses.find(c => c.id === classId);

    if (!selectedClass) return;

    // Actualizar UI
    const selectedInfo = document.getElementById('selectedClassInfo');
    if (selectedInfo) {
        selectedInfo.style.display = 'flex';
        document.getElementById('selectedClassName').textContent = selectedClass.nombre;
        document.getElementById('selectedClassCode').textContent = selectedClass.codigo || selectedClass.id.substring(0, 8);
    }

    // Cargar alumnos
    await loadStudents(classId);

    // Actualizar el estado visual de las cards activas
    const container = document.getElementById('classesListContainer');
    if (container) {
        container.querySelectorAll('.class-card').forEach(card => {
            if (card.classList.contains('active')) {
                card.classList.remove('active');
            }
        });
        const activeCard = container.querySelector(`[onclick="selectClass('${classId}')"]`);
        if (activeCard) {
            activeCard.classList.add('active');
        }
    }
}

/**
 * Cargar y renderizar alumnos en la tabla
 */
async function loadStudents(classId) {
    const tbody = document.getElementById('studentsTableBody');

    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="8" class="loading-message">Cargando alumnos...</td></tr>';

    const students = await fetchStudents(classId);

    // Actualizar contador
    const countBadge = document.getElementById('studentCountBadge');
    if (countBadge) {
        countBadge.textContent = `${students.length} alumno${students.length !== 1 ? 's' : ''}`;
    }

    if (students.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-message">No hay alumnos en esta clase</td></tr>';
        return;
    }

    tbody.innerHTML = students.map(student => {
        // Formatear tiempo
        const timeFormatted = formatTime(student.tiempo_total || 0);

        // Formatear fecha
        const lastActivity = student.ultima_actividad && student.ultima_actividad !== 'Nunca'
            ? new Date(student.ultima_actividad).toLocaleDateString('es-ES')
            : 'Sin actividad';

        // Determinar estado
        const isActive = student.ultima_actividad && student.ultima_actividad !== 'Nunca' &&
            (new Date() - new Date(student.ultima_actividad)) < (7 * 24 * 60 * 60 * 1000);

        return `
            <tr>
                <td>
                    <div class="student-name">${student.nombre || 'N/A'}</div>
                    <div class="student-username">@${student.username}</div>
                </td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${student.progreso || 0}%"></div>
                    </div>
                    <div style="margin-top: 0.25rem; font-size: 0.75rem; color: var(--color-text-secondary);">
                        ${student.progreso || 0}%
                    </div>
                </td>
                <td>${student.actividades_completadas || 0}</td>
                <td>${timeFormatted}</td>
                <td style="font-weight: 600;">${(student.nota_media || 0).toFixed(1)}</td>
                <td>${lastActivity}</td>
                <td>
                    <span class="status-badge ${isActive ? 'status-active' : 'status-inactive'}">
                        ${isActive ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td>
                    <button class="btn-remove-student" onclick="confirmRemoveStudent('${student.id}', '${student.nombre.replace(/'/g, "\\'")}');" title="Remover de clase">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                            <path d="M6 18L18 6M6 6l12 12" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Formatear tiempo en minutos a formato legible
 */
function formatTime(minutes) {
    if (!minutes || minutes === 0) return '0 min';

    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);

    if (hours === 0) return `${mins} min`;
    if (mins === 0) return `${hours}h`;
    return `${hours}h ${mins}min`;
}

/**
 * Mostrar notificación
 */
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#D4E7C5' : type === 'error' ? '#FFCDD2' : '#E3F2FD'};
        color: ${type === 'success' ? '#2D3B1C' : type === 'error' ? '#B71C1C' : '#0D47A1'};
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
        font-weight: 500;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Auto-eliminar después de 4 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

/**
 * Copiar código de clase
 */
function copyClassCode() {
    const code = document.getElementById('selectedClassCode')?.textContent;
    if (code) {
        navigator.clipboard.writeText(code).then(() => {
            showNotification('Código copiado al portapapeles', 'success');
        });
    }
}

/**
 * Handle logout
 */
function handleLogout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    window.location.href = '/login';
}

// ============================================
// Modal Handlers
// ============================================

function openModal(modalId) {
    document.getElementById(modalId)?.classList.add('active');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.remove('active');

    // Reset form
    const form = modal.querySelector('form');
    if (form) {
        form.reset();

        // Reset submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            // Restaurar texto original si existe en data-attribute
            if (submitBtn.dataset.originalText) {
                submitBtn.textContent = submitBtn.dataset.originalText;
            }
        }
    }
}

// ============================================
// Form Handlers
// ============================================

async function handleCreateClass(e) {
    e.preventDefault();

    const nombre = document.getElementById('className')?.value;
    const submitBtn = e.target.querySelector('button[type="submit"]');

    if (!nombre) {
        showNotification('Por favor ingresa un nombre para la clase', 'error');
        return;
    }

    // Deshabilitar botón para prevenir doble clic
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.originalText = submitBtn.textContent;
        submitBtn.textContent = 'Creando...';
    }

    try {
        const newClass = await createClass(nombre);
        closeModal('modalCreateClass');

        // IMPORTANTE: Limpiar cache del dashboard antes de recargar
        await clearDashboardCache();

        // Recargar clases desde el servidor (ahora sin cache)
        await loadClasses();

        // Seleccionar la nueva clase automáticamente
        if (newClass && newClass.id) {
            selectedClassId = newClass.id;
            await selectClass(newClass.id);
        }
    } catch (error) {
        // Error ya mostrado en createClass
        // Rehabilitar botón en caso de error
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = submitBtn.dataset.originalText || 'Crear Clase';
        }
    }
}

async function handleImportStudents(e) {
    e.preventDefault();

    if (!selectedClassId) {
        showNotification('Por favor selecciona una clase primero', 'error');
        return;
    }

    const csvFile = document.getElementById('csvFile')?.files[0];

    if (!csvFile) {
        showNotification('Por favor selecciona un archivo CSV', 'error');
        return;
    }

    // Leer archivo
    const csvText = await csvFile.text();

    // Mostrar barra de progreso
    const progressContainer = document.getElementById('importProgress');
    const progressBar = document.getElementById('importProgressBar');
    const progressText = document.getElementById('importProgressText');
    const submitBtn = e.target.querySelector('button[type="submit"]');

    if (progressContainer && progressBar && progressText && submitBtn) {
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';
        progressText.textContent = 'Validando datos...';
        submitBtn.disabled = true;
        submitBtn.dataset.originalText = submitBtn.textContent;
        submitBtn.textContent = 'Importando...';
    }

    try {
        // Simular progreso de validación
        if (progressBar) progressBar.style.width = '30%';
        if (progressText) progressText.textContent = 'Validando datos...';

        await new Promise(resolve => setTimeout(resolve, 300));

        // Progreso de envío
        if (progressBar) progressBar.style.width = '60%';
        if (progressText) progressText.textContent = 'Enviando datos al servidor...';

        const results = await importStudentsFromCSV(csvText, selectedClassId);

        // Completado
        if (progressBar) progressBar.style.width = '100%';
        if (progressText) progressText.textContent = 'Importación completada';

        await new Promise(resolve => setTimeout(resolve, 500));

        // Mensaje de éxito
        let message = `✓ ${results.total} alumno${results.total !== 1 ? 's' : ''} importado${results.total !== 1 ? 's' : ''} exitosamente`;
        if (results.errors && results.errors.length > 0) {
            message += `\n⚠ ${results.errors.length} error${results.errors.length !== 1 ? 'es' : ''}: ${results.errors.join(', ')}`;
        }

        showNotification(message, results.errors && results.errors.length > 0 ? 'error' : 'success');
        closeModal('modalImportStudents');

        // Recargar estudiantes y clases
        if (selectedClassId) {
            await loadStudents(selectedClassId);
            await loadClasses();
        }
    } catch (error) {
        // Error en la importación
        if (progressBar) progressBar.style.width = '100%';
        if (progressBar) progressBar.style.background = '#FFCDD2';
        if (progressText) progressText.textContent = 'Error en la importación';

        showNotification(error.message, 'error');
    } finally {
        // Restaurar estado del botón y ocultar progreso después de un momento
        setTimeout(() => {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = submitBtn.dataset.originalText || 'Importar';
            }
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
            if (progressBar) {
                progressBar.style.width = '0%';
                progressBar.style.background = '';
            }
        }, 2000);
    }
}

// ============================================
// Event Listeners
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Cargar clases al inicio
    loadClasses();

    // Botón copiar código
    document.getElementById('copyCodeBtn')?.addEventListener('click', copyClassCode);

    // Botones de herramientas
    document.getElementById('btnCreateClass')?.addEventListener('click', () => openModal('modalCreateClass'));
    document.getElementById('btnImportStudents')?.addEventListener('click', () => {
        if (!selectedClassId) {
            showNotification('Por favor selecciona una clase primero', 'error');
            return;
        }
        openModal('modalImportStudents');
    });

    // Botón descargar plantilla CSV
    document.getElementById('btnDownloadTemplate')?.addEventListener('click', downloadCSVTemplate);

    // Modales - Cerrar
    document.getElementById('closeCreateClassModal')?.addEventListener('click', () => closeModal('modalCreateClass'));
    document.getElementById('cancelCreateClass')?.addEventListener('click', () => closeModal('modalCreateClass'));
    document.getElementById('closeImportStudentsModal')?.addEventListener('click', () => closeModal('modalImportStudents'));
    document.getElementById('cancelImportStudents')?.addEventListener('click', () => closeModal('modalImportStudents'));

    // Forms
    document.getElementById('formCreateClass')?.addEventListener('submit', handleCreateClass);
    document.getElementById('formImportStudents')?.addEventListener('submit', handleImportStudents);

    // Exportar
    document.getElementById('exportCSV')?.addEventListener('click', () => exportStudentsCSV(selectedClassId));
    document.getElementById('exportExcel')?.addEventListener('click', () => exportStudentsExcel(selectedClassId));

    // Cerrar modal al hacer click fuera
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });
});

// ============================================
// Delete Class & Remove Student Functions
// ============================================

/**
 * Confirmar eliminación de clase
 */
function confirmDeleteClass(claseId, claseNombre) {
    if (confirm(`¿Estás seguro de que quieres eliminar la clase "${claseNombre}"?\n\nLos alumnos NO se eliminarán, solo quedarán sin clase asignada.`)) {
        deleteClass(claseId);
    }
}

/**
 * Eliminar clase
 */
async function deleteClass(claseId) {
    try {
        const response = await fetch(`${CLASES_API}/${claseId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al eliminar la clase');
        }

        showNotification('Clase eliminada exitosamente', 'success');

        // Limpiar cache y recargar
        await clearDashboardCache();
        await loadClasses();

        // Si era la clase seleccionada, limpiar selección
        if (selectedClassId === claseId) {
            selectedClassId = null;
            document.getElementById('selectedClassInfo').style.display = 'none';
            document.getElementById('studentsTableBody').innerHTML = '<tr><td colspan="8" class="loading-message">Selecciona una clase</td></tr>';
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

/**
 * Confirmar remover alumno de clase
 */
function confirmRemoveStudent(studentId, studentName) {
    if (confirm(`¿Remover a "${studentName}" de esta clase?\n\nEl alumno NO se eliminará, solo quedará sin clase asignada.`)) {
        removeStudentFromClass(studentId);
    }
}

/**
 * Remover alumno de clase
 */
async function removeStudentFromClass(studentId) {
    try {
        const response = await fetch(`${USUARIOS_API}/${studentId}/remove-from-class`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al remover alumno');
        }

        showNotification('Alumno removido de la clase', 'success');

        // Limpiar cache y recargar estudiantes
        await clearDashboardCache();
        if (selectedClassId) {
            await loadStudents(selectedClassId);
            await loadClasses(); // Para actualizar el contador
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Exponer funciones globales necesarias
window.selectClass = selectClass;
window.confirmDeleteClass = confirmDeleteClass;
window.confirmRemoveStudent = confirmRemoveStudent;
