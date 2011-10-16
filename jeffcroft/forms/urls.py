from django.conf.urls.defaults import *

urlpatterns = patterns('django_utils.forms.views',
    url(r'^', 'fuzzydtparse', name='fuzzydtparse'),
)
