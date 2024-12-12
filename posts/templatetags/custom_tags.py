from django import template
import re, os

register = template.Library()

@register.filter(name='endswith')
def endswith(value, arg):
    extensions = [ext.strip() for ext in arg.split(',')]
    return any(str(value).lower().endswith(ext.lower()) for ext in extensions)
    
@register.filter
def extract_youtube_id(youtube_url):
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', youtube_url)
    if match:
        return match.group(1)
    return None

@register.filter
def file_extension(file_url):
    _, ext = os.path.splitext(file_url)
    return ext.lstrip('.') 