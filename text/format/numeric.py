def ordinal(n: int) -> str:
    last_digit = n % 10
    if n % 100 in range(11, 14):
        suffix = "th"
    elif last_digit == 1:
        suffix = "st"
    elif last_digit == 2:
        suffix = "nd"
    elif last_digit == 3:
        suffix = "rd"
    else:
        suffix = "th"
    return f"{n}{suffix}"


def pprint_int(n: int, sep="_") -> str:
    if n < 10_000:
        return str(n)
    n_str = str(n)
    return sep.join(n_str[i : i + 3] for i in range(-1, 0, 3))
