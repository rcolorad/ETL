from django.shortcuts import render, redirect
from django.http import HttpResponse,  JsonResponse
from .etl import main
from django.contrib import messages
from django.db import connection
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os
from .forms import AdministradorForm

ruta_archivo_config = 'etl_app/etl/configs/config.yaml'

def login(request):
    if request.session['is_authenticated']:  # Verificar si el usuario ya inició sesión
        return redirect('home')  # Redirigir al "home"
    
    error_message = ""

    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Comprueba que los campos estén rellenos
        if not username or not password:
            error_message = "Por favor, ingresa tu usuario y contraseña."
        else:
            # Consulta para verificar usuario
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Usuario WHERE username = %s", [username])
                usuario = cursor.fetchone()

            if usuario:
                # usuario[4] tiene almacenada la contraseña del usuario
                db_password = usuario[4]
                if db_password == password:
                    # Guardar los datos del usuario en la sesión
                    request.session['usuario_id'] = usuario[0] # usuario[0] tiene almacenado el id del usuario
                    request.session['username'] = usuario[3] # usuario[3] tiene almacenado el username del usuario
                    request.session['is_authenticated'] = True
                    return redirect('home')
                else:
                    error_message = "La contraseña ingresada es incorrecta."
            else:
                error_message = "El usuario ingresado no existe."

    return render(request, 'login.html', {'error_message': error_message})

def logout(request):
    # Eliminar las claves de sesión personalizadas
    request.session['usuario_id'] = None
    request.session['username'] = None
    request.session['is_authenticated'] = False
    messages.success(request, 'Has cerrado sesión correctamente.')
    
    # Redirigir a la página de login
    return redirect('login')

# Vista para el home
def home(request):
    if not request.session.get('is_authenticated', False):
        messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
        return redirect('login')
    
    datos = main.get_tipo_datos()
    return render(request, 'home.html', {'datos': datos})

def cargar_pendientes(request):
    id_tipo_dato = request.GET.get('id_tipo_dato')
    if id_tipo_dato:
        ficheros = main.get_ficheros_pendientes(id_tipo_dato)
        return JsonResponse(ficheros, safe = False)
    
    messages.error(request, 'Tipo de dato no válido.')
    return redirect('home')

def procesar_fichero(request):
    if request.method == 'POST':
        id_tipo_dato = request.POST.get('tipo_dato')  # Obtener el tipo de dato
        id_fichero = request.POST.get('ficheros')
        
        # Consulta directa a la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Fichero WHERE id = %s", [id_fichero])
            fichero = cursor.fetchone()  # Devuelve None si no encuentra resultados
            
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM TipoDato WHERE id = %s", [id_tipo_dato])
            tipo_dato = cursor.fetchone()  # Devuelve None si no encuentra resultados

        if not fichero or not tipo_dato:
            messages.error(request, 'No se encontró el fichero o el tipo de dato.')
            return redirect('home')
        
        # Definir la ruta para buscar el archivo
        fichero_path = os.path.join(settings.MEDIA_ROOT, 'ficheros', tipo_dato[1], fichero[5])
        
        # Verificar si el fichero realmente existe en la ruta
        if not os.path.exists(fichero_path):
            return JsonResponse({'status': 'error', 'message': 'No se ha podido encontrar el archivo.'})
        
        idUsuario = request.session['usuario_id']
        
        if main.cargar_fichero(fichero_path):
            main.update_fichero(idUsuario, fichero_path, id_fichero)
            return JsonResponse({'status': 'success', 'message': 'Fichero procesado exitosamente.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Error al procesar el fichero.'})

    return JsonResponse({'status': 'error', 'message': 'No se ha enviado ningún fichero.'})

def admin_page(request):
    # Verificar si el usuario está autenticado
    if not request.session.get('is_authenticated', False):
        messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
        return redirect('login')
    
    # Verificar si el usuario tiene permisos de administrador
    if request.session.get('username') != "admin":
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('home')

    if request.method == 'POST':
        form = AdministradorForm(request.POST)
        # Verificar si el formulario es válido
        if form.is_valid():
            # Obtener los datos del formulario
            nombre = form.cleaned_data['nombre']
            siglas = form.cleaned_data['siglas']
            
            # Llamar a la función para insertar el tipo de dato
            resultado = main.insertar_tipo_dato(nombre, siglas)
            
            # Responder con un mensaje indicando que el formulario fue enviado correctamente
            return render(request, 'admin_page.html', {'form': form, 'resultado': resultado})
    else:
        form = AdministradorForm()

    return render(request, 'admin_page.html', {'form': form})