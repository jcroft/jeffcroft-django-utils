from django import template
from django.template import Library, Node
from django.conf import settings

register = Library()

@register.filter
def unescape(value):
  """
  Undoes basic HTML escaping, including ", <, >, and &.
    
    {% entry.body|unescape %}
  
  """
  value = value.replace('&quot;', '"')
  value = value.replace('&lt;', '<')
  value = value.replace('&gt;', '>')
  value = value.replace('&lt;br /&gt;', '<br />')
  value = value.replace('&amp;', '&')
  return value