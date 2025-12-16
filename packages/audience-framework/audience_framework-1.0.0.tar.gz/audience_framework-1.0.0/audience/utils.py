import re


def mask_password(url_string: str) -> str:
    """Маскирует пароль в строках типа 'amqp://admin:password@localhost'"""
    pattern = r'(://[^:]+:)[^@]+(@)'
    
    def replace_password(match: re.Match[str]) -> str:
        return f"{match.group(1)}******{match.group(2)}"
    
    return re.sub(pattern, replace_password, url_string)
