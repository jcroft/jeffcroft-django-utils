import locale

from django import template
 
register = template.Library()

def lower_if_string(object):
  try:
    return object.lower()
  except AttributeError:
    return object

@register.filter
def idictsort(value, arg):
    """
    Takes a list of dicts, returns that list sorted by the property given in
    the argument. Case insensitive on strings.
    """
    var_resolve = template.Variable(arg).resolve
    decorated = [(lower_if_string(var_resolve(item)), item) for item in value]
    decorated.sort()
    return [item[1] for item in decorated]
idictsort.is_safe = False

def idictsortreversed(value, arg):
    """
    Takes a list of dicts, returns that list sorted in reverse order by the
    property given in the argument.
    """
    var_resolve = template.Variable(arg).resolve
    decorated = [(lower_if_string(var_resolve(item)), item) for item in value]
    decorated.sort()
    decorated.reverse()
    return [item[1] for item in decorated]
idictsortreversed.is_safe = False