VALID_CHARACTER = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.()[]' "
)


def remove_illegal_file_chars(filename):
    """Remove illegal characters from a filename"""
    # remove emojis as well
    result = []
    for c in filename:
        if c not in VALID_CHARACTER:
            result.append("-")
        else:
            result.append(c)
    return "".join(result).strip()
