from django.conf.urls.defaults import *

urlpatterns = patterns('jeffcroft.forms.views',
    url(r'^', 'fuzzydtparse', name='fuzzydtparse'),
)
