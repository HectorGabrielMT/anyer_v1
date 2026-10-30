# Generated as the initial schema for the educational inventory project.
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Categoria",
            fields=[
                ("id_categoria", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre_categoria", models.CharField(max_length=255, verbose_name="Nombre de la categoría")),
            ],
            options={"verbose_name": "categoría", "verbose_name_plural": "categorías", "ordering": ["nombre_categoria"]},
        ),
        migrations.CreateModel(
            name="Proveedor",
            fields=[
                ("id_proveedor", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre_empresa", models.CharField(max_length=255, verbose_name="Nombre de la empresa")),
                ("telefono", models.CharField(max_length=20, verbose_name="Teléfono")),
            ],
            options={"verbose_name": "proveedor", "verbose_name_plural": "proveedores", "ordering": ["nombre_empresa"]},
        ),
        migrations.CreateModel(
            name="Cliente",
            fields=[
                ("id_cliente", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=255, verbose_name="Nombre")),
                ("cedula_o_rif", models.CharField(max_length=50, verbose_name="Cédula o RIF")),
                ("telefono", models.CharField(max_length=20, verbose_name="Teléfono")),
            ],
            options={"verbose_name": "cliente", "verbose_name_plural": "clientes", "ordering": ["nombre"]},
        ),
        migrations.CreateModel(
            name="Trabajador",
            fields=[
                ("id_trabajador", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=255, verbose_name="Nombre")),
                ("cargo", models.CharField(max_length=255, verbose_name="Cargo")),
            ],
            options={"verbose_name": "trabajador", "verbose_name_plural": "trabajadores", "ordering": ["nombre"]},
        ),
        migrations.CreateModel(
            name="Producto",
            fields=[
                ("id_producto", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("precio_actual", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal("0.00"), message="El precio no puede ser negativo.")], verbose_name="Precio actual")),
                ("marca", models.CharField(max_length=255, verbose_name="Marca")),
                ("stock", models.PositiveIntegerField(default=0, verbose_name="Existencias")),
                ("id_categoria", models.ForeignKey(db_column="id_categoria", on_delete=django.db.models.deletion.PROTECT, related_name="productos", to="inventario.categoria", verbose_name="Categoría")),
                ("id_proveedor", models.ForeignKey(db_column="id_proveedor", on_delete=django.db.models.deletion.PROTECT, related_name="productos", to="inventario.proveedor", verbose_name="Proveedor")),
            ],
            options={"verbose_name": "producto", "verbose_name_plural": "productos", "ordering": ["marca", "id_producto"]},
        ),
        migrations.CreateModel(
            name="Factura",
            fields=[
                ("id_factura", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField(default=django.utils.timezone.localdate, verbose_name="Fecha")),
                ("total_factura", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal("0.00"), message="El total no puede ser negativo.")], verbose_name="Total de la factura")),
                ("id_cliente", models.ForeignKey(db_column="id_cliente", on_delete=django.db.models.deletion.PROTECT, related_name="facturas", to="inventario.cliente", verbose_name="Cliente")),
                ("id_trabajador", models.ForeignKey(db_column="id_trabajador", on_delete=django.db.models.deletion.PROTECT, related_name="facturas", to="inventario.trabajador", verbose_name="Trabajador")),
            ],
            options={"verbose_name": "factura", "verbose_name_plural": "facturas", "ordering": ["-fecha", "-id_factura"]},
        ),
        migrations.CreateModel(
            name="DetalleFactura",
            fields=[
                ("id_detalle", models.AutoField(primary_key=True, serialize=False, verbose_name="ID")),
                ("cantidad", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, message="La cantidad debe ser al menos 1.")], verbose_name="Cantidad")),
                ("precio_vendido", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal("0.00"), message="El precio vendido no puede ser negativo.")], verbose_name="Precio de venta")),
                ("id_factura", models.ForeignKey(db_column="id_factura", on_delete=django.db.models.deletion.CASCADE, related_name="detalles", to="inventario.factura", verbose_name="Factura")),
                ("id_producto", models.ForeignKey(db_column="id_producto", on_delete=django.db.models.deletion.PROTECT, related_name="detalles_factura", to="inventario.producto", verbose_name="Producto")),
            ],
            options={"verbose_name": "detalle de factura", "verbose_name_plural": "detalles de factura", "ordering": ["id_detalle"]},
        ),
    ]
