from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cliente, DetalleFactura, Factura, Producto, Proveedor, Trabajador


class FlujoFacturaTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(username="operador", password="prueba-segura-123")
        self.client.login(username=usuario.username, password="prueba-segura-123")
        proveedor = Proveedor.objects.create(nombre_empresa="Proveedor de prueba", telefono="04120000000")
        self.producto = Producto.objects.create(
            marca="Cable USB",
            precio_actual=Decimal("10.00"),
            stock=5,
            id_proveedor=proveedor,
        )
        self.cliente = Cliente.objects.create(nombre="Cliente de prueba", cedula_o_rif="V-12345678", telefono="04121111111")
        self.trabajador = Trabajador.objects.create(nombre="Operador de prueba", cargo="Vendedor")

    def test_factura_calcula_total_y_descuenta_stock(self):
        respuesta = self.client.post(
            reverse("factura_crear"),
            {
                "id_cliente": str(self.cliente.pk),
                "id_trabajador": str(self.trabajador.pk),
                "productos[]": [str(self.producto.pk)],
                "cantidades[]": ["2"],
            },
        )

        factura = Factura.objects.get()
        detalle = DetalleFactura.objects.get(id_factura=factura)
        self.producto.refresh_from_db()

        self.assertRedirects(respuesta, reverse("factura_detalle", kwargs={"pk": factura.pk}))
        self.assertEqual(factura.total_factura, Decimal("20.00"))
        self.assertEqual(detalle.precio_vendido, Decimal("10.00"))
        self.assertEqual(self.producto.stock, 3)

    def test_no_registra_venta_con_stock_insuficiente(self):
        respuesta = self.client.post(
            reverse("factura_crear"),
            {
                "id_cliente": str(self.cliente.pk),
                "id_trabajador": str(self.trabajador.pk),
                "productos[]": [str(self.producto.pk)],
                "cantidades[]": ["8"],
            },
        )

        self.producto.refresh_from_db()
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Factura.objects.count(), 0)
        self.assertEqual(self.producto.stock, 5)


class CatalogosTests(TestCase):
    def test_usuario_no_autenticado_debe_iniciar_sesion(self):
        respuesta = self.client.get(reverse("productos"))
        self.assertRedirects(respuesta, f"{reverse('login')}?next={reverse('productos')}")
