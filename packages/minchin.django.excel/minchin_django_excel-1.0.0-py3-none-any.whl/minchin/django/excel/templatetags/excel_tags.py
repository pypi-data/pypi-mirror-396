from django import template
from django.contrib.admin.views.main import PAGE_VAR
from django.template import Node, TemplateSyntaxError
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def back_url(cl, i):
    """
    Generate url for Back button in admin pagination.
    """
    if i == cl.paginator.ELLIPSIS:
        return format_html("{} ", cl.paginator.ELLIPSIS)
    elif cl.page_num > 0:
        return format_html(
            '<a href="{}">{}</a> ',
            cl.get_query_string({PAGE_VAR: cl.page_num - 1}),
            "Prev.",
        )
    else:
        return ""


@register.simple_tag
def forward_url(cl, i):
    """
    Generate url for Forward button in admin pagination.
    """
    if i == cl.paginator.ELLIPSIS:
        return format_html("{} ", cl.paginator.ELLIPSIS)
    elif cl.page_num + 1 < cl.paginator.num_pages:
        return format_html(
            '<a href="{}">{}</a> ',
            cl.get_query_string({PAGE_VAR: cl.page_num + 1}),
            "Next",
        )
    else:
        return ""


# based on: http://www.djangosnippets.org/snippets/779/
class RangeNode(Node):
    def __init__(self, range_args, context_name):
        self.range_args = range_args
        self.context_name = context_name

    def render(self, context):
        context[self.context_name] = range(
            *[x.resolve(context) for x in self.range_args]
        )
        return ""


@register.tag
def make_range(context, token):
    """
    Accepts the same arguments as the 'range' builtin and creates
    a list containing the result of 'range'.

    Syntax:
        {% mkrange [start,] stop[, step] as context_name %}

    For example:
        {% mkrange 5 10 2 as some_range %}
        {% for i in some_range %}
            {{ i }}: Something I want to repeat\n
        {% endfor %}

    Produces:
        5: Something I want to repeat
        7: Something I want to repeat
        9: Something I want to repeat
    """
    tokens = token.split_contents()
    fnctl = tokens.pop(0)

    def error(msg=None):
        raise TemplateSyntaxError(
            "%s accepts the syntax: "
            "{%% %s [start,] stop[, step] as context_name %%}, where 'start', "
            "'stop' and 'step' must all be integers. %s" % (fnctl, fnctl, msg)
        )

    range_args = []
    while True:
        if len(tokens) < 2:
            error('Did not receive a "stop" value.')

        my_token = tokens.pop(0)

        if my_token == "as":
            break
        # print(my_token)
        # raise()

        try:
            my_token = int(my_token)
        except ValueError:
            try:
                # allow passing a template variable as any of the number parameters
                my_token = template.Variable(my_token)
            except template.VariableDoesNotExist:
                error('"%s" is not a number or a valid template variable.' % my_token)
            # else:
            #     my_token = my_token.resolve(context)
        # print(my_token, type(my_token))
        range_args.append(my_token)

    if len(tokens) != 1:
        error('Can only provide a single value after "as".')

    context_name = tokens.pop()

    return RangeNode(range_args, context_name)
