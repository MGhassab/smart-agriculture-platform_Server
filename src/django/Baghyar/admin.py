from django.db.models import Model
from django.urls import reverse
from django.utils.html import format_html


def get_linked_repr(obj: Model, name, prefix=None):
    try:
        url = reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
            args=(obj.id,)
        )
        if prefix:
            return format_html('{}.<a href="{}">{}</a>', prefix, url, name)
        return format_html('<a href="{}">{}</a>', url, name)
    except TypeError:
        return None


def get_linked_named_model_repr(obj):
    if obj is None:
        return None
    try:
        return get_linked_repr(obj, obj.name, obj.id)
    except AttributeError:
        try:
            return get_linked_repr(obj, obj.id)
        except AttributeError:
            return None

