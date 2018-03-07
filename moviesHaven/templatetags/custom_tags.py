from django import template
register = template.Library()


@register.filter
def message_filter(msg, **kwargs):
    if msg.message.lower().startswith("error"):
        return 'text-danger'
    else:
        return 'class=row text-success'


@register.filter
def get_display(arg, **kwargs):
    print(arg)
    return arg


@register.filter
def filter_range(start, end):
    return range(start, end)
