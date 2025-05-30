from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    """
    Multiplies the value by the argument
    Usage: {{ value|mul:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
