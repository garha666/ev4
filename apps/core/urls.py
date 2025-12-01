from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, PlanViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = router.urls
