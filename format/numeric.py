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
