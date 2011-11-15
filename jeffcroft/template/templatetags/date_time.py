from django import template
from django.template import Variable, Library, Node
from django.conf import settings
from django.utils.encoding import force_unicode

import datetime
import re


register = Library()

@register.filter
def days_since(value):
  """
  Returns number of days between today and value as a nicely formatted string.
    
    {% entry.pub_date|days_since %}
  
  """
  today = datetime.datetime.today()
  difference  = today - value
  if difference.days > 1:
    return '%s days ago' % difference.days
  elif difference.days == 1:
    return 'yesterday'
  elif difference.days == 0:
    return 'today'
  else:
    return value




@register.filter
def days_since_int(value):
  """
  Returns number of days between today and value as an integer.

    {% entry.pub_date|days_since_int %}

  """
  today = datetime.date.today()
  try:
    difference = today - value
  except:
    difference = today - value.date()
  return difference.days




@register.filter
def fuzzy_time(time):
  """
  Formats a time as fuzzy periods of the day.
  Accepts a datetime.time or datetime.datetime object.

    {% entry.pub_date|fuzzy_time %}

  """
  from bisect import bisect
  periods = ["Early-Morning", "Morning", "Mid-day", "Afternoon", "Evening", "Late-Night"]
  breakpoints = [4, 10, 13, 17, 21]
  try:
    return periods[bisect(breakpoints, time.hour)]
  except AttributeError: # Not a datetime object
    return '' #Fail silently




@register.filter  
def fuzzy_timesince(start_time):
  try:
    delta = datetime.datetime.now() - start_time

    plural = lambda x: 's' if x != 1 else ''

    num_years = delta.days / 365
    if (num_years > 0):
      return "%d year%s" % (num_years, plural(num_years))

    num_weeks = delta.days / 7
    if (num_weeks > 0):
      return "%d week%s" % (num_weeks, plural(num_weeks))

    if (delta.days > 0):
      return "%d day%s" % (delta.days, plural(delta.days))

    num_hours = delta.seconds / 3600
    if (num_hours > 0):
      return "%d hour%s" % (num_hours, plural(num_hours))

    num_minutes = delta.seconds / 60
    if (num_minutes > 0):
      return "%d minute%s" % (num_minutes, plural(num_minutes))

    return "a few seconds"
  except:
    return '' #Fail silently



@register.filter  
def fuzzy_timeuntil(start_time):
  try:
    if type(start_time) == type(datetime.date.today()):
      start_time = datetime.datetime(start_time.year, start_time.month, start_time.day)

    delta = start_time - datetime.datetime.now()

    num_years = delta.days / 365
    if (num_years > 0):
      return "%d year%s" % (num_years, plural(num_years))

    num_weeks = delta.days / 7
    if (num_weeks > 0):
      return "%d week%s" % (num_weeks, plural(num_weeks))

    if (delta.days > 0):
      return "%d day%s" % (delta.days, plural(delta.days))

    num_hours = delta.seconds / 3600
    if (num_hours > 0):
      return "%d hour%s" % (num_hours, plural(num_hours))

    num_minutes = delta.seconds / 60
    if (num_minutes > 0):
      return "%d minute%s" % (num_minutes, plural(num_minutes))

    return "a few seconds"
  except:
    return '' #Fail silently