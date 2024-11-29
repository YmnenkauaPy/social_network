from django import template
import re 

register = template.Library()

@register.filter(name='endswith')
def endswith(value, arg):
    return str(value).lower().endswith(arg.lower())
    
@register.filter
def extract_youtube_id(youtube_url):
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', youtube_url)
    if match:
        return match.group(1)
    return None