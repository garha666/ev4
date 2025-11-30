from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Company, Subscription
from apps.inventory.models import Branch, Inventory, Product, Supplier


class Command(BaseCommand):
    help = 'Crea datos de demo'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Reinicia los datos de demo')

    def handle(self, *args, **options):
        User = get_user_model()
        reset = options.get('reset')

        usernames = ['admin_cliente', 'gerente', 'vendedor']
        if reset:
            self.stdout.write('Limpiando datos previos...')
            User.objects.filter(username__in=usernames).delete()
            Company.objects.filter(rut='11111111-1').delete()

        company, _ = Company.objects.get_or_create(name='Demo SA', rut='11111111-1')
        Subscription.objects.update_or_create(
            company=company,
            defaults={
                'plan_name': Subscription.PLAN_ESTANDAR,
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=365),
                'active': True,
            },
        )

        admin_cliente, _ = User.objects.get_or_create(
            username='admin_cliente',
            defaults={
                'email': 'admin_cliente@example.com',
                'rut': '11111111-1',
                'role': User.ROLE_ADMIN_CLIENTE,
                'company': company,
            },
        )
        admin_cliente.set_password('demo12345')
        admin_cliente.company = company
        admin_cliente.save()

        gerente, _ = User.objects.get_or_create(
            username='gerente',
            defaults={
                'email': 'gerente@example.com',
                'rut': '22222222-2',
                'role': User.ROLE_GERENTE,
                'company': company,
            },
        )
        gerente.set_password('demo12345')
        gerente.company = company
        gerente.save()

        vendedor, _ = User.objects.get_or_create(
            username='vendedor',
            defaults={
                'email': 'vendedor@example.com',
                'rut': '33333333-3',
                'role': User.ROLE_VENDEDOR,
                'company': company,
            },
        )
        vendedor.set_password('demo12345')
        vendedor.company = company
        vendedor.save()

        branch_specs = [
            {'name': 'Casa Matriz', 'address': 'Santiago Centro', 'phone': '2222 1111'},
            {'name': 'Sucursal Norte', 'address': 'Antofagasta', 'phone': '2222 3333'},
            {'name': 'Sucursal Sur', 'address': 'Concepción', 'phone': '2222 5555'},
        ]
        branches = []
        for spec in branch_specs:
            branch, _ = Branch.objects.update_or_create(
                company=company,
                name=spec['name'],
                defaults={'address': spec['address'], 'phone': spec['phone']},
            )
            branches.append(branch)

        categories = ['Electrónica', 'Oficina', 'Hogar', 'Outdoor', 'Computación']
        products = []
        for i in range(1, 25):
            category = categories[i % len(categories)]
            price = Decimal('5000') + Decimal(i * 350)
            cost = price * Decimal('0.6')
            product, _ = Product.objects.update_or_create(
                company=company,
                sku=f'SKU-{i:03d}',
                defaults={
                    'name': f'Producto {i}',
                    'description': f'Producto demo número {i}',
                    'price': price,
                    'cost': cost.quantize(Decimal('0.01')),
                    'category': category,
                },
            )
            products.append(product)

        supplier_specs = [
            {'name': 'Proveedor Andes', 'rut': '44444444-4', 'contact_name': 'Ana Torres', 'contact_email': 'ana@andes.cl', 'contact_phone': '+56 9 1111 1111'},
            {'name': 'Logística Sur', 'rut': '55555555-5', 'contact_name': 'Carlos Rojas', 'contact_email': 'carlos@logs.cl', 'contact_phone': '+56 9 2222 2222'},
            {'name': 'Insumos Norte', 'rut': '66666666-6', 'contact_name': 'Marcela Díaz', 'contact_email': 'marcela@insumosnorte.cl', 'contact_phone': '+56 9 3333 3333'},
            {'name': 'Tech Partners', 'rut': '77777777-7', 'contact_name': 'Jorge Silva', 'contact_email': 'jorge@techpartners.cl', 'contact_phone': '+56 9 4444 4444'},
            {'name': 'Distribuidora Centro', 'rut': '88888888-8', 'contact_name': 'Paula Zamora', 'contact_email': 'paula@dcentro.cl', 'contact_phone': '+56 9 5555 5555'},
        ]
        suppliers = []
        for spec in supplier_specs:
            supplier, _ = Supplier.objects.update_or_create(
                company=company,
                rut=spec['rut'],
                defaults={
                    'name': spec['name'],
                    'contact_name': spec['contact_name'],
                    'contact_email': spec['contact_email'],
                    'contact_phone': spec['contact_phone'],
                },
            )
            suppliers.append(supplier)

        for idx, product in enumerate(products):
            for b_idx, branch in enumerate(branches):
                stock = 20 + (idx * 3 + b_idx * 5) % 80
                reorder_point = 8 + (idx % 5)
                Inventory.objects.update_or_create(
                    company=company,
                    branch=branch,
                    product=product,
                    defaults={
                        'stock': stock,
                        'reorder_point': reorder_point,
                    },
                )

        self.stdout.write(self.style.SUCCESS('Datos de demo creados'))
