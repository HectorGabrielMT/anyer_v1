"""Modelos que representan las tablas del diagrama de inventario."""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True, verbose_name="ID")
    nombre_empresa = models.CharField(max_length=255, verbose_name="Nombre de la empresa")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")

    class Meta:
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"
        ordering = ["nombre_empresa"]

    def __str__(self):
        return self.nombre_empresa


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True, verbose_name="ID")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    cedula_o_rif = models.CharField(max_length=50, verbose_name="Cédula o RIF")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.cedula_o_rif})"


class Trabajador(models.Model):
    id_trabajador = models.AutoField(primary_key=True, verbose_name="ID")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    cargo = models.CharField(max_length=255, verbose_name="Cargo")

    class Meta:
        verbose_name = "trabajador"
        verbose_name_plural = "trabajadores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True, verbose_name="ID")
    precio_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"), message="El precio no puede ser negativo.")],
        verbose_name="Precio actual",
    )
    marca = models.CharField(max_length=255, verbose_name="Marca")
    stock = models.PositiveIntegerField(default=0, verbose_name="Existencias")
    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        db_column="id_proveedor",
        related_name="productos",
        verbose_name="Proveedor",
    )

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["marca", "id_producto"]

    def __str__(self):
        return f"{self.marca} · #{self.id_producto}"


class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True, verbose_name="ID")
    fecha = models.DateField(default=timezone.localdate, verbose_name="Fecha")
    total_factura = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"), message="El total no puede ser negativo.")],
        verbose_name="Total de la factura",
    )
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column="id_cliente",
        related_name="facturas",
        verbose_name="Cliente",
    )
    id_trabajador = models.ForeignKey(
        Trabajador,
        on_delete=models.PROTECT,
        db_column="id_trabajador",
        related_name="facturas",
        verbose_name="Trabajador",
    )

    class Meta:
        verbose_name = "factura"
        verbose_name_plural = "facturas"
        ordering = ["-fecha", "-id_factura"]

    def __str__(self):
        return f"Factura #{self.id_factura} · {self.fecha:%d/%m/%Y}"


class DetalleFactura(models.Model):
    id_detalle = models.AutoField(primary_key=True, verbose_name="ID")
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="La cantidad debe ser al menos 1.")],
        verbose_name="Cantidad",
    )
    precio_vendido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"), message="El precio vendido no puede ser negativo.")],
        verbose_name="Precio de venta",
    )
    id_factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        db_column="id_factura",
        related_name="detalles",
        verbose_name="Factura",
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column="id_producto",
        related_name="detalles_factura",
        verbose_name="Producto",
    )

    class Meta:
        verbose_name = "detalle de factura"
        verbose_name_plural = "detalles de factura"
        ordering = ["id_detalle"]

    def __str__(self):
        return f"Factura #{self.id_factura_id} · {self.id_producto} × {self.cantidad}"

    @property
    def subtotal(self):
        return self.precio_vendido * self.cantidad
