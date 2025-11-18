document.addEventListener('DOMContentLoaded', function () {
    const tipoRecargoSelect = document.getElementById('tipo-recargo');
    const valorAddon = document.getElementById('valor-addon');

    if (tipoRecargoSelect && valorAddon) {
        tipoRecargoSelect.addEventListener('change', function () {
            if (this.value === 'fijo') {
                valorAddon.textContent = '$';
            } else if (this.value === 'porcentaje') {
                valorAddon.textContent = '%';
            }
        });
    }
});