"""
Collection of template tags usefull in  projects
"""
import datetime
import re

from django import template
from django.urls import reverse, NoReverseMatch
import urllib

from django.utils.safestring import mark_safe

from server import settings

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, field, value):
    """
    Construct a GET query url with a parameter keeping other values
    """
    request = context['request']
    dict_ = request.GET.copy()
    dict_[field] = value
    return urllib.parse.urlencode(dict_)

@register.simple_tag(takes_context=True)
def url_replace_with_inverse(context, field):
    """
    Construct a GET query url with a parameter keeping other values and inversing existing for ordering purposes
    """
    request = context['request']
    dict_ = request.GET.copy()
    if field in dict_.get('order', ''):
        if dict_['order'].startswith('-'):
            dict_['order'] = field
        else:
            dict_['order'] = '-' + field
    else:
        dict_['order'] = field

    return urllib.parse.urlencode(dict_)


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    """
    Check if link is active
    Usage : class='(% active 'blog:news-list'%)' will be replace by class='active'
            if current url is 'blog:news-list'
    """
    try:
        pattern = '^' + reverse(pattern_or_urlname) + '$'
    except NoReverseMatch:
        pattern = pattern_or_urlname
    path = context['request'].get_full_path().split("?")[0]
    if re.search(pattern, path):
        return 'active'
    return ''



@register.filter()
def is_form_locked(intervention, user):
    if intervention:
        return intervention.is_form_locked(user)
    return True



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag()
def get_verbose_name(instance, field_name):
    return instance._meta.get_field(field_name).verbose_name

@register.filter
def show_field_value(instance, field):
    print(field)
    value = None
    field_name = field["name"]
    if field["internal_type"] == "TextField":
        if len(getattr(instance, field_name))>50:
            return getattr(instance, field_name)[:50]
        return getattr(instance, field_name)

    if 'photo' in field_name:
        if getattr(instance, field_name):
            return f"""<span class="avatar avatar-xl" style="background-image: url('{getattr(instance, field_name).url}')"></span>"""
        return ""
    if "__" in field_name:
        foreign_key, field_name = field_name.split("__")
        instance = getattr(instance, foreign_key)
    if field["internal_type"] in ["ManyToOneRel", "ManyToManyField"]:
        value = ""
        for item in getattr(instance, field_name).all():
            value += f"<li>{item}</li>"
    elif instance and hasattr(instance, f"get_{field_name}_display"):
        return getattr(instance, f"get_{field_name}_display")() or ""
    elif instance:
        value = getattr(instance, field_name)
    if isinstance(value, str) and value.startswith("http"):
        return f'<a href="{value}">link</a>'
    if value is None:
        return ''
    elif value is True:
        return 'Oui'
    elif value is False:
        return 'Non'
    elif isinstance(value, datetime.date):
        return value.strftime('%d/%m/%Y')
    elif isinstance(value, datetime.datetime):
        return value.strftime('%d/%m/%Y %H:%M')
    elif "video" in field_name and value:
        return f'<a href="{value.url}" class="nolink" data-fslightbox="video">Video</a>'
    elif value and hasattr(value, 'url'):
        return f'<a href="{value.url}">{field_name}</a>'
    elif isinstance(value, (int, float)) and any(x in field["verbose_name"] for x in ["Index actuel"]):
        return f"{value:,.0f} {instance.unite}".replace(",", " ")
    return mark_safe(value)