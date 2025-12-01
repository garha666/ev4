from django import template

from apps.core.access import plan_allows

register = template.Library()


@register.simple_tag(takes_context=True)
def plan_allows_feature(context, feature_code):
    user = context['user']
    return plan_allows(user, feature_code)
