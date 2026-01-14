def sanitize_url(string: str):
    # Performance of this is ok. Regex would be slower.

    replace_strings = [
        "?",
        "[",
        "]",
        "/",
        "\\",
        "=",
        "<",
        ">",
        ":",
        ";",
        ",",
        "'",
        '"',
        "&",
        "$",
        "#",
        "*",
        "(",
        ")",
        "|",
        "~",
        "`",
        "!",
        "{",
        "}",
    ]

    sanitized = string
    for string in replace_strings:
        sanitized = string.replace(string, "_")

    return sanitized
