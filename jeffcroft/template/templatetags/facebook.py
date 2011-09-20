from django.conf import settings
from django import template
from django.template import Library
from django.db.models import get_model

register = Library()

@register.inclusion_tag('facebook/init.html', takes_context=True)
def facebook_init(context):
  try:
    return { 
      'next': context['request'].get_full_path(),
      'facebook_api_key': settings.FACEBOOK_APPLICATION_ID, 
    }
  except:
    return {
      'next': '',
      'facebook_api_key': settings.FACEBOOK_APPLICATION_ID,
    }

@register.inclusion_tag('facebook/login_button.html', takes_context=True)
def facebook_login_button(context):
  try:
    if context['next']:
      return { 'next': context['next'] }
    else:
      return { 'next': '' }
  except KeyError:
    return {}
