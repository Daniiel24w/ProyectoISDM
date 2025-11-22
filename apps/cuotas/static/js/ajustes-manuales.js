$(document).ready(function() {
    let cuotasTable;

    // 1. Manejar la búsqueda del alumno
    $('#form-buscar-alumno').on('submit', function(e) {
        e.preventDefault();
        const termino = $('#search-alumno').val();

        if (!termino) {
            alert('Por favor, ingrese un legajo o DNI.');
            return;
        }

        fetch(`/cuotas/api/buscar-cuotas-alumno/?termino=${termino}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error) });
                }
                return response.json();
            })
            .then(data => {
                // Poblar datos del alumno
                $('#info-nombre').text(data.alumno.nombre_completo);
                $('#info-legajo').text(data.alumno.legajo);
                $('#info-dni').text(data.alumno.dni);
                $('#info-carrera').text(data.alumno.carrera);
                $('#info-plan').text(data.alumno.plan_actual);
                $('#info-email').text(data.alumno.email);

                // Inicializar o recargar DataTable
                if (cuotasTable) {
                    cuotasTable.clear().rows.add(data.cuotas).draw();
                } else {
                    cuotasTable = $('#tabla-cuotas-alumno').DataTable({
                        data: data.cuotas,
                        columns: [
                            { data: 'id' },
                            { data: 'periodo' },
                            { data: 'plan_pago' },
                            { data: 'monto_original' },
                            { data: 'monto_final' },
                            { data: 'vencimiento_original' },
                            { data: 'vencimiento_final' },
                            { data: 'estado' },
                            { 
                                data: null,
                                render: function(data, type, row) {
                                    if (row.es_ajustable) {
                                        return `<button class="btn btn-info btn-sm btn-ajustar" data-id="${row.id}" data-periodo="${row.periodo}">Ajustar</button>`;
                                    }
                                    return `<button class="btn btn-secondary btn-sm" disabled>Ajustar</button>`;
                                }
                            }
                        ],
                        language: { /* Puedes copiar el objeto de idioma de reportes.js aquí */ },
                        order: [[0, 'desc']]
                    });
                }

                // Mostrar la sección de resultados
                $('#resultados-busqueda').slideDown();
            })
            .catch(error => {
                alert(`Error: ${error.message}`);
                $('#resultados-busqueda').slideUp();
            });
    });

    // 2. Abrir y poblar el modal de ajuste
    $('#tabla-cuotas-alumno tbody').on('click', '.btn-ajustar', function() {
        const cuotaId = $(this).data('id');
        const periodo = $(this).data('periodo');

        $('#ajuste-cuota-id').val(cuotaId);
        $('#ajustarVencimientoLabel').text(`Ajustar Cuota (Período: ${periodo})`);
        
        // Limpiar formulario del modal
        $('#form-ajustar-cuota')[0].reset();

        const ajustarModal = new bootstrap.Modal(document.getElementById('ajustarVencimientoModal'));
        ajustarModal.show();
    });

    // 3. Guardar el ajuste
    $('#form-ajustar-cuota').on('submit', function(e) {
        e.preventDefault();
        const cuotaId = $('#ajuste-cuota-id').val();
        const nuevoVencimiento = $('#nueva-fecha-vencimiento').val();
        const nuevoMonto = $('#nuevo-monto').val();
        const motivo = $('#motivo-ajuste').val();

        if (!motivo) {
            alert('El motivo del ajuste es obligatorio.');
            return;
        }

        if (!nuevoVencimiento && !nuevoMonto) {
            alert('Debe especificar al menos un nuevo vencimiento o un nuevo monto.');
            return;
        }

        const payload = {
            vencimiento: nuevoVencimiento,
            monto: nuevoMonto,
            motivo: motivo
        };

        fetch(`/cuotas/api/ajustar-cuota/${cuotaId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Reutilizamos la función de reportes.js
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json().then(data => ({ok: response.ok, data})))
        .then(({ok, data}) => {
            if (!ok) {
                throw new Error(data.error);
            }
            alert(data.message);
            bootstrap.Modal.getInstance(document.getElementById('ajustarVencimientoModal')).hide();
            // Disparar de nuevo la búsqueda para refrescar la tabla
            $('#form-buscar-alumno').trigger('submit');
        })
        .catch(error => {
            alert(`Error al guardar el ajuste: ${error.message}`);
        });
    });

    // Función para obtener el token CSRF (puedes ponerla en un archivo JS global)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});