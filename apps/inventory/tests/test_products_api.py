from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.core.models import Company
from apps.inventory.models import Product

User = get_user_model()


class ProductTenantIsolationTests(TestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name='Company A', rut='12345678-5')
        self.company_b = Company.objects.create(name='Company B', rut='87654321-4')
        self.user_a = User.objects.create_user(
            username='user_a',
            password='pass1234',
            email='usera@example.com',
            rut='11111111-1',
            role=User.ROLE_ADMIN_CLIENTE,
            company=self.company_a,
        )
        self.product_a = Product.objects.create(company=self.company_a, sku='SKU-A', name='Product A', description='', price=10, cost=5, category='')
        self.product_b = Product.objects.create(company=self.company_b, sku='SKU-B', name='Product B', description='', price=20, cost=10, category='')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user_a)

    def test_list_only_returns_user_company_products(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)
        returned_ids = {item['id'] for item in response.data}
        self.assertIn(self.product_a.id, returned_ids)
        self.assertNotIn(self.product_b.id, returned_ids)

    def test_retrieve_other_company_product_returns_404(self):
        response = self.client.get(reverse('product-detail', args=[self.product_b.id]))
        self.assertEqual(response.status_code, 404)
