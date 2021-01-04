stopchars = set([' ', '.', ',', '!', ':', ':', '?'])

def get_preview_text(text, max_char_count=120):
    """text: string of text to be shortened
    max_char_count: int (default 120)
    returns string, shortened to nearest word shorter than max_char_count
    """
    i = max_char_count
    char = text[i]
    while char not in stopchars:
        i -= 1
        char = text[i]
    return text[:i] + '...'
