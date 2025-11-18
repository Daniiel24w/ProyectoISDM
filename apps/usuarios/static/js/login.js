document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.querySelector('form');
    const usernameInput = document.getElementById('id_username');
    const passwordInput = document.getElementById('id_password');

    loginForm.addEventListener('submit', function (event) {
        let isValid = true;

        // Validación del nombre de usuario
        if (usernameInput.value.trim() === '') {
            isValid = false;
            displayAlert('Por favor, ingrese su nombre de usuario.', 'id_username');
        }

        // Validación de la contraseña
        if (passwordInput.value.trim() === '') {
            isValid = false;
            displayAlert('Por favor, ingrese su contraseña.', 'id_password');
        }

        if (!isValid) {
            event.preventDefault(); // Evita que el formulario se envíe si hay errores
        }
    });

    function displayAlert(message, elementId) {
        // Elimina cualquier alerta existente
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        // Crea el elemento de alerta
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger';
        alertDiv.textContent = message;

        // Inserta la alerta antes del campo de entrada correspondiente
        const inputElement = document.getElementById(elementId);
        inputElement.parentNode.insertBefore(alertDiv, inputElement);
    }
});