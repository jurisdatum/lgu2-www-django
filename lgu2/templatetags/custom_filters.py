import re
from django import template
from ..util.types import to_short_type, get_category
from ..util.labels import get_type_label
register = template.Library()

from collections import namedtuple

CamelWordsResult = namedtuple("CamelWordsResult", ["short_type", "label_type"])

@register.filter
def camel_to_words(value):
    short_type = to_short_type(value)
    label_type = get_type_label(short_type)
    return CamelWordsResult(short_type=short_type, label_type=label_type)


@register.filter
def dict_key(d, key):
    return d.get(key, '')