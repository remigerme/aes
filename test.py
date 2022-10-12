from os import urandom
from aes import IO, Nb, cipher, inv_cipher

# IO <-> str
def str_to_io(s: str) -> IO:
    return list(bytearray(s, encoding="utf-8"))

def io_to_str(o: IO) -> str:
    return bytearray(o).decode("utf-8")


k = [int.from_bytes(urandom(4), "big") for _ in range(Nb)]
plain = "z7E9PEB!h9xS5LfWbaq*$$EkKGFp9rze8Us@yBViBey4Ry"
ciphertext = cipher(str_to_io(plain), k)
inv_ciphertext = inv_cipher(ciphertext, k)

assert plain == io_to_str(inv_ciphertext) # Hurrah! It works
