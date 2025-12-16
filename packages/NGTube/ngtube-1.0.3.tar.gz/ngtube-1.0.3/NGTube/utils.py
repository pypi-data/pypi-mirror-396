import re


def extract_number(text):
    """
    Extract and parse numbers from text, handling German number formatting.

    Args:
        text (str): The text containing numbers.

    Returns:
        int: The extracted number.
    """
    if not text:
        return 0
    text = text.strip()
    multiplier = 1
    if 'Mio' in text:
        multiplier = 1000000
        text = text.replace('Mio.', '').replace('Mio', '').strip()
    elif 'M' in text and 'Mio' not in text:
        multiplier = 1000000
        text = text.replace('M', '').strip()
    elif 'K' in text:
        multiplier = 1000
        text = text.replace('K', '').strip()
    cleaned = re.sub(r'[^\d.,]', '', text)
    if multiplier == 1:
        # No multiplier, treat as integer with thousand separators
        cleaned = cleaned.replace(',', '')
    else:
        # With multiplier, handle decimal
        if '.' in cleaned and ',' not in cleaned:
            pass  # already good
        elif ',' in cleaned and '.' not in cleaned:
            cleaned = cleaned.replace(',', '.')
        elif ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace('.', '').replace(',', '.')
    try:
        num = float(cleaned)
        return int(num * multiplier)
    except Exception:
        return 0


def extract_links(text):
    """
    Extract URLs from text.

    Args:
        text (str): The text containing URLs.

    Returns:
        list: List of extracted URLs.
    """
    if not text:
        return []
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    return urls