from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'rut', 'contact_name', 'contact_email', 'contact_phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        qs = Supplier.objects.all()
        if self.company:
            qs = qs.filter(company=self.company)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.filter(rut=rut).exists():
            raise forms.ValidationError('Ya existe un proveedor con este RUT en tu compañía')
        return rut
