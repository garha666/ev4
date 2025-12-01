from rest_framework.permissions import BasePermission

from apps.core.access import plan_allows


class IsActive(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active)


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == request.user.ROLE_SUPER_ADMIN)


class CompanyPlanAllowsReports(BasePermission):
    def has_permission(self, request, view):
        return plan_allows(request.user, 'reports')
