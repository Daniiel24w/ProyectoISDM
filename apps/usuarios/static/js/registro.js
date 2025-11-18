document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('id_password1');
    const passwordHelpContainer = document.getElementById('password-help-container');

    if (passwordInput && passwordHelpContainer) {
        // Lista de validaciones con sus expresiones regulares y mensajes
        const validations = [
            { regex: /.{8,}/, message: 'Debe contener al menos 8 caracteres.' },
            { regex: /[A-Z]/, message: 'Debe contener al menos una mayúscula.' },
            { regex: /[a-z]/, message: 'Debe contener al menos una minúscula.' },
            { regex: /[0-9]/, message: 'Debe contener al menos un número.' },
            { regex: /[^A-Za-z0-9]/, message: 'Debe contener al menos un símbolo.' }
        ];

        // Generar los elementos de la lista de ayuda
        validations.forEach((validation, index) => {
            const li = document.createElement('li');
            li.id = `validation-rule-${index}`;
            li.textContent = validation.message;
            li.classList.add('password-rule');
            passwordHelpContainer.appendChild(li);
        });

        passwordInput.addEventListener('input', () => {
            const password = passwordInput.value;

            validations.forEach((validation, index) => {
                const ruleElement = document.getElementById(`validation-rule-${index}`);
                if (validation.regex.test(password)) {
                    ruleElement.classList.add('valid');
                    ruleElement.classList.remove('invalid');
                } else {
                    ruleElement.classList.add('invalid');
                    ruleElement.classList.remove('valid');
                }
            });
        });

        // Para los mensajes de error de Django (similitud, etc.)
        // Django los añade en un <ul> con la clase 'errorlist'.
        // Vamos a moverlos a nuestro contenedor.
        const djangoErrorList = passwordInput.parentElement.querySelector('.errorlist');
        if (djangoErrorList) {
            const djangoErrors = djangoErrorList.querySelectorAll('li');
            djangoErrors.forEach(error => {
                const li = document.createElement('li');
                li.textContent = error.textContent;
                li.classList.add('password-rule', 'invalid');
                passwordHelpContainer.appendChild(li);
            });
            djangoErrorList.remove(); // Limpiamos la lista original
        }
    }
});