def human_format(num):
    """
    Convert a large number to a human-readable string with suffixes:
    K = thousand, M = million, B = billion, T = trillion.
    """
    for unit in ["", "K", "M", "B", "T"]:
        if abs(num) < 1000:
            return f"{num:.1f}{unit}".rstrip('0').rstrip('.')
        num /= 1000
    return f"{num:.1f}T".rstrip('0').rstrip('.')
