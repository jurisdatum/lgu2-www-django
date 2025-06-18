from django import template

register = template.Library()

@register.simple_tag
def render_list_tags(children):
    first_child = children[0]
    # Check if the first child has a 'children' key and it's a list
    has_nested_children = isinstance(first_child, dict) and bool(first_child.get("children"))
    if has_nested_children:
        tag = 'ul'    
    else:
        tag = 'ol'        
    return f"<{tag}>", f"</{tag}>"
