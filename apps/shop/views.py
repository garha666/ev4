from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from apps.inventory.models import Product
from apps.sales.models import CartItem


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def product_list(request):
    products = Product.objects.filter(company=request.user.company)
    return render(request, 'shop/products.html', {'products': products})


@login_required
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk, company=request.user.company)
    except Product.DoesNotExist as exc:
        raise Http404 from exc
    return render(request, 'shop/product_detail.html', {'product': product})


@login_required
def cart_view(request):
    items = CartItem.objects.filter(user=request.user)
    return render(request, 'shop/cart.html', {'items': items})


@login_required
def checkout_view(request):
    return render(request, 'shop/checkout.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
