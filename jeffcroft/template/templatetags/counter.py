from django import template

register = template.Library()

@register.tag(name='counter')
def do_counter(parser, token):
    """
    The counter initializes the variable to 0, and next it increments one by one:

    {% load counter_tag %}
    {% for pet in pets %}
        {% if pet.is_cat %}
            {% counter cats %}
        {% else %}
            {% counter dogs %}
        {% endif %}
    {% endfor %}
    cats: {{cats}}
    dogs: {{dogs}}
    
    """
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'counter' node requires a variable name.")
    return CounterNode(args)




class CounterNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        try:
            var = template.resolve_variable(self.varname, context)
        except:
            var = 0
        deep = len(context.dicts)-1
        context.dicts[deep][self.varname] = var+1
        return ''