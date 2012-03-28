from django import forms
from django.forms.widgets import Input, MultiWidget
from django.utils.safestring import mark_safe
from django.utils.dateformat import format, time_format

import datetime
import simplejson

try:
  from parsedatetime import Calendar
except ImportError:
  from parsedatetime.parsedatetime import Calendar

class AutoCompleteInput(forms.TextInput):
  def __init__(self, attrs=None, items=[], multiple=False):
    if attrs is not None:
      self.attrs = attrs.copy()
    else:
      self.attrs = {}
    self.items = items
    self.multiple = multiple
  
  def render(self, name, value, attrs=None):
    output = super(AutoCompleteInput, self).render(name, value, attrs)
    items = self.items
    item_json = simplejson.dumps(items, ensure_ascii=False)
    if self.multiple:
      multiple = "true"
    else:
      multiple = "false"
    return output + mark_safe(u'''
      <script type="text/javascript">
        if(typeof(jQuery) === "function"){
          jQuery("#id_%s").autocomplete(%s, {
            width: 292,
            max: 10,
            highlight: false,
            multiple: %s,
            multipleSeparator: ", ",
            scroll: true,
            scrollHeight: 300,
            matchContains: true,
            autoFill: false,
          });
        }
      </script>
    ''' % (name, item_json, multiple))

class NaturalDateInput(Input):
    input_type = 'text'
    format = 'M jS Y' # 'Oct 31st 2009'
        
    def __init__(self, attrs=None, format=None):
        if not attrs:
            attrs = {'class': 'natural_dtinput'}
        else:
            if 'class' in attrs:
                attrs['class'] += ' natural_dtinput'
            else:
                attrs['class'] = 'natural_dtinput'
        super(NaturalDateInput, self).__init__(attrs)
        if format:
            self.format = format        
        self.attrs['title'] = 'Date'
    
    def _format_value(self, value):
        if value is None:
            return ''
        elif not isinstance(value, datetime.date):
            return value
        else:
            return format(value, self.format)
    
    def render(self, name, value, attrs=None):
        value = self._format_value(value)
        rendered = super(NaturalDateInput, self).render(name, value, attrs)
        return rendered
    
    def _has_changed(self, initial, data):
        return super(NaturalDateInput, self)._has_changed(self._format_value(initial), data)

class NaturalTimeInput(Input):
    input_type = 'text'
    format = 'g:i A' # '11:59 PM'
    
    def __init__(self, attrs=None, format=None):
        if not attrs:
            attrs = {'class': 'natural_dtinput'}
        else:
            if 'class' in attrs:
                attrs['class'] += ' natural_dtinput'
            else:
                attrs['class'] = 'natural_dtinput'
        
        super(NaturalTimeInput, self).__init__(attrs)
        if format:
            self.format = format        
        self.attrs['title'] = 'Time'
        
    def _format_value(self, value):
        if value is None:
            return ''
        elif not isinstance(value, datetime.time):
            return value
        else:
            return time_format(value, self.format)
    
    def render(self, name, value, attrs=None):
        value = self._format_value(value)
        rendered = super(NaturalTimeInput, self).render(name, value, attrs)
        return rendered
    
    def _has_changed(self, initial, data):
        return super(NaturalTimeInput, self)._has_changed(self._format_value(initial), data)

class NaturalDateTimeInput(Input):
    input_type = 'text'
    format = 'M jS Y, g:i A' # 'Oct 31st 2009, 11:59 PM'
    
    def __init__(self, attrs=None, format=None):
        if not attrs:
            attrs = {'class': 'natural_dtinput'}
        else:
            if 'class' in attrs:
                attrs['class'] += ' natural_dtinput'
            else:
                attrs['class'] = 'natural_dtinput'
        super(NaturalDateTimeInput, self).__init__(attrs)
        if format:
            self.format = format        
        self.attrs['title'] = 'Date and Time'
    
    def _format_value(self, value):
        if value is None:
            return ''
        else:
            return format(value, self.format)
    
    def render(self, name, value, attrs=None):
        value = self._format_value(value)
        rendered = super(NaturalDateTimeInput, self).render(name, value, attrs)
        return rendered
    
    def _has_changed(self, initial, data):
        return super(NaturalDateTimeInput, self)._has_changed(self._format_value(initial), data)

class SplitNaturalDateTimeWidget(MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """
    date_format = NaturalDateInput.format
    time_format = NaturalTimeInput.format

    def __init__(self,attrs=None, date_format=None, time_format=None):
        if date_format:
            self.date_format = date_format
        if time_format:
            self.time_format = time_format
        
        widgets = (
            NaturalDateInput(attrs=attrs, format=self.date_format),
            NaturalTimeInput(attrs=attrs, format=self.time_format),
        )
        super(SplitNaturalDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]




class AutocompleteFromExistingEntriesInput(forms.TextInput):

  def __init__(self, queryset, field_name, *args, **kwargs):
    super(AutocompleteFromExistingEntriesInput, self).__init__(*args, **kwargs)
    self.queryset = queryset
    self.field_name = field_name

  def render(self, name, value, attrs=None):
    output = super(AutocompleteFromExistingEntriesInput, self).render(name, value, attrs=attrs)
    items = self.get_existing_entries(self.queryset, self.field_name)
    item_json = simplejson.dumps(items, ensure_ascii=False)
    return output + mark_safe(u'''
      <script type="text/javascript">
        if(typeof(jQuery) === "function"){
          jQuery("#id_%s").autocomplete(%s, {
            max: 10,
            highlight: false,
            multiple: false,
            multipleSeparator: ", ",
            scroll: true,
            scrollHeight: 300,
            matchContains: true,
            autoFill: false,
            selectFirst: false,
          });
        }
      </script>
    ''' % (name, item_json))

  def get_existing_entries(self, queryset, field_name):
    entries = queryset.values_list(field_name, flat=True)

    # Return the entries, while removing duplicates.
    return list(set(entries))