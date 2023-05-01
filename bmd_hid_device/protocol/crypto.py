# Copyright (C) 2021 Sylvain Munaut <tnt@246tNt.com>
# SPDX-License-Identifier: Apache-2.0

# ----------------------------------------------------------------------------
# Authentication
# ----------------------------------------------------------------------------

# There is a mutual authentication mechanism where the software and the
# keyboard authenticate to each other ... without that, the keyboard
# doesn't send REPORTs :/
#
# We don't care about authenticating the keyboard so the implementation
# here is minimal, just enough to make the keyboard start working

__AUTH_EVEN_TBL = [
    0x3ae1206f97c10bc8,
    0x2a9ab32bebf244c6,
    0x20a6f8b8df9adf0a,
    0xaf80ece52cfc1719,
    0xec2ee2f7414fd151,
    0xb055adfd73344a15,
    0xa63d2e3059001187,
    0x751bf623f42e0dde,
]
__AUTH_ODD_TBL = [
    0x3e22b34f502e7fde,
    0x24656b981875ab1c,
    0xa17f3456df7bf8c3,
    0x6df72e1941aef698,
    0x72226f011e66ab94,
    0x3831a3c606296b42,
    0xfd7ff81881332c89,
    0x61a3f6474ff236c6,
]
__MASK = 0xa79a63f585d37bf0


def __rotate(data: int) -> int:
    return ((data << 56) | (data >> 8)) & 0xffffffffffffffff


def __rotate_n(data: int, n: int) -> int:
    for _ in range(n):
        data = __rotate(data)
    return data


def solve_challenge(challenge: int) -> int:
    n = challenge & 7
    v = __rotate_n(challenge, n)
    parity = (v & 1) == ((0x78 >> n) & 1)

    if not parity:
        v = v ^ __rotate(v)

    if parity:
        k = __AUTH_EVEN_TBL[n]
    else:
        k = __AUTH_ODD_TBL[n]

    return v ^ (__rotate(v) & __MASK) ^ k
