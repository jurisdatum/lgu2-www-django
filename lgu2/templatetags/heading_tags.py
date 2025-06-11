from django import template

register = template.Library()

@register.filter
def heading_tag(level):
    try:
        level = int(level) + 3
    except (ValueError, TypeError):
        level = 1  # Default to level 1 if it's invalid or empty
    
    if level > 6:
        level = 6
    
    return f"h{level}"
