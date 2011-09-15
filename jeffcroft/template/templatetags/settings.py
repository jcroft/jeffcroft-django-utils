from django import template
from django.template import Variable, Library, Node
from django.conf import settings

register = Library()

@register.simple_tag
def setting(name):
  return str(settings.__getattr__(name))