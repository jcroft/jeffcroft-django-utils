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





def _replace_entity(m): 
  entity = m.group(3) 
  if m.group(1) == '#': 
      val = int(entity, m.group(2) == '' and 10 or 16) 
  else: 
      val = name2codepoint[entity] 
  return unichr(val)

@register.filter
def deconde_entities(value):
  """ 
  Replaces HTML entities with unicode equivalents. 
  Ampersands, quotes and carets are not replaced. 
   
  """ 
  import re
  from htmlentitydefs import name2codepoint 
  from django.utils.encoding import force_unicode 

  entity_re = re.compile("&(#?)([Xx]?)(\d+|[A-Fa-f0-9]+|%s);" % '|'.join(name2codepoint)) 
  entity_no_escape_chars_re = re.compile(r"&(#?)([Xx]?)((?!39;)(\d+|[A-Fa-f0-9]+)|%s);" % '|'.join([k for k in name2codepoint if k not in ('amp', 'lt', 'gt', 'quot')])) 
  regexp = decode_all and entity_re or entity_no_escape_chars_re 
  return regexp.sub(_replace_entity, force_unicode(html)) 