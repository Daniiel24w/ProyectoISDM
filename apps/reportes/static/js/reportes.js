$(document).ready(function() {
    $('#lotesTable').DataTable({
        "processing": true,
        "serverSide": false, // Lo ponemos en false porque cargamos todos los datos de una vez
        "ajax": {
            "url": "/reportes/api/lotes-data/", // La URL que creamos
            "type": "GET",
            "dataSrc": "data" // La clave que contiene la lista de lotes en el JSON
        },
        "columns": [
            { "data": "id" },
            { "data": "fecha_creacion" },
            { "data": "usuario" },
            { "data": "plan_pago" },
            { "data": "estado" },
            { "data": "fecha_programacion" },
            { "data": "monto_total" },
            { "data": "acciones", "orderable": false, "searchable": false }
        ],
        "language": {
            "processing": "Procesando...",
            "lengthMenu": "Mostrar _MENU_ registros",
            "zeroRecords": "No se encontraron resultados",
            "emptyTable": "Ningún dato disponible en esta tabla",
            "info": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "infoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
            "infoFiltered": "(filtrado de un total de _MAX_ registros)",
            "search": "Buscar:",
            "loadingRecords": "Cargando...",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            },
            "aria": {
                "sortAscending": ": Activar para ordenar la columna de manera ascendente",
                "sortDescending": ": Activar para ordenar la columna de manera descendente"
            },
            "buttons": {
                "copy": "Copiar"
            }
        },
        "order": [[0, 'desc']] // Ordenar por ID descendente por defecto
    });
});

function verResumen(loteId) {    
    fetch(`/reportes/api/lote/${loteId}/detalles/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Rellenar información general
            document.getElementById('resumenModalLabel').textContent = `Resumen del Lote #${loteId}`;
            document.getElementById('detalle-plan-nombre').textContent = data.plan_nombre;
            document.getElementById('detalle-carrera-nombre').textContent = data.carrera_nombre;
            document.getElementById('detalle-carrera-modalidad').textContent = data.carrera_modalidad;
            document.getElementById('detalle-cantidad-cuotas').textContent = data.cantidad_cuotas;
            document.getElementById('detalle-valor-cuota').textContent = data.valor_cuota;
            document.getElementById('detalle-mora').textContent = data.mora;
            document.getElementById('detalle-fecha-creacion').textContent = data.fecha_creacion;
            document.getElementById('detalle-creado-por').textContent = data.creado_por;
            document.getElementById('detalle-monto-estimado').textContent = data.monto_total_estimado;

            // Guardar el ID del lote en el botón de exportar
            const exportBtn = document.getElementById('exportar-pdf-btn');
            exportBtn.dataset.loteId = loteId;

            // Rellenar tabla de alumnos y cuotas
            const tbody = document.getElementById('tabla-alumnos-cuotas-body');
            tbody.innerHTML = ''; // Limpiar tabla
            data.alumnos.forEach(cuota => {
                const row = `
                    <tr data-search-text="${cuota.legajo} ${cuota.apellido.toLowerCase()} ${cuota.nombre.toLowerCase()}">
                        <td>${cuota.legajo}</td>
                        <td>${cuota.apellido}, ${cuota.nombre}</td>
                        <td>${cuota.periodo}</td>
                        <td>${cuota.vencimiento}</td>
                        <td>${cuota.monto_cuota}</td>
                        <td><span class="badge bg-warning text-dark">${cuota.estado}</span></td>
                    </tr>
                `;
                tbody.insertAdjacentHTML('beforeend', row);
            });

            // Mostrar el modal
            const resumenModal = new bootstrap.Modal(document.getElementById('resumenModal'));
            resumenModal.show();
        })
        .catch(error => console.error('Error al cargar los detalles del lote:', error));
}

// Buscador dentro del modal
document.getElementById('buscador-alumnos-modal').addEventListener('keyup', function() {
    const searchTerm = this.value.toLowerCase();
    document.querySelectorAll('#tabla-alumnos-cuotas-body tr').forEach(row => {
        const rowText = row.dataset.searchText;
        row.style.display = rowText.includes(searchTerm) ? '' : 'none';
    });
});

// Event listener para el botón de exportar a PDF
document.getElementById('exportar-pdf-btn').addEventListener('click', function() {
    const loteId = this.dataset.loteId;
    // Simplemente redirigimos a la URL de exportación, el navegador se encargará de la descarga
    window.location.href = `/reportes/lote/${loteId}/exportar-pdf/`;
});

function prepararAnulacion(loteId) {
    // Pone el ID del lote en el título y en el botón de confirmar
    document.getElementById('anularModalLabel').textContent = `Anular Lote #${loteId}`;
    const confirmBtn = document.getElementById('confirmarAnulacion');
    confirmBtn.dataset.loteId = loteId; // Guardamos el ID en el botón

    const anularModal = new bootstrap.Modal(document.getElementById('anularModal'));
    anularModal.show();
}

// Función para obtener el valor de la cookie CSRF
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

document.getElementById('confirmarAnulacion').addEventListener('click', function() {
    const loteId = this.dataset.loteId;
    const motivo = document.getElementById('motivoAnulacion').value;
    fetch(`/reportes/api/lote/${loteId}/anular/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ motivo: motivo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            bootstrap.Modal.getInstance(document.getElementById('anularModal')).hide();
            $('#lotesTable').DataTable().ajax.reload(); // Recargar la tabla
        } else {
            alert('Error al anular el lote: ' + data.message);
        }
    });
});