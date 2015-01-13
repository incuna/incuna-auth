import re

# Python 2/3 compatibility hackery
try:
    unicode
except NameError:
    unicode = str


def compile_url(url):
    clean_url = unicode(url).lstrip('/')
    return re.compile(clean_url)


def compile_urls(urls):
    return [compile_url(expr) for expr in urls]
