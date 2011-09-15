from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.tag
def render_template_for(parser, token):
    """
    Renders a template matching the app_name.module_name of the given object 
    in the given template directory, falling back to default.html.
    
    If called as ``{% render_tempate_for story_object in "includes/story_list_snippets" %}``
    it would first look for includes/story_list_snippets/news.stories.html and then
    for includes/story_list_snippets/default.html
    
    This is particularly useful when dealing with object of unknown type as 
    it keeps nasty nested {% if %} blocks out and allows you to customize where desired.
    
    The object passed to the tag will be available in the rendered template 
    as ``object``. The current context is also made available.
    """
    try:
        tag_name, object, in_var, template_dir = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments '[object] in [template_dir]'" % token.contents.split()[0]
    if not (in_var == 'in'):
        raise template.TemplateSyntaxError, "%s tag's second argument must be the keyword 'in'" % tag_name
    if not (template_dir[0] == template_dir[-1] and template_dir[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%s tag's final argument should be in quotes" % tag_name
    return RenderTemplateForNode(object, template_dir[1:-1])





class RenderTemplateForNode(template.Node):
  
    def __init__(self, object, template_dir):
        self.object = template.Variable(object)
        # Normalize template_dirs that end in /
        if template_dir[-1] == "/":
            self.template_dir = template_dir[:-1]
        else:
            self.template_dir = template_dir

    def render(self, context):
        try:
            object = self.object.resolve(context)
            ctype_str = "%s.%s" % (object._meta.app_label, object._meta.module_name)
            context.push()
            context['object'] = object
            return render_to_string(["%s/%s.html" % (self.template_dir, ctype_str), 
                                     "%s/default.html" % self.template_dir],
                                     context)
        except (template.VariableDoesNotExist, AttributeError):
            return ''
