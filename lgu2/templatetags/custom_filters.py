import re
from django import template

register = template.Library()

@register.filter
def camel_to_words(value):
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', value)
