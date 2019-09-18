from django.template.defaulttags import register
...
@register.filter
def get_item_len(dictionary, key):
    return len(dictionary.get(key))