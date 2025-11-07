def sanitize_url(string: str):
    # TODO
    sanitized = (
        string.replace("#", "_")
        .replace("/", "_")
        .replace(" ", "_")
        .replace("#", "")
        .replace("#", "")
        .replace("#", "")
        .replace("#", "")
    )

    return sanitized
