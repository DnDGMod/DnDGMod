import re
import unicodedata

def generate_slug(name):
    """Generate a slug from a full name.
        Adapted from https://github.com/django/django/blob/master/django/utils/text.py"""
    slug = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^\w\s-]', '', slug.lower())
    return re.sub(r'[-\s]+', '-', slug).strip('-_')
