stopchars = set([' ', '.', ',', '!', ':', ':', '?'])

def get_preview_text(text, max_char_count=120):
    """text: string of text to be shortened
    max_char_count: int (default 120)
    returns string, shortened to nearest word shorter than max_char_count
    """
    i = max_char_count
    try:
        char = text[i]
    except IndexError:
        return text
    while char not in stopchars and i > 0:
        i -= 1
        char = text[i]
    # no spaces or punctuation? interrupt word at ideal length
    if i == 0:
        return text[:max_char_count] + '...'
    return text[:i] + '...'
