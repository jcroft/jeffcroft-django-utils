import random as random_module

from django import template
 
register = template.Library()

@register.filter
def several_random(queryset, arg=1):
  "Returns one or more random item(s) from a QuerySet"
  try:
    arg = int(arg)
  except ValueError:
    return queryset
  return queryset.order_by('?')[:arg]