$(document).ready(function() {
    $('#lotesTable').DataTable({
        "ajax": {
            "url": "/reportes/data/",
            "type": "GET",
            "dataType": "json",
            "dataSrc": "data" // La clave que contiene la lista de lotes en el JSON
        },
        "columns": [
            { "data": "id" },
            { "data": "fecha_ejecucion" },
            { "data": "usuario" },
            { "data": "filtros_aplicados" },
            { 
                "data": "estado",
                "render": function(data, type, row) {
                    // Asignar clases de badge de Bootstrap según el estado
                    let badgeClass = 'bg-secondary';
                    if (data === 'Completado') {
                        badgeClass = 'bg-success';
                    } else if (data === 'Error') {
                        badgeClass = 'bg-danger';
                    } else if (data === 'Pendiente') {
                        badgeClass = 'bg-warning text-dark';
                    } else if (data === 'Procesando') {
                        badgeClass = 'bg-info text-dark';
                    }
                    return `<span class="badge ${badgeClass}">${data}</span>`;
                }
            },
            {
                "data": null, // Columna para los botones de acción
                "orderable": false,
                "searchable": false,
                "render": function(data, type, row) {
                    // Aquí puedes generar los botones dinámicamente
                    // Por ahora, son estáticos pero podrías añadir lógica
                    // basada en el estado del lote (row.estado)
                    return `
                        <button class="btn btn-info btn-sm" title="Ver Resumen">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" title="Anular Lote">
                            <i class="bi bi-trash"></i>
                        </button>
                    `;
                }
            }
        ],
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
        },
        "responsive": true,
        "autoWidth": false,
        "order": [[ 0, "desc" ]] // Ordenar por ID de lote descendente por defecto
    });
});