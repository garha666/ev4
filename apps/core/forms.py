from django import forms

from apps.core.models import Plan, PlanFeature, Subscription


class PlanForm(forms.ModelForm):
    features = forms.ModelMultipleChoiceField(
        queryset=PlanFeature.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Selecciona las funcionalidades incluidas en el plan.',
    )

    class Meta:
        model = Plan
        fields = ['code', 'name', 'description', 'monthly_price', 'branch_limit', 'is_active', 'features']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class SubscriptionAdminForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['company', 'plan', 'start_date', 'end_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            self.add_error('end_date', 'La fecha fin debe ser posterior al inicio.')
        return cleaned
