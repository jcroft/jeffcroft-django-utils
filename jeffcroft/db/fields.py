import datetime
from dateutil import parser
import re
import functools
from types import MethodType

from django.db import models
from django.template.defaultfilters import slugify
from django.db.models import DateTimeField, CharField, SlugField
from django.db.models.fields.related import ManyToManyField, ReverseManyRelatedObjectsDescriptor, ManyRelatedObjectsDescriptor
from django.db.models.query import QuerySet
from django.db.models import signals

try:
  from south.modelsinspector import add_introspection_rules
except ImportError:
  add_introspection_rules = None


class CreationDateTimeField(models.DateTimeField):
  """
  Sets editable=False, blank=True, auto_now_add=True
  """
  
  def __init__(self, *args, **kwargs):
    kwargs.setdefault('auto_now_add', True)
    models.DateTimeField.__init__(self, *args, **kwargs)
  
  def get_internal_type(self):
    return "DateTimeField"

if add_introspection_rules:
  add_introspection_rules([], ["^jeffcroft\.db\.fields\.CreationDateTimeField"])


class ModificationDateTimeField(models.DateTimeField):
  """ 
    Sets editable=False, blank=True, auto_now=True
  """
  
  def __init__(self, *args, **kwargs):
    kwargs.setdefault('auto_now_add', True)
    models.DateTimeField.__init__(self, *args, **kwargs)
  
  def get_internal_type(self):
    return "DateTimeField"

if add_introspection_rules:
  add_introspection_rules([], ["^jeffcroft\.db\.fields\.ModificationDateTimeField"])


    
class AutoSlugField(SlugField):
    """ AutoSlugField

    By default, sets editable=False, blank=True.

    Required arguments:

    populate_from
        Specifies which field or list of fields the slug is populated from.

    Optional arguments:

    separator
        Defines the used separator (default: '-')

    overwrite
        If set to True, overwrites the slug on every save (default: False)

    Inspired by SmileyChris' Unique Slugify snippet:
    http://www.djangosnippets.org/snippets/690/
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)
        kwargs.setdefault('editable', False)

        populate_from = kwargs.pop('populate_from', None)
        if populate_from is None:
            raise ValueError("missing 'populate_from' argument")
        else:
            self._populate_from = populate_from
        self.separator = kwargs.pop('separator',  u'-')
        self.overwrite = kwargs.pop('overwrite', False)
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def _slug_strip(self, value):
        """
        Cleans up a slug by removing slug separator characters that occur at
        the beginning or end of a slug.

        If an alternate separator is used, it will also replace any instances
        of the default '-' separator with the new separator.
        """
        re_sep = '(?:-|%s)' % re.escape(self.separator)
        value = re.sub('%s+' % re_sep, self.separator, value)
        return re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)

    def slugify_func(self, content):
        return slugify(content)

    def create_slug(self, model_instance, add):
        # get fields to populate from and slug field to set
        if not isinstance(self._populate_from, (list, tuple)):
            self._populate_from = (self._populate_from, )
        slug_field = model_instance._meta.get_field(self.attname)

        if add or self.overwrite:
            # slugify the original field content and set next step to 2
            slug_for_field = lambda field: self.slugify_func(getattr(model_instance, field))
            slug = self.separator.join(map(slug_for_field, self._populate_from))
            next = 2
        else:
            # get slug from the current model instance and calculate next
            # step from its number, clean-up
            slug = self._slug_strip(getattr(model_instance, self.attname))
            next = slug.split(self.separator)[-1]
            if next.isdigit():
                slug = self.separator.join(slug.split(self.separator)[:-1])
                next = int(next)
            else:
                next = 2

        # strip slug depending on max_length attribute of the slug field
        # and clean-up
        slug_len = slug_field.max_length
        if slug_len:
            slug = slug[:slug_len]
        slug = self._slug_strip(slug)
        original_slug = slug

        # exclude the current model instance from the queryset used in finding
        # the next valid slug
        queryset = model_instance.__class__._default_manager.all()
        if model_instance.pk:
            queryset = queryset.exclude(pk=model_instance.pk)

        # form a kwarg dict used to impliment any unique_together contraints
        kwargs = {}
        for params in model_instance._meta.unique_together:
            if self.attname in params:
                for param in params:
                    kwargs[param] = getattr(model_instance, param, None)
        kwargs[self.attname] = slug

        # increases the number while searching for the next valid slug
        # depending on the given slug, clean-up
        while not slug or queryset.filter(**kwargs):
            slug = original_slug
            end = '%s%s' % (self.separator, next)
            end_len = len(end)
            if slug_len and len(slug)+end_len > slug_len:
                slug = slug[:slug_len-end_len]
                slug = self._slug_strip(slug)
            slug = '%s%s' % (slug, end)
            kwargs[self.attname] = slug
            next += 1
        return slug

    def pre_save(self, model_instance, add):
        value = unicode(self.create_slug(model_instance, add))
        setattr(model_instance, self.attname, value)
        return value

    def get_internal_type(self):
        return "SlugField"

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.SlugField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)







"""Pickle field implementation for Django."""

from copy import deepcopy
from base64 import b64encode, b64decode
from zlib import compress, decompress
try:
    from cPickle import loads, dumps
except ImportError:
    from pickle import loads, dumps

from django.db import models
from django.utils.encoding import force_unicode

DEFAULT_PROTOCOL = 2

class PickledObject(str):
    """
    A subclass of string so it can be told whether a string is a pickled
    object or not (if the object is an instance of this class then it must
    [well, should] be a pickled one).

    Only really useful for passing pre-encoded values to ``default``
    with ``dbsafe_encode``, not that doing so is necessary. If you
    remove PickledObject and its references, you won't be able to pass
    in pre-encoded values anymore, but you can always just pass in the
    python objects themselves.

    """


def dbsafe_encode(value, compress_object=False, pickle_protocol=DEFAULT_PROTOCOL):
    # We use deepcopy() here to avoid a problem with cPickle, where dumps
    # can generate different character streams for same lookup value if
    # they are referenced differently.
    # The reason this is important is because we do all of our lookups as
    # simple string matches, thus the character streams must be the same
    # for the lookups to work properly. See tests.py for more information.
    if not compress_object:
        value = b64encode(dumps(deepcopy(value), pickle_protocol))
    else:
        value = b64encode(compress(dumps(deepcopy(value), pickle_protocol)))
    return PickledObject(value)


def dbsafe_decode(value, compress_object=False):
    if not compress_object:
        value = loads(b64decode(value))
    else:
        value = loads(decompress(b64decode(value)))
    return value


class PickledObjectField(models.Field):
    """
    A field that will accept *any* python object and store it in the
    database. PickledObjectField will optionally compress its values if
    declared with the keyword argument ``compress=True``.

    Does not actually encode and compress ``None`` objects (although you
    can still do lookups using None). This way, it is still possible to
    use the ``isnull`` lookup type correctly.
    """

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.compress = kwargs.pop('compress', False)
        self.protocol = kwargs.pop('protocol', DEFAULT_PROTOCOL)
        kwargs.setdefault('editable', False)
        super(PickledObjectField, self).__init__(*args, **kwargs)

    def get_default(self):
        """
        Returns the default value for this field.

        The default implementation on models.Field calls force_unicode
        on the default, which means you can't set arbitrary Python
        objects as the default. To fix this, we just return the value
        without calling force_unicode on it. Note that if you set a
        callable as a default, the field will still call it. It will
        *not* try to pickle and encode it.

        """
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        # If the field doesn't have a default, then we punt to models.Field.
        return super(PickledObjectField, self).get_default()

    def to_python(self, value):
        """
        B64decode and unpickle the object, optionally decompressing it.

        If an error is raised in de-pickling and we're sure the value is
        a definite pickle, the error is allowed to propogate. If we
        aren't sure if the value is a pickle or not, then we catch the
        error and return the original value instead.

        """
        if value is not None:
            try:
                value = dbsafe_decode(value, self.compress)
            except:
                # If the value is a definite pickle; and an error is raised in
                # de-pickling it should be allowed to propogate.
                if isinstance(value, PickledObject):
                    raise
        return value

    def get_db_prep_value(self, value, connection, prepared):
        """
        Pickle and b64encode the object, optionally compressing it.

        The pickling protocol is specified explicitly (by default 2),
        rather than as -1 or HIGHEST_PROTOCOL, because we don't want the
        protocol to change over time. If it did, ``exact`` and ``in``
        lookups would likely fail, since pickle would now be generating
        a different string.

        """
        if value is not None and not isinstance(value, PickledObject):
            # We call force_unicode here explicitly, so that the encoded string
            # isn't rejected by the postgresql_psycopg2 backend. Alternatively,
            # we could have just registered PickledObject with the psycopg
            # marshaller (telling it to store it like it would a string), but
            # since both of these methods result in the same value being stored,
            # doing things this way is much easier.
            value = force_unicode(dbsafe_encode(value, self.compress, self.protocol))
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

    def get_internal_type(self):
        return 'TextField'

    def get_db_prep_lookup(self, lookup_type, value, connection=None, prepared=False):
        if lookup_type not in ['exact', 'in', 'isnull', 'contains', 'icontains']:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)
        # The Field model already calls get_db_prep_value before doing the
        # actual lookup, so all we need to do is limit the lookup types.
        try:
            return super(PickledObjectField, self).get_db_prep_lookup(
                lookup_type, value, connection=connection, prepared=prepared)
        except TypeError:
            # Try not to break on older versions of Django, where the
            # `connection` and `prepared` parameters are not available.
            return super(PickledObjectField, self).get_db_prep_lookup(
                lookup_type, value)


# South support; see http://south.aeracode.org/docs/tutorial/part4.html#simple-inheritance
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], [r"^jeffcroft\.db\.fields\.PickledObjectField"])
