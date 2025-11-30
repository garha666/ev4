from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.accounts.models import User
from .forms import SupplierForm
from .models import Branch, Inventory, Supplier


def _user_has_role(user, allowed_roles):
    user_role = getattr(user, 'role', None)
    return bool(user and user.is_authenticated and (user_role in allowed_roles or user.is_superuser))


def _guard_role(request, allowed_roles):
    if not _user_has_role(request.user, allowed_roles):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')
    if not request.user.company:
        messages.error(request, 'Debes pertenecer a una compañía para ver esta sección.')
        return redirect('dashboard')
    return None


@login_required
def suppliers_list(request):
    denial = _guard_role(request, {User.ROLE_ADMIN_CLIENTE, User.ROLE_GERENTE, User.ROLE_SUPER_ADMIN})
    if denial:
        return denial
    suppliers = Supplier.objects.filter(company=request.user.company).order_by('name')
    context = {
        'suppliers': suppliers,
        'can_create': _user_has_role(request.user, {User.ROLE_ADMIN_CLIENTE, User.ROLE_GERENTE, User.ROLE_SUPER_ADMIN}),
    }
    return render(request, 'suppliers/list.html', context)


@login_required
def supplier_create(request):
    denial = _guard_role(request, {User.ROLE_ADMIN_CLIENTE, User.ROLE_GERENTE, User.ROLE_SUPER_ADMIN})
    if denial:
        return denial
    if request.method == 'POST':
        form = SupplierForm(request.POST, company=request.user.company)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.company = request.user.company
            supplier.save()
            messages.success(request, 'Proveedor creado correctamente')
            return redirect('suppliers_list')
    else:
        form = SupplierForm(company=request.user.company)
    return render(request, 'suppliers/create.html', {'form': form})


@login_required
def inventory_by_branch(request):
    denial = _guard_role(request, {User.ROLE_ADMIN_CLIENTE, User.ROLE_GERENTE, User.ROLE_SUPER_ADMIN, User.ROLE_VENDEDOR})
    if denial:
        return denial
    branches = Branch.objects.filter(company=request.user.company).order_by('name')
    selected_branch_id = request.GET.get('branch')
    selected_branch = None
    if selected_branch_id:
        selected_branch = branches.filter(id=selected_branch_id).first()
    if not selected_branch and branches:
        selected_branch = branches[0]

    inventories = Inventory.objects.filter(company=request.user.company)
    if selected_branch:
        inventories = inventories.filter(branch=selected_branch)
    inventories = inventories.select_related('product', 'branch').order_by('product__name')

    context = {
        'branches': branches,
        'selected_branch': selected_branch,
        'inventories': inventories,
    }
    return render(request, 'inventory/branch_inventory.html', context)
