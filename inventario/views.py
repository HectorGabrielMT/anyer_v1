"""Vistas Bootstrap. Los datos de los formularios se procesan sin forms.py."""
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Cliente, DetalleFactura, Factura, Producto, Proveedor, Trabajador


CATALOGOS = {
    "proveedores": {
        "modelo": Proveedor,
        "titulo": "Proveedores",
        "singular": "proveedor",
        "nav": "proveedores",
        "nombre_pk": "id_proveedor",
        "ruta_lista": "proveedores",
        "ruta_crear": "proveedor_crear",
        "ruta_editar": "proveedor_editar",
        "ruta_eliminar": "proveedor_eliminar",
        "orden": "nombre_empresa",
        "busqueda": ("nombre_empresa", "telefono"),
        "campos": [
            {"name": "nombre_empresa", "label": "Nombre de la empresa", "type": "text", "maxlength": 255, "required": True},
            {"name": "telefono", "label": "Teléfono", "type": "tel", "maxlength": 20, "required": True},
        ],
        "columnas": [
            ("ID", lambda item: item.id_proveedor),
            ("Empresa", lambda item: item.nombre_empresa),
            ("Teléfono", lambda item: item.telefono),
        ],
    },
    "productos": {
        "modelo": Producto,
        "titulo": "Productos",
        "singular": "producto",
        "nav": "productos",
        "nombre_pk": "id_producto",
        "ruta_lista": "productos",
        "ruta_crear": "producto_crear",
        "ruta_editar": "producto_editar",
        "ruta_eliminar": "producto_eliminar",
        "orden": "marca",
        "busqueda": ("marca", "id_proveedor__nombre_empresa"),
        "campos": [
            {"name": "marca", "label": "Nombre del aceite / marca", "type": "text", "maxlength": 255, "required": True},
            {"name": "precio_actual", "label": "Precio actual", "type": "number", "step": "0.01", "min": "0", "required": True},
            {"name": "stock", "label": "Existencias", "type": "number", "step": "1", "min": "0", "required": True},
            {"name": "id_proveedor", "label": "Proveedor", "type": "select", "modelo_opciones": Proveedor, "etiqueta_opcion": "nombre_empresa", "required": True},
        ],
        "columnas": [
            ("ID", lambda item: item.id_producto),
            ("Aceite / producto", lambda item: item.marca),
            ("Precio", lambda item: f"{item.precio_actual:.2f}"),
            ("Existencias", lambda item: item.stock),
            ("Proveedor", lambda item: item.id_proveedor.nombre_empresa),
        ],
        "relaciones": ("id_proveedor",),
    },
    "clientes": {
        "modelo": Cliente,
        "titulo": "Clientes",
        "singular": "cliente",
        "nav": "clientes",
        "nombre_pk": "id_cliente",
        "ruta_lista": "clientes",
        "ruta_crear": "cliente_crear",
        "ruta_editar": "cliente_editar",
        "ruta_eliminar": "cliente_eliminar",
        "orden": "nombre",
        "busqueda": ("nombre", "cedula_o_rif", "telefono"),
        "campos": [
            {"name": "nombre", "label": "Nombre o razón social", "type": "text", "maxlength": 255, "required": True},
            {"name": "cedula_o_rif", "label": "Cédula o RIF", "type": "text", "maxlength": 50, "required": True},
            {"name": "telefono", "label": "Teléfono", "type": "tel", "maxlength": 20, "required": True},
        ],
        "columnas": [
            ("ID", lambda item: item.id_cliente),
            ("Nombre", lambda item: item.nombre),
            ("Cédula / RIF", lambda item: item.cedula_o_rif),
            ("Teléfono", lambda item: item.telefono),
        ],
    },
    "trabajadores": {
        "modelo": Trabajador,
        "titulo": "Trabajadores",
        "singular": "trabajador",
        "nav": "trabajadores",
        "nombre_pk": "id_trabajador",
        "ruta_lista": "trabajadores",
        "ruta_crear": "trabajador_crear",
        "ruta_editar": "trabajador_editar",
        "ruta_eliminar": "trabajador_eliminar",
        "orden": "nombre",
        "busqueda": ("nombre", "cargo"),
        "campos": [
            {"name": "nombre", "label": "Nombre completo", "type": "text", "maxlength": 255, "required": True},
            {"name": "cargo", "label": "Cargo", "type": "text", "maxlength": 255, "required": True},
        ],
        "columnas": [
            ("ID", lambda item: item.id_trabajador),
            ("Nombre", lambda item: item.nombre),
            ("Cargo", lambda item: item.cargo),
        ],
    },
}


def _configuracion(entidad):
    """Devuelve la configuración del catálogo o rechaza una ruta desconocida."""
    return CATALOGOS.get(entidad)


def _preparar_campos(config, instancia=None, valores=None, errores=None):
    """Construye los campos HTML y las opciones de sus listas desplegables."""
    campos = []
    valores = valores or {}
    errores = errores or {}
    for campo_original in config["campos"]:
        campo = campo_original.copy()
        nombre = campo["name"]
        if nombre in valores:
            valor = valores[nombre]
        elif instancia is not None:
            valor = getattr(instancia, nombre, "")
            if hasattr(valor, "pk"):
                valor = valor.pk
        else:
            valor = ""
        campo["value"] = "" if valor is None else str(valor)
        campo["error"] = errores.get(nombre)
        if campo["type"] == "select":
            modelo_opciones = campo["modelo_opciones"]
            campo["options"] = [
                {"id": opcion.pk, "label": str(getattr(opcion, campo["etiqueta_opcion"]))}
                for opcion in modelo_opciones.objects.all()
            ]
        campos.append(campo)
    return campos


def _mensaje_validacion(error):
    """Convierte los errores de validación de modelos en mensajes legibles."""
    if hasattr(error, "message_dict"):
        errores = {}
        for campo, mensajes in error.message_dict.items():
            errores[campo] = " ".join(str(mensaje) for mensaje in mensajes)
        return errores
    return {"__all__": " ".join(str(mensaje) for mensaje in error.messages)}


def es_administrador(usuario):
    return usuario.is_superuser or usuario.is_staff


def exigir_administrador(request):
    if not es_administrador(request.user):
        raise PermissionDenied("Esta sección está disponible únicamente para administradores.")


@login_required
def inicio(request):
    productos = Producto.objects.select_related("id_proveedor")
    contexto = {
        "active_nav": "inicio",
        "total_productos": Producto.objects.count(),
        "total_proveedores": Proveedor.objects.count(),
        "total_clientes": Cliente.objects.count(),
        "total_trabajadores": Trabajador.objects.count(),
        "total_facturas": Factura.objects.count(),
        "productos_bajos": productos.filter(stock__lte=5).order_by("stock", "marca")[:6],
        "facturas_recientes": Factura.objects.select_related("id_cliente", "id_trabajador")[:6],
    }
    return render(request, "inventario/inicio.html", contexto)


@login_required
def lista_catalogo(request, entidad):
    config = _configuracion(entidad)
    if config is None:
        return redirect("inicio")
    if entidad != "productos":
        exigir_administrador(request)

    queryset = config["modelo"].objects.all()
    if config.get("relaciones"):
        queryset = queryset.select_related(*config["relaciones"])
    busqueda = request.GET.get("q", "").strip()
    if busqueda:
        filtro = Q()
        for campo in config["busqueda"]:
            filtro |= Q(**{f"{campo}__icontains": busqueda})
        queryset = queryset.filter(filtro)
    queryset = queryset.order_by(config["orden"])

    columnas = [etiqueta for etiqueta, _ in config["columnas"]]
    filas = [
        {
            "id": item.pk,
            "valores": [str(obtener(item)) for _, obtener in config["columnas"]],
            "url_editar": reverse(config["ruta_editar"], kwargs={"pk": item.pk}),
            "url_eliminar": reverse(config["ruta_eliminar"], kwargs={"pk": item.pk}),
        }
        for item in queryset
    ]
    contexto = {
        "active_nav": config["nav"],
        "titulo": config["titulo"],
        "singular": config["singular"],
        "columnas": columnas,
        "filas": filas,
        "buscar": busqueda,
        "url_crear": reverse(config["ruta_crear"]),
        "cantidad": len(filas),
    }
    return render(request, "inventario/catalogo/lista.html", contexto)


@login_required
@require_http_methods(["GET", "POST"])
def formulario_catalogo(request, entidad, pk=None):
    config = _configuracion(entidad)
    if config is None:
        return redirect("inicio")
    if entidad != "productos":
        exigir_administrador(request)

    instancia = get_object_or_404(config["modelo"], pk=pk) if pk is not None else config["modelo"]()
    es_edicion = pk is not None
    errores = {}
    valores = {}
    error_general = ""

    if request.method == "POST":
        for campo in config["campos"]:
            nombre = campo["name"]
            valor = request.POST.get(nombre, "").strip()
            valores[nombre] = valor
            if campo.get("required") and not valor:
                errores[nombre] = "Este campo es obligatorio."
                continue
            if campo["type"] == "select":
                try:
                    relacion = campo["modelo_opciones"].objects.get(pk=valor)
                    setattr(instancia, nombre, relacion)
                except (campo["modelo_opciones"].DoesNotExist, ValueError, TypeError):
                    errores[nombre] = "Seleccione una opción válida."
            else:
                setattr(instancia, nombre, valor)

        if not errores:
            try:
                instancia.full_clean()
            except ValidationError as error:
                errores = _mensaje_validacion(error)
                error_general = errores.pop("__all__", "")

        if not errores and not error_general:
            try:
                instancia.save()
                messages.success(
                    request,
                    f"El registro se {'actualizó' if es_edicion else 'creó'} correctamente.",
                )
                return redirect(config["ruta_lista"])
            except ValidationError as error:
                errores = _mensaje_validacion(error)
                error_general = errores.pop("__all__", "")

    contexto = {
        "active_nav": config["nav"],
        "titulo": f"Editar {config['singular']}" if es_edicion else f"Nueva {config['singular']}",
        "singular": config["singular"],
        "campos": _preparar_campos(config, instancia, valores, errores),
        "errores": errores,
        "error_general": error_general,
        "url_volver": reverse(config["ruta_lista"]),
        "url_formulario": request.path,
        "es_edicion": es_edicion,
    }
    return render(request, "inventario/catalogo/formulario.html", contexto)


@login_required
@require_http_methods(["GET", "POST"])
def eliminar_catalogo(request, entidad, pk):
    config = _configuracion(entidad)
    if config is None:
        return redirect("inicio")
    if entidad != "productos":
        exigir_administrador(request)
    instancia = get_object_or_404(config["modelo"], pk=pk)
    if request.method == "POST":
        try:
            instancia.delete()
            messages.success(request, f"La {config['singular']} se eliminó correctamente.")
            return redirect(config["ruta_lista"])
        except:
            messages.error(
                request,
                "No se puede eliminar este registro porque está relacionado con otros datos.",
            )
            return redirect(config["ruta_lista"])
    return render(
        request,
        "inventario/catalogo/eliminar.html",
        {
            "active_nav": config["nav"],
            "titulo": f"Eliminar {config['singular']}",
            "descripcion": str(instancia),
            "url_volver": reverse(config["ruta_lista"]),
        },
    )


@login_required
def lista_facturas(request):
    facturas = Factura.objects.select_related("id_cliente", "id_trabajador").all()
    contexto = {
        "active_nav": "facturas",
        "facturas": facturas,
    }
    return render(request, "inventario/facturas/lista.html", contexto)


def _contexto_formulario_factura(filas, cliente_seleccionado="", trabajador_seleccionado=""):
    productos = Producto.objects.select_related("id_proveedor").order_by("marca")
    return {
        "active_nav": "facturas",
        "clientes": Cliente.objects.all(),
        "trabajadores": Trabajador.objects.all(),
        "productos": productos,
        "filas": filas,
        "cliente_seleccionado": str(cliente_seleccionado),
        "trabajador_seleccionado": str(trabajador_seleccionado),
    }


@login_required
@require_http_methods(["GET", "POST"])
def crear_factura(request):
    if request.method == "GET":
        filas = [{"producto": "", "cantidad": "1"} for _ in range(3)]
        return render(request, "inventario/facturas/formulario.html", _contexto_formulario_factura(filas))

    producto_ids = request.POST.getlist("productos[]")
    cantidades_recibidas = request.POST.getlist("cantidades[]")
    cantidad_filas = max(len(producto_ids), len(cantidades_recibidas))
    filas = []
    cantidades_por_producto = {}
    error_formulario = ""

    for indice in range(cantidad_filas):
        producto_id = producto_ids[indice].strip() if indice < len(producto_ids) else ""
        cantidad_texto = cantidades_recibidas[indice].strip() if indice < len(cantidades_recibidas) else ""
        filas.append({"producto": producto_id, "cantidad": cantidad_texto or "1"})
        if not producto_id:
            if cantidad_texto not in ("", "1"):
                error_formulario = "Seleccione un producto para cada cantidad indicada."
                break
            continue
        try:
            cantidad = int(cantidad_texto)
        except (TypeError, ValueError):
            error_formulario = "Las cantidades deben ser números enteros mayores que cero."
            break
        if cantidad <= 0:
            error_formulario = "Las cantidades deben ser mayores que cero."
            break
        try:
            producto_id_int = int(producto_id)
        except ValueError:
            error_formulario = "Uno de los productos seleccionados no es válido."
            break
        cantidades_por_producto[producto_id_int] = cantidades_por_producto.get(producto_id_int, 0) + cantidad

    if not filas:
        filas = [{"producto": "", "cantidad": "1"} for _ in range(3)]
    while len(filas) < 3:
        filas.append({"producto": "", "cantidad": "1"})

    cliente_id = request.POST.get("id_cliente", "").strip()
    trabajador_id = request.POST.get("id_trabajador", "").strip()
    cliente = None
    trabajador = None
    if not error_formulario:
        try:
            cliente = Cliente.objects.get(pk=cliente_id)
        except (Cliente.DoesNotExist, ValueError, TypeError):
            error_formulario = "Seleccione un cliente válido."
    if not error_formulario:
        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
        except (Trabajador.DoesNotExist, ValueError, TypeError):
            error_formulario = "Seleccione un trabajador válido."
    if not error_formulario and not cantidades_por_producto:
        error_formulario = "Agregue al menos un producto a la factura."

    if error_formulario:
        messages.error(request, error_formulario)
        contexto = _contexto_formulario_factura(filas, cliente_id, trabajador_id)
        return render(request, "inventario/facturas/formulario.html", contexto)

    try:
        with transaction.atomic():
            productos_bloqueados = Producto.objects.select_for_update().filter(
                pk__in=list(cantidades_por_producto.keys())
            )
            mapa_productos = {producto.pk: producto for producto in productos_bloqueados}
            if len(mapa_productos) != len(cantidades_por_producto):
                raise ValueError("Uno de los productos seleccionados ya no existe.")

            for producto_id, cantidad in cantidades_por_producto.items():
                producto = mapa_productos[producto_id]
                if cantidad > producto.stock:
                    raise ValueError(
                        f"Stock insuficiente para {producto.marca}. Disponibles: {producto.stock}; solicitadas: {cantidad}."
                    )

            factura = Factura.objects.create(
                fecha=timezone.localdate(),
                total_factura=Decimal("0.00"),
                id_cliente=cliente,
                id_trabajador=trabajador,
            )
            total = Decimal("0.00")
            for producto_id, cantidad in cantidades_por_producto.items():
                producto = mapa_productos[producto_id]
                precio_aplicado = producto.precio_actual
                DetalleFactura.objects.create(
                    id_factura=factura,
                    id_producto=producto,
                    cantidad=cantidad,
                    precio_vendido=precio_aplicado,
                )
                producto.stock -= cantidad
                producto.save(update_fields=["stock"])
                total += precio_aplicado * cantidad

            total = total.quantize(Decimal("0.01"))
            if total > Decimal("99999999.99"):
                raise ValueError("El total supera el máximo permitido para una factura.")
            factura.total_factura = total
            factura.save(update_fields=["total_factura"])
    except ValueError as error:
        messages.error(request, str(error))
        contexto = _contexto_formulario_factura(filas, cliente_id, trabajador_id)
        return render(request, "inventario/facturas/formulario.html", contexto)

    messages.success(request, f"La factura #{factura.pk} se registró correctamente.")
    return redirect("factura_detalle", pk=factura.pk)


@login_required
def detalle_factura(request, pk):
    factura = get_object_or_404(
        Factura.objects.select_related("id_cliente", "id_trabajador"),
        pk=pk,
    )
    detalles = factura.detalles.select_related("id_producto").all()
    return render(
        request,
        "inventario/facturas/detalle.html",
        {
            "active_nav": "facturas",
            "factura": factura,
            "detalles": detalles,
        },
    )
