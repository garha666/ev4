from rest_framework import serializers
from .models import Company, Plan, PlanFeature, Subscription
from .validators import validate_rut


class CompanySerializer(serializers.ModelSerializer):
    rut = serializers.CharField(validators=[validate_rut])

    class Meta:
        model = Company
        fields = ['id', 'name', 'rut', 'administrators', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'administrators': {'required': False, 'allow_empty': True},
        }


class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ['id', 'code', 'label', 'description']
        read_only_fields = ['id']


class PlanSerializer(serializers.ModelSerializer):
    features = PlanFeatureSerializer(many=True, read_only=True)
    feature_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=PlanFeature.objects.all(),
        source='features',
        write_only=True,
        required=False,
    )

    class Meta:
        model = Plan
        fields = [
            'id',
            'code',
            'name',
            'description',
            'monthly_price',
            'branch_limit',
            'is_active',
            'features',
            'feature_ids',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all())

    class Meta:
        model = Subscription
        fields = ['id', 'company', 'plan', 'start_date', 'end_date', 'status', 'canceled_at']
        read_only_fields = ['id', 'company', 'canceled_at']

    def validate(self, attrs):
        if attrs['end_date'] < attrs['start_date']:
            raise serializers.ValidationError('Fecha fin debe ser posterior a inicio')
        return attrs
