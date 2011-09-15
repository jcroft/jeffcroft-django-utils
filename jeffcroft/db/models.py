import datetime
from django.db import models
from django.contrib.auth.models import User

from jeffcroft.db.fields import *




class CreationDateMixin(models.Model):
  date_created = CreationDateTimeField()
  class Meta:
    abstract=True




class ModificationDateMixin(models.Model):
  date_modified = ModificationDateTimeField()
  class Meta:
    abstract=True



    
class CreationUserMixin(models.Model):
  created_by    = models.ForeignKey(User, null=True, blank=True, related_name="%(class)s_created" )
  class Meta:
    abstract=True




class ModificationUserMixin(models.Model):
  updated_by    = models.ForeignKey(User, null=True, blank=True, editable=False, related_name="%(class)s_updated")
  class Meta:
    abstract=True