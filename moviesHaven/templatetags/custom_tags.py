from django import template
register = template.Library()


@register.filter
def message_filter(msg, **kwargs):
    if msg.message.lower().startswith("error"):
        return 'text-danger'
    else:
        return 'class=row text-success'


@register.filter
def toogle_button_status(thread_instance, *args):
    if thread_instance:
        if thread_instance.status != 0:
            return "enabled"
