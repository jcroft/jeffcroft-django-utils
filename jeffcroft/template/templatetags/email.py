from django import template

register = template.Library()

@register.filter
def html_encode(text):
    return ''.join(map(lambda c:'%%%x'%ord(c),text))
html_encode.is_safe=True

@register.filter
def html_encode_email(email):
    return '<a href="mailto:%s">%s</a>' % (html_encode(email),email)
html_encode_email.is_safe=True