document.addEventListener('DOMContentLoaded', function () {
    // 1. Deshabilitar las opciones de placeholder ("Seleccionar...") en los select
    document.querySelectorAll('select').forEach(function(select) {
        const firstOption = select.querySelector('option[value=""]');
        if (firstOption) {
            firstOption.disabled = true;
        }
    });

    // 2. Lógica para cambiar el símbolo de Mora ($ o %)
    // Django genera los IDs como "id_<nombre_del_campo>"
    const tipoRecargoSelect = document.getElementById('id_tipo_recargo');
    const valorMoraAddon = document.getElementById('valor-addon');

    function actualizarSimboloMora() {
        if (!tipoRecargoSelect || !valorMoraAddon) {
            return;
        }

        const seleccion = tipoRecargoSelect.value;
        if (seleccion === 'fijo') {
            valorMoraAddon.textContent = '$';
        } else if (seleccion === 'porcentaje') {
            valorMoraAddon.textContent = '%';
        }
    }

    if (tipoRecargoSelect) {
        // Llamar una vez al cargar la página para establecer el estado inicial
        actualizarSimboloMora();
        
        // Añadir el listener para que se actualice cada vez que el usuario cambie la opción
        tipoRecargoSelect.addEventListener('change', actualizarSimboloMora);
    }

});