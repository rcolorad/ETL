// Función para mostrar el popup de carga
function mostrarPopupCarga() {
    document.getElementById('popupCarga').style.display = 'block';
}

// Función para ocultar el popup de carga
function ocultarPopupCarga() {
    document.getElementById('popupCarga').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('tipo_dato_form');
    const tipoDato = document.getElementById('tipo_dato');
    const ficheros = document.getElementById('ficheros');
    const popupCarga = document.getElementById("popupCarga");

    form.addEventListener('submit', (e) => {
        // Validar que ambos campos tengan un valor seleccionado
        if (!tipoDato.value || !ficheros.value) {
            e.preventDefault(); // Evita que el formulario se envíe
            alert('Debe seleccionar un tipo de dato y un fichero antes de procesar.');
        } else {
            // Mostrar el popup de carga
            mostrarPopupCarga();

            // Detener el formulario para evitar la recarga de la página
            e.preventDefault();

            // Crear un FormData con los datos del formulario
            let formData = new FormData(form);

            // Realizar la solicitud AJAX utilizando fetch
            fetch(procesarFicheroUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                }
            })
            .then(response => response.json())
            .then(data => {
                // Mostrar un mensaje dependiendo de la respuesta
                if (data.status === 'success') {
                    alert(data.message);  // Muestra mensaje de éxito
                    // Recargar la página para actualizar las opciones
                    location.reload();
                } else {
                    alert(data.message);  // Muestra mensaje de error
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("Hubo un error al procesar el archivo.");
            })
            .finally(() => {
                // Ocultar el popup de carga después de la respuesta
                ocultarPopupCarga();
            });
        }
    });
});
