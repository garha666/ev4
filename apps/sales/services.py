from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.inventory.models import Inventory, InventoryMovement
from .models import Sale, SaleItem


def create_sale(validated_data, user):
    items_data = list(validated_data.pop('items'))
    branch = validated_data['branch']
    if branch.company != user.company:
        raise ValidationError('Sucursal invalida')
    total = Decimal('0')
    with transaction.atomic():
        sale = Sale.objects.create(company=user.company, seller=user, **validated_data)
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            unit_price = item['unit_price']
            if product.company != user.company:
                raise ValidationError('Producto no pertenece a la empresa del usuario')
            try:
                inventory = Inventory.objects.select_for_update().get(company=user.company, branch=branch, product=product)
            except Inventory.DoesNotExist:
                raise ValidationError('Inventario no encontrado para el producto/sucursal')
            if inventory.stock < quantity:
                raise ValidationError('Stock insuficiente')
            inventory.stock -= quantity
            inventory.save()
            SaleItem.objects.create(sale=sale, **item)
            InventoryMovement.objects.create(
                company=user.company,
                branch=branch,
                product=product,
                movement_type=InventoryMovement.MOV_SALE,
                quantity_delta=-quantity,
                reason='Venta',
                created_by=user,
            )
            total += quantity * unit_price
        sale.total = total
        sale.save()
        if sale.created_at > timezone.now():
            raise ValidationError('La fecha de venta no puede estar en el futuro')
    return sale
