# TemucoSoft S.A. (POS + e-commerce)

Proyecto Django + DRF multi-tenant por Company, con autenticacion JWT (SimpleJWT) y vistas HTML Bootstrap 5. Incluye planes con limites, control por roles y demo seed.

## Requisitos
- Python 3.10+
- pip + venv/pipenv

## Instalacion local (sqlite)
```bash
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo --reset
python manage.py runserver
```

## Datos de demo
- Ejecuta `python manage.py seed_demo --reset` para recrear datos completos (empresa demo con plan Premium e inventario).
- Parametros utiles: `--products 200 --suppliers 30 --branches 5 --purchases 80 --sales 180 --orders 120`.
- Usuarios de prueba:
  - `superadmin` / `demo12345` (sin company, crea `admin_cliente`)
  - `admin_cliente` / `demo12345` (plan Premium)
  - `gerente` / `demo12345` (plan Premium)
  - `vendedor` / `demo12345` (plan Premium)
  - `admin_basico`, `gerente_basico`, `admin_estandar`, `gerente_estandar` (todas con `demo12345`)
- Login por sesion: `http://localhost:8000/login/`
- JWT: boton "Obtener JWT" en login y pagina "Tokens API (JWT)" en el menu del usuario.

## JWT rapido
- `POST /api/token/` con `username` y `password` -> access/refresh
- `POST /api/token/refresh/` -> nuevo access
- `POST /api/token/session/` (loggeado por sesion) -> access/refresh en JSON

## Roles y accesos
- `super_admin`: crea companies y admin_cliente (sin company asociada)
- `admin_cliente`: usuarios internos, productos, proveedores, sucursales, inventario, reportes
- `gerente`: ventas y reportes
- `vendedor`: ventas POS y carrito

## Endpoints clave (prefijo /api/)
- Auth: `/token/`, `/token/refresh/`, `/token/session/`
- Usuarios: `POST /users/` (segun rol), `GET /users/me/`
- Companies/Planes: `GET/POST /companies/` (solo super_admin), `POST /companies/{id}/subscribe/`
- Productos: `GET /products/?company=<id>` publico; CRUD restringido por company/rol
- Sucursales: `GET/POST /branches/` (respeta branch_limit del plan), `GET /branches/{id}/inventory/`
- Inventario: `GET /inventory/?branch=...`, `POST /inventory/adjust/` (stock no negativo)
- Proveedores: `GET/POST /suppliers/`
- Compras: `POST /purchases/` (incrementa stock, valida fecha <= hoy)
- Ventas POS: `POST /sales/` (valida stock y fecha no futura), `GET /sales/?branch=&date_from=&date_to=`
- Carrito/Orders: `POST /cart/add/`, `POST /cart/checkout/` (descuenta stock, genera Order)
- Reportes: `GET /reports/stock/`, `GET /reports/sales/`, `GET /reports/suppliers/` (requieren plan con reports)

## Templates y UI (Bootstrap 5 + tema propio)
- Login con boton JWT, dashboard segun rol, catalogo/detalle (publico con ?company=<id>), carrito/checkout, POS, lista de ventas, inventario por sucursal, proveedores (list/create), compras, sucursales (list/create), suscripcion, reportes, panel super_admin (planes, suscripciones, companies, usuarios).
- Menu muestra/oculta secciones segun `user.role` y features del plan.
- Branding navbar/titulo: TemucoSoft S.A.

## Validaciones destacadas
- RUT con DV: `apps/core/validators.py`
- Fechas: ventas no en futuro, compras no en futuro, end_date > start_date en suscripciones
- Numericos: precio/costo >= 0, stock >= 0, quantity >= 1, sin stock negativo en ajustes/ventas

## Documentacion
- MER y tablas normalizadas: `docs/MER.md`
- Deploy EC2 + Nginx + Gunicorn: `docs/DEPLOY_EC2.md`
- Ejemplos curl JWT: `scripts/curl_examples.sh`

## Deploy (resumen)
1) Configurar Postgres y variables `.env` (ver `.env.example`).  
2) `pip install -r requirements.txt`  
3) `python manage.py migrate` y `python manage.py collectstatic --noinput`  
4) Servicios de referencia: `deploy/gunicorn.service`, `deploy/nginx.conf`  
5) Abrir SG: 22 (SSH), 80/443 (HTTP/HTTPS), 5432 solo desde la app (o SG privado si DB separada).  

## Smoke test sugerido
- `python manage.py seed_demo --reset`
- Login como **gerente** y validar proveedores, inventario por sucursal, compra, venta, reportes (si plan habilita)
- Login como **vendedor** y validar catalogo, carrito, checkout, POS
- JWT via `/api/token/` y consumo de endpoints protegidos
- Confirmar multi-tenant: usuario de otra company no ve datos cruzados
- Pruebas automaticas: `python manage.py test`
