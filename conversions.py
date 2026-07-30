def bi_to_hd(s: str) -> str:
    dec = (
        2 ** 3 * int(s[0])
        + 2 ** 2 * int(s[1])
        + 2 ** 1 * int(s[2])
        + 2 ** 0 * int(s[3])
    )
    if dec < 10:
        return chr(dec + 48)
    else:
        return chr(dec + 87)


def dec_to_bi(dec: int, s: str) -> str:
    if dec >= 2:
        s = dec_to_bi(int(dec / 2), s)
    return s + str(dec % 2)


def hd_to_bi(hexadec: str) -> str:
    dec = int(hexadec, 16)
    s = dec_to_bi(dec, "")
    if len(s) < 4:
        for _ in range(4 - len(s)):
            s = "0" + s
    return s
