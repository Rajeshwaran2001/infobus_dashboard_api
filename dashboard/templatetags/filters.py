from django import template

register = template.Library()

@register.filter
def tolist(value):
    return value.tolist()
