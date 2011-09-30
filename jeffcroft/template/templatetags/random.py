import random as random_module

from django import template
 
register = template.Library()

@register.filter
def several_random(value, arg=1):
  "Returns one or more random item(s) from the list"
  try:
    arg = int(arg)
  except ValueError:
    return value
  if arg == 1:    
    return random_module.choice(value)
  elif len(value) > arg:  # Only pick if we are asked for fewer items than we are given
    return random_module.sample(value, arg)
  else:   # Number requested is equal to or greater than the number we have, return them all in random order
    new_list = list(value)
    random_module.shuffle(new_list)
    return new_list