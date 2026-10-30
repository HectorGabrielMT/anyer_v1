# Inversiones Zambrano — Control de inventario con Django

Inversiones Zambrano es un proyecto educativo de control de inventario basado en el diagrama entregado. Usa SQLite para que pueda ejecutarse sin instalar un servidor de base de datos, el administrador oficial de Django y páginas HTML con clases de Bootstrap 5 y Bootstrap Icons, además de imágenes locales de aceites lubricantes para vehículos. Los formularios de los catálogos se procesan directamente en `inventario/views.py`; el proyecto no usa `forms.py`.

## Requisitos

- Python 3.10 o superior.
- Acceso a internet en el navegador para cargar Bootstrap desde su CDN.

## Instalación en Windows

Abra una terminal en la carpeta `InversionesZambrano` del proyecto y ejecute:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abra `http://127.0.0.1:8000/` e ingrese con el usuario creado. El panel oficial de Django está en `http://127.0.0.1:8000/admin/`.

## Instalación en Linux o macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Funcionalidades

- Inicio de sesión basado en el sistema de autenticación de Django.
- CRUD de proveedores, productos, clientes y trabajadores; los productos no utilizan categorías.
- Búsqueda de registros en los listados.
- Registro y consulta de facturas con sus detalles.
- Validación de las cantidades y las existencias antes de confirmar una venta.
- Cálculo del total en el servidor, copia del precio vendido en cada detalle y descuento automático del stock dentro de una transacción.
- Protección frente a la eliminación de catálogos que todavía tengan registros relacionados.
- Modelos registrados en el administrador de Django. Las facturas y sus detalles se muestran en modo de solo lectura para evitar modificar ventas históricas sin ajustar las existencias.

## Orden sugerido para comenzar

1. Inicie sesión en el sitio.
2. Registre proveedores y productos.
3. Registre productos y sus precios y existencias.
4. Registre clientes y trabajadores.
5. Entre en **Facturas** y registre una venta.

## Notas

La zona horaria inicial es `America/Caracas`; puede modificarse en `config/settings.py`. `DEBUG` está activado por defecto para el entorno educativo local. Antes de desplegar públicamente el proyecto, configure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` y `DJANGO_ALLOWED_HOSTS`, además de revisar HTTPS, copias de seguridad y las demás medidas de seguridad de producción.


## Identidad visual

La interfaz utiliza Bootstrap 5 y Bootstrap Icons, con imágenes locales de almacén y cajas en `inventario/static/inventario/images/`. Los formularios y las rutas mantienen el comportamiento original.


## Roles de usuario

- **Administrador:** usuario con `is_staff` o `is_superuser` activado. Puede gestionar productos, ventas, proveedores, clientes, trabajadores y acceder al panel de administración de Django.
- **Normal:** usuario sin esos permisos. Solo puede consultar y gestionar productos y registrar/consultar ventas. Las rutas de proveedores, clientes y trabajadores están protegidas también en el servidor.

Para crear un usuario normal, créelo desde el panel de administración y deje desactivadas las opciones «Es staff» y «Es superusuario». Para un administrador, active «Es staff».

Las categorías fueron eliminadas del modelo y del flujo de productos. La migración `0002_eliminar_categorias` elimina la relación de categoría sin alterar los demás registros.
