"""Configuración de los modelos en el administrador oficial de Django."""
from django.contrib import admin

from .models import Cliente, DetalleFactura, Factura, Producto, Proveedor, Trabajador


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("id_proveedor", "nombre_empresa", "telefono")
    search_fields = ("nombre_empresa", "telefono")


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id_cliente", "nombre", "cedula_o_rif", "telefono")
    search_fields = ("nombre", "cedula_o_rif", "telefono")


@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ("id_trabajador", "nombre", "cargo")
    search_fields = ("nombre", "cargo")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id_producto", "marca", "precio_actual", "stock", "id_proveedor")
    list_filter = ("id_proveedor",)
    search_fields = ("marca",)
    list_select_related = ("id_proveedor",)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    """Las facturas se crean por el flujo de venta para controlar las existencias."""
    list_display = ("id_factura", "fecha", "id_cliente", "id_trabajador", "total_factura")
    list_filter = ("fecha",)
    search_fields = ("=id_factura", "id_cliente__nombre", "id_cliente__cedula_o_rif")
    list_select_related = ("id_cliente", "id_trabajador")
    readonly_fields = ("fecha", "total_factura", "id_cliente", "id_trabajador")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    """Los detalles también son de solo lectura para preservar el historial de ventas."""
    list_display = ("id_detalle", "id_factura", "id_producto", "cantidad", "precio_vendido", "mostrar_subtotal")
    list_select_related = ("id_factura", "id_producto")
    search_fields = ("=id_factura__id_factura", "id_producto__marca")
    readonly_fields = ("cantidad", "precio_vendido", "id_factura", "id_producto")

    @admin.display(description="Subtotal")
    def mostrar_subtotal(self, obj):
        return obj.subtotal

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
