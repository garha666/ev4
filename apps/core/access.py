from __future__ import annotations

from datetime import date
from typing import Iterable

from django.contrib.auth import get_user_model

User = get_user_model()

# Mapeo de funcionalidades por plan. Las claves deben existir como PlanFeature.code.
DEFAULT_PLAN_MATRIX = {
    'BASICO': {'inventory', 'sales', 'orders', 'pos', 'user_management'},
    'ESTANDAR': {'inventory', 'sales', 'orders', 'pos', 'reports', 'user_management'},
    'PREMIUM': {'inventory', 'sales', 'orders', 'pos', 'reports', 'user_management', 'branches_unlimited'},
}


def plan_allows(user, feature_code: str) -> bool:
    """Evalúa si el usuario puede acceder a una funcionalidad según su plan y rol."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'role', None) == getattr(user, 'ROLE_SUPER_ADMIN', 'super_admin'):
        return True

    company = getattr(user, 'company', None)
    subscription = getattr(company, 'subscription', None) if company else None
    if not subscription or not subscription.is_active:
        return False
    plan = getattr(subscription, 'plan', None)
    if not plan:
        return False
    if hasattr(plan, 'has_feature') and plan.has_feature(feature_code):
        return True

    # fallback para planes iniciales basados en código
    feature_set: Iterable[str] = DEFAULT_PLAN_MATRIX.get(plan.code, set())
    return feature_code in feature_set


def plan_window_active(subscription) -> bool:
    if not subscription:
        return False
    today = date.today()
    return subscription.start_date <= today <= subscription.end_date and subscription.status == subscription.STATUS_ACTIVE
