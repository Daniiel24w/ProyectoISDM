document.addEventListener('DOMContentLoaded', function () {
    const anularModalElement = document.getElementById('anularModal');

    // Solo ejecutar si el modal existe en la página
    if (anularModalElement) {
        // Obtener una instancia del modal de Bootstrap para controlarlo con JS
        const anularModal = new bootstrap.Modal(anularModalElement);

        const confirmarAnulacionBtn = document.getElementById('confirmarAnulacion');
        const motivoAnulacionTextarea = document.getElementById('motivoAnulacion');

        confirmarAnulacionBtn.addEventListener('click', function () {
            const motivo = motivoAnulacionTextarea.value.trim();

            if (motivo === '') {
                alert('Por favor, ingrese un motivo para la anulación.');
                motivoAnulacionTextarea.focus();
                return; // Detiene la ejecución si no hay motivo
            } else {
                // TODO: Aquí irá la lógica para enviar la anulación al backend usando fetch()
                // const loteId = this.dataset.loteId; // Se obtendrá de un atributo data-* en el botón

                console.log('Anulando lote por el siguiente motivo:', motivo);
                alert('El lote ha sido marcado para anulación.');

                // Cierra el modal usando la API de Bootstrap 5
                anularModal.hide();
            }
        });
    }
});