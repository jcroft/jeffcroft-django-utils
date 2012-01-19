from __future__ import division

from django import template
from django.utils.safestring import mark_safe
 
register = template.Library()

@register.filter
def multiply(value, arg):
  "Multiplies the arg and the value"
  return int(value) * int(arg)

@register.filter
def subtract(value, arg):
  "Subtracts the arg from the value"
  return int(value) - int(arg)

@register.filter
def divide(value, arg):
  "Divides the value by the arg"
  return int(value) / int(arg)

@register.filter
def integer_divide(value, arg):
  "Divides the value by the arg"
  return int(value) // int(arg)

