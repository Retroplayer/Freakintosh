"""Print a MacGPIO v1 frame; standard-library desktop Python, no serial I/O."""

import argparse
import binascii


def frame(body):
    encoded = body.encode("ascii")
    if not 1 <= len(encoded) <= 120:
        raise ValueError("body must contain 1–120 ASCII bytes")
    tokens = body.split(" ")
    if any(not token or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                            for c in token) for token in tokens):
        raise ValueError("use uppercase tokens separated by single spaces")
    if not tokens[0].isdigit() or str(int(tokens[0])) != tokens[0]:
        raise ValueError("sequence must be canonical decimal")
    if not 1 <= int(tokens[0]) <= 65535 or len(tokens) < 2:
        raise ValueError("expected sequence 1–65535 followed by command")
    crc = binascii.crc_hqx(encoded, 0xFFFF)
    return "@%s*%04X\r\n" % (body, crc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("body", help='e.g. "1 HELLO 1"')
    args = parser.parse_args()
    try:
        result = frame(args.body)
    except (ValueError, UnicodeError) as error:
        parser.error(str(error))
    print(result, end="")
