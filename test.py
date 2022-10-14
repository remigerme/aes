from os import urandom
import aes

# IO <-> str
def str_to_io(s: str) -> aes.IO:
    return list(bytearray(s, encoding="utf-8"))

def io_to_str(o: aes.IO) -> str:
    return bytearray(o).decode("utf-8")


k = [int.from_bytes(urandom(4), "big") for _ in range(aes.Nb)]
plain = "z7E9PEB!h9xS5LfWbaq*$$EkKGFp9rze8Us@yBViBey4Ry"
ciphertext = aes.cipher(str_to_io(plain), k)
inv_ciphertext = aes.inv_cipher(ciphertext, k)

assert plain == io_to_str(inv_ciphertext) # Hurrah! It works


# Hex str <-> IO
def hex_str_to_io(s: str) -> aes.IO:
    return [int(s[2 * i : 2 * (i + 1)], 16) for i in range(len(s) // 2)]

def io_to_hex_str(a: aes.IO) -> str:
    return "".join([hex(x)[2:] for x in a])


key = aes.io_to_state(hex_str_to_io("2b7e151628aed2a6abf7158809cf4f3c"))
iv = aes.io_to_state(hex_str_to_io("000102030405060708090a0b0c0d0e0f"))
plain = "6bc1bee22e409f96e93d7e117393172a"

c = aes.encrypt_cbc(hex_str_to_io(plain), key, iv)
d = aes.decrypt_cbc(c, key, iv)

assert plain == io_to_hex_str(d)
