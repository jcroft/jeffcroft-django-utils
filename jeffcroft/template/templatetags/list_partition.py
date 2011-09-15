from __future__ import division
from django import template
from django.template.loader import render_to_string

register = template.Library()

def grouper(n, iterable):
  import itertools
  "grouper(3, 'ABCDEFG') --> ABC DEF G"
  args = [iter(iterable)] * n
  return list(list(n for n in t if n)
       for t in itertools.izip_longest(*args))




@register.filter
def partition_every(thelist, n):
  new_lists = grouper(n, thelist)
  return new_lists




@register.filter
def partition(thelist, n):
  """
  Break a list into ``n`` pieces. The last list may be larger than the rest if
  the list doesn't break cleanly. That is::

  >>> l = range(10)

  >>> partition(l, 2)
  [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

  >>> partition(l, 3)
  [[0, 1, 2], [3, 4, 5], [6, 7, 8, 9]]

  >>> partition(l, 4)
  [[0, 1], [2, 3], [4, 5], [6, 7, 8, 9]]

  >>> partition(l, 5)
  [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
  
    {% for sublist in mylist|parition:"3" %}
      {% for item in sublist %}
        do something with {{ item }}
      {% endfor %}
    {% endfor %}

  """
  try:
    n = int(n)
    thelist = list(thelist)
  except (ValueError, TypeError):
    return [thelist]
  p = len(thelist) / n
  return [thelist[p*i:p*(i+1)] for i in range(n - 1)] + [thelist[p*(i+1):]]



@register.filter
def partition_horizontal(thelist, n):
  """
  Break a list into ``n`` peices, but "horizontally." That is, 
  ``partition_horizontal(range(10), 3)`` gives::

    [[1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    [10]]
  """
    
  try:
    n = int(n)
    thelist = list(thelist)
  except (ValueError, TypeError):
    return [thelist]
  newlists = [list() for i in range(n)]
  for i, val in enumerate(thelist):
    newlists[i%n].append(val)
  return newlists