from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from inventario import views

admin.site.site_header = "Inversiones Zambrano | Administración"
admin.site.site_title = "Inversiones Zambrano | Administración"
admin.site.index_title = "Gestión de inventario, ventas y catálogos"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "acceso/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.inicio, name="inicio"),

    path("proveedores/", views.lista_catalogo, {"entidad": "proveedores"}, name="proveedores"),
    path("proveedores/nuevo/", views.formulario_catalogo, {"entidad": "proveedores"}, name="proveedor_crear"),
    path("proveedores/<int:pk>/editar/", views.formulario_catalogo, {"entidad": "proveedores"}, name="proveedor_editar"),
    path("proveedores/<int:pk>/eliminar/", views.eliminar_catalogo, {"entidad": "proveedores"}, name="proveedor_eliminar"),

    path("productos/", views.lista_catalogo, {"entidad": "productos"}, name="productos"),
    path("productos/nuevo/", views.formulario_catalogo, {"entidad": "productos"}, name="producto_crear"),
    path("productos/<int:pk>/editar/", views.formulario_catalogo, {"entidad": "productos"}, name="producto_editar"),
    path("productos/<int:pk>/eliminar/", views.eliminar_catalogo, {"entidad": "productos"}, name="producto_eliminar"),

    path("clientes/", views.lista_catalogo, {"entidad": "clientes"}, name="clientes"),
    path("clientes/nuevo/", views.formulario_catalogo, {"entidad": "clientes"}, name="cliente_crear"),
    path("clientes/<int:pk>/editar/", views.formulario_catalogo, {"entidad": "clientes"}, name="cliente_editar"),
    path("clientes/<int:pk>/eliminar/", views.eliminar_catalogo, {"entidad": "clientes"}, name="cliente_eliminar"),

    path("trabajadores/", views.lista_catalogo, {"entidad": "trabajadores"}, name="trabajadores"),
    path("trabajadores/nuevo/", views.formulario_catalogo, {"entidad": "trabajadores"}, name="trabajador_crear"),
    path("trabajadores/<int:pk>/editar/", views.formulario_catalogo, {"entidad": "trabajadores"}, name="trabajador_editar"),
    path("trabajadores/<int:pk>/eliminar/", views.eliminar_catalogo, {"entidad": "trabajadores"}, name="trabajador_eliminar"),

    path("facturas/", views.lista_facturas, name="facturas"),
    path("facturas/nueva/", views.crear_factura, name="factura_crear"),
    path("facturas/<int:pk>/", views.detalle_factura, name="factura_detalle"),
]
