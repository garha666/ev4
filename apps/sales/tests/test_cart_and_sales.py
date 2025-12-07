from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Company
from apps.inventory.models import Branch, Product
from apps.sales.models import Sale

User = get_user_model()


class CartAndSaleIsolationTests(TestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name='Company A', rut='12345678-5')
        self.company_b = Company.objects.create(name='Company B', rut='87654321-4')
        self.user_a = User.objects.create_user(
            username='seller',
            password='pass1234',
            email='seller@example.com',
            rut='22222222-2',
            role=User.ROLE_ADMIN_CLIENTE,
            company=self.company_a,
        )
        self.branch_a = Branch.objects.create(company=self.company_a, name='Branch A', address='Addr A', phone='123')
        self.branch_b = Branch.objects.create(company=self.company_b, name='Branch B', address='Addr B', phone='456')
        self.product_a = Product.objects.create(company=self.company_a, sku='SKU-A', name='Product A', description='', price=10, cost=5, category='')
        self.product_b = Product.objects.create(company=self.company_b, sku='SKU-B', name='Product B', description='', price=20, cost=10, category='')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user_a)

    def test_cart_add_rejects_product_from_other_company(self):
        response = self.client.post(reverse('cart-add'), {'product': self.product_b.id, 'quantity': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Producto no pertenece', str(response.data.get('detail', '')))

    def test_checkout_rejects_branch_from_other_company(self):
        add_response = self.client.post(reverse('cart-add'), {'product': self.product_a.id, 'quantity': 1}, format='json')
        self.assertEqual(add_response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('cart-checkout'), {'branch_id': self.branch_b.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Sucursal invalida', str(response.data.get('detail', '')))

    def test_create_sale_rejects_foreign_product(self):
        payload = {
            'branch': self.branch_a.id,
            'payment_method': 'cash',
            'items': [{'product': self.product_b.id, 'quantity': 1, 'unit_price': '20.00'}],
        }
        response = self.client.post(reverse('sale-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Producto no pertenece', str(response.data))
        self.assertEqual(Sale.objects.count(), 0)

    def test_create_sale_returns_400_when_inventory_missing(self):
        payload = {
            'branch': self.branch_a.id,
            'payment_method': 'cash',
            'items': [{'product': self.product_a.id, 'quantity': 1, 'unit_price': '10.00'}],
        }
        response = self.client.post(reverse('sale-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Inventario no encontrado', str(response.data))
        self.assertEqual(Sale.objects.count(), 0)
