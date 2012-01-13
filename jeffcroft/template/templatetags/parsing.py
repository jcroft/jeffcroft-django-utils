from django import template
from django.utils.safestring import mark_safe
 
register = template.Library()

@register.filter
def get_links(value):
  """
  Returns links found in an (X)HTML string as Python objects for iteration in templates.

    <ul>
      {% for link in object.body|markdown|get_links %}
        <li><a href="{{ link.href }}">{{ link.title }}</a></li>
      {% endfor %}
    </ul>

  """
  
  try:
    from BeautifulSoup import BeautifulSoup
    import urllib2
  except ImportError:
    if settings.DEBUG:
      raise template.TemplateSyntaxError, "Error in {% get_links %} filter: The Python BeautifulSoup and/or urllib2 libraries aren't installed."
    return value
  soup = BeautifulSoup(value)
  return [ {'href': a.href, 'title': a.title } for a in soup.findAll('a') ]