import re

EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\. \w+$")
PHONE_RE = re.compile(r"^\d{10,13}$")

def _partial(text, start=2, end=2):
    if len(text) <= start + end:
        return "*" * len(text)
    return text[:start] + "*" * (len(text) - start - end) + text[-end:]

def mask(value):
    text = str(value).strip()

    if EMAIL_RE.match(text):
        name, domain = text.split("@")
        return _partial(name, 1, 1) + "@" + domain
    
    if PHONE_RE.match(text):
        return _partial(text)
    
    return _partial(text, 1, 1)

