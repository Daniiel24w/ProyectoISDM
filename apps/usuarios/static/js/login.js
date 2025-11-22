document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('id_username');
    const passwordInput = document.getElementById('id_password');
    const alertContainer = document.getElementById('alert-container');

    // Al cargar la página, revisa si el servidor inyectó un mensaje de error.
    if (typeof window.serverLoginError !== 'undefined') {
        showAlert(window.serverLoginError, 'danger');
    }

    loginForm.addEventListener('submit', function(event) {
        // Limpiamos las clases de error de los inputs
        usernameInput.classList.remove('is-invalid');
        passwordInput.classList.remove('is-invalid');

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        let errors = [];

        if (username === '') {
            usernameInput.classList.add('is-invalid');
            errors.push('Por favor, ingrese su nombre de usuario.');
        }

        if (password === '') {
            passwordInput.classList.add('is-invalid');
            errors.push('Por favor, ingrese su contraseña.');
        }

        // Si la validación no pasa, prevenimos el envío del formulario
        if (errors.length > 0) {
            event.preventDefault();
            // Si ambos campos están vacíos, mostramos un mensaje genérico.
            // Si solo uno está vacío, mostramos su mensaje específico.
            const message = errors.length > 1 ? 'Por favor, complete todos los campos.' : errors[0];
            showAlert(message, 'danger');
        }
    });

    /**
     * Muestra una alerta personalizada en el contenedor de alertas.
     * Ahora muestra una Alerta de Bootstrap.
     * @param {string} message El mensaje a mostrar.
     * @param {string} type El tipo de alerta de Bootstrap (e.g., 'danger', 'success').
     */
    function showAlert(message, type = 'danger') {
        // Limpiar alertas anteriores para no acumularlas
        alertContainer.innerHTML = '';

        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        alertContainer.append(wrapper);
    }
});