from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('cargar_pendientes/', views.cargar_pendientes, name='cargar_pendientes'),
    path('procesar_fichero/', views.procesar_fichero, name='procesar_fichero'),
    path('admin_page/', views.admin_page, name='admin_page')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
