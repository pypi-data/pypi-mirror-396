# FilterGenius

Smart filters to detect:
- Email / Gmail  
- Phone numbers  
- Emojis  
- Integer / Float / Boolean  
- Alphanumeric  
- URL  
- Whitespace  
- Special characters  

## Install
pip install filtergenius

## Usage
```python
import filtergenius as fg

print(fg.is_email("abc@test.com"))
print(fg.is_gmail("xyz@gmail.com"))
print(fg.is_phone("+1 555 234 5678"))
print(fg.has_emoji("Hi 😊"))
print(fg.is_int("123"))
print(fg.is_float("12.5"))
print(fg.is_bool("true"))
print(fg.is_alphanumeric("abc123"))
print(fg.is_url("https://google.com"))
print(fg.is_whitespace("   "))
print(fg.has_special_char("hi@"))
