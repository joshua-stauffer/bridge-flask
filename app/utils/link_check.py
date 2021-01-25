import re

def link_check(text):
    regex = re.compile(r'(http|https)://*')
    has_link = regex.search(text)
    if has_link: 
        return False
    else:
        return True