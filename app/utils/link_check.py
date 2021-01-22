import re

def link_check(text):
    forbidden = re.compile(r'(http|https)://*')
    has_link = forbidden.search(text)
    if has_link: 
        return False
    else:
        return True