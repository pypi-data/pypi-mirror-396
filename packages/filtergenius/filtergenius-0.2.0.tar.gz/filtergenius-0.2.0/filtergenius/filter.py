import re

EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
GMAIL_PATTERN = re.compile(r"^[\w\.-]+@gmail\.com$")
PHONE_PATTERN = re.compile(r"^\+?\d[\d\-\s]{7,}\d$")
URL_PATTERN = re.compile(r"^https?:\/\/[\w\-]+(\.[\w\-]+)+[/#?]?.*$", re.IGNORECASE)
EMOJI_PATTERN = re.compile(
    "[" 
    "\U0001F600-\U0001F64F" 
    "\U0001F300-\U0001F5FF" 
    "\U0001F680-\U0001F6FF" 
    "\U0001F1E0-\U0001F1FF"
    "]+",
    flags=re.UNICODE
)
SPECIAL_CHAR_PATTERN = re.compile(r"[^A-Za-z0-9 ]")

def is_email(text: str) -> bool:
    return bool(EMAIL_PATTERN.match(text))

def is_gmail(text: str) -> bool:
    return bool(GMAIL_PATTERN.match(text))

def is_phone(text: str) -> bool:
    return bool(PHONE_PATTERN.match(text))

def has_emoji(text: str) -> bool:
    return bool(EMOJI_PATTERN.search(text))

def is_int(text: str) -> bool:
    try:
        int(text)
        return True
    except:
        return False

def is_float(text: str) -> bool:
    try:
        float(text)
        return True
    except:
        return False

def is_bool(text: str) -> bool:
    return str(text).lower() in ["true", "false"]

def is_str(text) -> bool:
    return isinstance(text, str)

def is_alphanumeric(text: str) -> bool:
    return text.isalnum()

def is_url(text: str) -> bool:
    return bool(URL_PATTERN.match(text))

def is_whitespace(text: str) -> bool:
    return text.strip() == ""

def has_special_char(text: str) -> bool:
    return bool(SPECIAL_CHAR_PATTERN.search(text))



