# Implemented according to FIPS 197 : https://csrc.nist.gov/csrc/media/publications/fips/197/final/documents/fips-197.pdf

# Type hints
Word = int # a 32-bit word
State = list[Word]
IO = list[int] # a list of bytes (int in [0,255])
MasterKey = list[int]
ExpandedKey = list[Word]

# Some constants
Nb = 4 # nb of columns of the state

# Nr as a function of Nk
N_ROUNDS = {
    4: 10,
    6: 12,
    8: 14
}

S_BOX = (
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8, 
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
)

INV_S_BOX = (
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
)

R_C = (0x01, 0x02,0x04, 0x08, 0x10,0x20, 0x40, 0x80, 0x1B, 0x36)
R_CON = [b << 24 for b in R_C]


# IO <-> state
def io_to_state(inp: IO) -> State:
    s = [word_from_bytes(inp[4 * c : 4 * (c + 1)]) for c in range(Nb)]
    return s

def state_to_io(s: State) -> IO:
    out = []
    for c in range(Nb):
        out.extend([ith_byte(s[c], i) for i in range(4)])
    return out

# Playing with 32-bit words, sometimes viewed as a list of 4 bytes
def ith_byte(a: Word, i: int):
    return (a >> 8 * (3 - i)) &0b11111111

def word_from_bytes(l: list[int]) -> Word:
    return l[0] * 256 ** 3 + l[1] * 256 ** 2 + l[2] * 256 + l[3]


# See section 4.2.1
def xtime(b: int) -> int:
    m = 0b100011011
    if b & 0b10000000:
        return (b << 1) ^ m
    return b << 1


# See section 5.1
def cipher_state(s: State, w: ExpandedKey, Nr: int):
    add_round_key(s, w[0 : Nb])

    for round in range(1, Nr):
        sub_bytes(s)
        shift_rows(s)
        mix_columns(s)
        add_round_key(s, w[round * Nb : (round + 1) * Nb])

    sub_bytes(s)
    shift_rows(s)
    add_round_key(s, w[Nr * Nb : (Nr + 1) * Nb])

def cipher(plain: IO, k: MasterKey) -> IO: 
    # PKCS#7 padding
    n_padding = 4 * Nb - len(plain) % (4 * Nb)
    assert n_padding < 256 # n_padding must be coded on a single byte
    plain.extend([n_padding] * n_padding)

    Nk = len(k) 
    Nr = N_ROUNDS[Nk]
    w = key_expansion(len(k), k)
    states = []
    for i in range(len(plain) // (4 * Nb)):
        states.append(io_to_state(plain[4 * Nb * i : 4 * Nb * (i + 1)]))
    
    for s in states:
        cipher_state(s, w, Nr)

    ciphertext = [b for s in states for b in state_to_io(s)]
    return ciphertext


# See section 5.1.1
def sub_word(a: Word) -> Word:
    l = [ith_byte(a, i) for i in range(4)]
    l = [S_BOX[b] for b in l]
    return word_from_bytes(l)

def sub_bytes(s: State):
    for c in range(Nb):
        s[c] = sub_word(s[c])


# See section 5.1.2
def shift_rows(s: State):
    s_ = list(s) # buffer to do in place modifications to s
    for c in range(Nb):
        l = [ith_byte(s_[(c + i) % Nb], i) for i in range(4)]
        s[c] = word_from_bytes(l)


# See section 5.1.3
def mix_columns(s: State):
    for c in range(Nb):
        l = [ith_byte(s[c], i) for i in range(4)]
        a = l[0] ^ l[1] ^ l[2] ^ l[3]
        l_ = [a ^ l[i] ^ xtime(l[i] ^ l[(i + 1) % 4]) for i in range(4)]
        s[c] = word_from_bytes(l_)


# See section 5.1.4
def add_round_key(s: State, w: ExpandedKey):
    for c in range(Nb):
        s[c] ^= w[c]


# See section 5.2
def rot_word(a: Word) -> Word:
    temp = a >> 24
    return (a << 8 | temp) & 0xffffffff # equivalent to (...) % 256 ** 4 

def key_expansion(Nk: int, k: MasterKey) -> ExpandedKey:
    assert len(k) == Nk
    assert Nk in N_ROUNDS
    
    Nr = N_ROUNDS[Nk]

    w = list(k)

    for i in range(Nk, Nb * (Nr + 1)):
        temp = w[-1]
        if i % Nk == 0:
            temp = sub_word(rot_word(temp)) ^ R_CON[i // Nk - 1]
        elif Nk > 6 and i % Nk == 4:
            temp = sub_word(temp)
        w.append(w[i - Nk] ^ temp)
    return w


# See section 5.3
def inv_cipher_state(s: State, w: ExpandedKey, Nr: int):
    add_round_key(s, w[Nr * Nb : (Nr + 1) * Nb])

    for round in range(Nr - 1, 0, -1):
        inv_shift_rows(s)
        inv_sub_bytes(s)
        add_round_key(s, w[round * Nb : (round + 1) * Nb])
        inv_mix_columns(s)
    
    inv_sub_bytes(s)
    inv_shift_rows(s)
    add_round_key(s, w[0 : Nb])

def inv_cipher(ciphertext: IO, k: MasterKey) -> IO:
    assert len(ciphertext) % (4 * Nb) == 0

    Nk = len(k) 
    Nr = N_ROUNDS[Nk]
    w = key_expansion(len(k), k)
    states = []
    for i in range(len(ciphertext) // (4 * Nb)):
        states.append(io_to_state(ciphertext[4 * Nb * i : 4 * Nb * (i + 1)]))
    
    for s in states:
        inv_cipher_state(s, w, Nr)

    plain = [b for s in states for b in state_to_io(s)]
    # PKCS#7 unpadding
    n = plain[-1]
    for _ in range(n):
        plain.pop()
    return plain


# See section 5.3.1
def inv_shift_rows(s: State):
    s_ = list(s) # buffer to do in place modifications to s
    for c in range(Nb):
        l = [ith_byte(s_[(c - i) % Nb], i) for i in range(4)]
        s[c] = word_from_bytes(l)


# See section 5.3.2 
def inv_sub_word(a: Word) -> Word:
    l = [ith_byte(a, i) for i in range(4)]
    l = [INV_S_BOX[b] for b in l]
    return word_from_bytes(l)

def inv_sub_bytes(s: State):
    for c in range(Nb):
        s[c] = inv_sub_word(s[c])


# See section 5.3.3
def inv_mix_columns(s: State):
    for c in range(Nb):
        l = [ith_byte(s[c], i) for i in range(4)]
        time_9 = lambda b: b ^ xtime(xtime(xtime(b))) #0x09 = 1 + 8
        time_b = lambda b: b ^ xtime(b) ^ xtime(xtime(xtime(b))) # 0x0b = 1 + 2 + 8
        time_d = lambda b: b ^ xtime(xtime(b)) ^ xtime(xtime(xtime(b))) # 0x0d = 1 + 4 + 8
        time_e = lambda b: xtime(b) ^ xtime(xtime(b)) ^ xtime(xtime(xtime(b))) #0x0e = 2 + 4 + 8
        l = [
            time_e(l[0]) ^ time_b(l[1]) ^ time_d(l[2]) ^ time_9(l[3]),
            time_9(l[0]) ^ time_e(l[1]) ^ time_b(l[2]) ^ time_d(l[3]),
            time_d(l[0]) ^ time_9(l[1]) ^ time_e(l[2]) ^ time_b(l[3]),
            time_b(l[0]) ^ time_d(l[1]) ^ time_9(l[2]) ^ time_e(l[3])
        ]
        s[c] = word_from_bytes(l)



def xor_state(s: State, t: State) -> State:
    return [x ^ y for (x, y) in zip(s, t)]


# CBC implementation according to https://doi.org/10.6028/NIST.SP.800-38A
# See section 6.2
def encrypt_cbc(plain: IO, k: MasterKey, IV: State) -> IO:
    # PKCS#7 padding
    n_padding = 4 * Nb - len(plain) % (4 * Nb)
    assert n_padding < 256 # n_padding must be coded on a single byte
    plain.extend([n_padding] * n_padding)

    Nk = len(k) 
    Nr = N_ROUNDS[Nk]
    w = key_expansion(len(k), k)
    states = []
    for i in range(len(plain) // (4 * Nb)):
        states.append(io_to_state(plain[4 * Nb * i : 4 * Nb * (i + 1)]))
    
    for (i, s) in enumerate(states):
        states[i] = xor_state(s, IV) if i == 0 else xor_state(s, states[i - 1])
        cipher_state(states[i] , w, Nr)

    ciphertext = [b for s in states for b in state_to_io(s)]
    return ciphertext


def decrypt_cbc(ciphertext: IO, k: MasterKey, IV: State) -> IO:
    assert len(ciphertext) % (4 * Nb) == 0

    Nk = len(k) 
    Nr = N_ROUNDS[Nk]
    w = key_expansion(len(k), k)
    states = []
    for i in range(len(ciphertext) // (4 * Nb)):
        states.append(io_to_state(ciphertext[4 * Nb * i : 4 * Nb * (i + 1)]))
    
    previous_cipher_block = IV
    for (i, s) in enumerate(states):
        current_cipher_block = list(s)
        inv_cipher_state(s, w, Nr)
        states[i] = xor_state(s, previous_cipher_block)
        previous_cipher_block = current_cipher_block

    plain = [b for s in states for b in state_to_io(s)]
    # PKCS#7 unpadding
    n = plain[-1]
    for _ in range(n):
        plain.pop()
    return plain
