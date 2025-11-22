document.addEventListener('DOMContentLoaded', function() {
    const openModalBtn = document.getElementById('open-modal-btn');
    const imageInput = document.getElementById('id_imagen');
    const avatarPreview = document.getElementById('avatar-preview');
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmRegisterModal'));

    const fieldsToValidate = {
        'id_first_name': 'Por favor, ingrese su nombre.',
        'id_last_name': 'Por favor, ingrese su apellido.',
        'id_username': 'Por favor, ingrese un nombre de usuario.',
        'id_email': 'Por favor, ingrese un correo electrónico válido.',
        'id_password1': 'Por favor, ingrese una contraseña.',
        'id_password2': 'Por favor, confirme su contraseña.',
        'id_rol': 'Por favor, seleccione un rol.'
    };

    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                avatarPreview.src = e.target.result;
            }
            reader.readAsDataURL(file);
        }
    });

    openModalBtn.addEventListener('click', function() {
        if (validateForm()) {
            confirmModal.show();
        }
    });

    function validateForm() {
        let isValid = true;

        Object.keys(fieldsToValidate).forEach(fieldId => {
            const input = document.getElementById(fieldId);
            if (input) {
                input.classList.remove('is-invalid');
                let errorDiv = input.nextElementSibling;
                if (input.parentElement.classList.contains('input-group')) {
                    errorDiv = input.parentElement.nextElementSibling;
                }
                if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                    errorDiv.textContent = '';
                }
            }
        });

        Object.entries(fieldsToValidate).forEach(([fieldId, errorMessage]) => {
            const input = document.getElementById(fieldId);
            if (input && input.value.trim() === '') {
                isValid = false;
                input.classList.add('is-invalid');
                let errorDiv = input.nextElementSibling;
                if (input.parentElement.classList.contains('input-group')) {
                    errorDiv = input.parentElement.nextElementSibling;
                }

                if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                    errorDiv.textContent = errorMessage;
                }
            }
        });

        const password1 = document.getElementById('id_password1');
        const password2 = document.getElementById('id_password2');
        if (password1.value && password2.value && password1.value !== password2.value) {
            isValid = false;
            password2.classList.add('is-invalid');
            let errorDiv = password2.nextElementSibling;
            if (password2.parentElement.classList.contains('input-group')) {
                errorDiv = password2.parentElement.nextElementSibling;
            }

            if (errorDiv) {
                errorDiv.textContent = 'Las contraseñas no coinciden.';
            }
        }
        return isValid;
    }
});