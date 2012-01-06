from django import template
from django.template import Library, Node

register = Library()

@register.filter
def leading_zeros(value, desired_digits):
  """
  Given an integer, returns a string representation, padding with [desired_digits] zeros.
  """
  num_zeros = int(desired_digits) - len(str(value))
  padded_value = []
  while num_zeros >= 1:
    padded_value.append("0") 
    num_zeros = num_zeros - 1
  padded_value.append(str(value))
  return "".join(padded_value)