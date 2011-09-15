from django.views.debug import technical_500_response
import sys

class UserBasedExceptionMiddleware(object):
  """
  For superusers, always show the debug error screens, even if DEBUG is False.
  """
  def process_exception(self, request, exception):
    if request.user.is_superuser:
      return technical_500_response(request, *sys.exc_info())