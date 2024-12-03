$(document).ready(function () {
    $('#tipo_dato').change(function () {
        const id_tipo_dato = $(this).val();  // Obtener el ID seleccionado

        if (id_tipo_dato) {
            // Petición AJAX para obtener los ficheros
            $.ajax({
                url: '/cargar_pendientes/',  // URL configurada desde la plantilla
                data: {
                    'id_tipo_dato': id_tipo_dato  // Parámetro enviado al backend
                },
                success: function (data) {
                    // Vaciar y rellenar el select con los ficheros recibidos
                    $('#ficheros').empty();  // Limpia el select de ficheros
                    $('#ficheros').append('<option value="">Seleccione un fichero</option>');  // Opción predeterminada
                    data.forEach(function (fichero) {
                        $('#ficheros').append(`<option value="${fichero.id}">${fichero.fichero}</option>`);
                    });
                },
                error: function () {
                    alert('Ocurrió un error al cargar los ficheros.');  // Manejo de errores
                }
            });
        } else {
            // Si no hay tipo seleccionado, limpia el select de ficheros
            $('#ficheros').empty();
            $('#ficheros').append('<option value="">Seleccione un fichero</option>');
        }
    });
});
