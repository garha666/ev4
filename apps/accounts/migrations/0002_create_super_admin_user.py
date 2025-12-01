from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_super_admin_user(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    user, created = User.objects.get_or_create(
        username='super_admin',
        defaults={
            'email': 'super_admin@example.com',
            'rut': '99999999-9',
            # Historical models provided by migrations don't include
            # custom class-level constants, so use the raw value instead
            # of referencing User.ROLE_SUPER_ADMIN which is unavailable
            # when the migration runs.
            'role': 'super_admin',
            'is_staff': True,
            'is_superuser': True,
        },
    )
    user.role = 'super_admin'
    user.email = 'super_admin@example.com'
    user.rut = '99999999-9'
    user.is_staff = True
    user.is_superuser = True
    user.password = make_password('1234')
    user.save()


def remove_super_admin_user(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(username='super_admin').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_super_admin_user, remove_super_admin_user),
    ]
