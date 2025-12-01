from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.access import plan_allows
from apps.core.models import Company, Plan, PlanFeature, Subscription

User = get_user_model()


class PlanAndSubscriptionViewsTests(TestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            username='super', password='pass1234', role=User.ROLE_SUPER_ADMIN, email='super@example.com', rut='99999999-9'
        )
        self.company = Company.objects.create(name='ACME', rut='12345678-5')
        self.feature_inventory, _ = PlanFeature.objects.get_or_create(code='inventory', defaults={'label': 'Inventario'})
        self.feature_reports, _ = PlanFeature.objects.get_or_create(code='reports', defaults={'label': 'Reportes'})
        self.plan_basic, _ = Plan.objects.get_or_create(
            code='BASICO', defaults={'name': 'Básico', 'branch_limit': 1, 'monthly_price': 0}
        )
        self.plan_basic.features.add(self.feature_inventory)
        self.plan_premium, _ = Plan.objects.get_or_create(
            code='PREMIUM', defaults={'name': 'Premium', 'branch_limit': None, 'monthly_price': 10}
        )
        self.plan_premium.features.set([self.feature_inventory, self.feature_reports])

    def test_super_admin_can_create_plan_via_view(self):
        self.client.login(username='super', password='pass1234')
        response = self.client.post(
            reverse('super_admin_plans'),
            {
                'code': 'NUEVO',
                'name': 'Nuevo plan',
                'monthly_price': '5',
                'branch_limit': 2,
                'description': 'Cobertura ampliada',
                'features': [self.feature_inventory.id, self.feature_reports.id],
                'is_active': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Plan.objects.filter(code='NUEVO').exists())

    def test_plan_delete_blocked_with_subscription(self):
        Subscription.objects.create(
            company=self.company,
            plan=self.plan_basic,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status=Subscription.STATUS_ACTIVE,
        )
        self.client.login(username='super', password='pass1234')
        response = self.client.post(reverse('super_admin_plan_delete', args=[self.plan_basic.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Plan.objects.filter(id=self.plan_basic.id).exists())

    def test_super_admin_assigns_and_cancels_subscription(self):
        self.client.login(username='super', password='pass1234')
        start = date.today()
        end = start + timedelta(days=365)
        assign_response = self.client.post(
            reverse('super_admin_subscriptions'),
            {
                'company': self.company.id,
                'plan': self.plan_premium.id,
                'start_date': start,
                'end_date': end,
                'status': Subscription.STATUS_ACTIVE,
            },
        )
        self.assertEqual(assign_response.status_code, 302)
        subscription = Subscription.objects.get(company=self.company)
        self.assertEqual(subscription.plan, self.plan_premium)
        self.assertEqual(subscription.status, Subscription.STATUS_ACTIVE)

        cancel_response = self.client.post(
            reverse('super_admin_subscriptions'),
            {'cancel_id': subscription.id},
        )
        self.assertEqual(cancel_response.status_code, 302)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, Subscription.STATUS_CANCELLED)

    def test_plan_allows_respects_status(self):
        user = User.objects.create_user(
            username='admin', password='pass1234', role=User.ROLE_ADMIN_CLIENTE, email='a@example.com', rut='11111111-1'
        )
        user.company = self.company
        user.save()
        Subscription.objects.create(
            company=self.company,
            plan=self.plan_premium,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status=Subscription.STATUS_CANCELLED,
        )
        self.assertFalse(plan_allows(user, 'reports'))
        subscription = user.company.subscription
        subscription.status = Subscription.STATUS_ACTIVE
        subscription.save()
        self.assertTrue(plan_allows(user, 'reports'))
