import re

from django.db import models

def get_unique_slug_value(queryset, proposal, field_name="slug", instance_pk=None, separator="-"):
    """ Returns unique string by the proposed one.
    Optionally takes:
    * field name which can  be 'slug', 'username', 'invoice_number', etc.
    * the primary key of the instance to which the string will be assigned.
    * separator which can be '-', '_', ' ', '', etc.
    By default, for proposal 'example' returns strings from the sequence:
        'example', 'example-2', 'example-3', 'example-4', ...
    """
    
    if instance_pk:
        similar_ones = queryset.filter(**{field_name + "__startswith": proposal}).exclude(pk=instance_pk).values(field_name)
    else:
        similar_ones = queryset.filter(**{field_name + "__startswith": proposal}).values(field_name)
    similar_ones = [elem[field_name] for elem in similar_ones]
    if proposal not in similar_ones:
        return proposal
    else:
        numbers = []
        for value in similar_ones:
            match = re.match(r'^%s%s(\d+)$' % (proposal, separator), value)
            if match:
                numbers.append(int(match.group(1)))
        if len(numbers)==0:
            return "%s%s2" % (proposal, separator)
        else:
            largest = sorted(numbers)[-1]
            return "%s%s%d" % (proposal, separator, largest + 1)