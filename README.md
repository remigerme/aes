# Advanced Encryption Standard (AES)

A simple AES python implementation, because I was wondering how it works.

I followed the specification given in FIPS-197 (available over [here](https://csrc.nist.gov/csrc/media/publications/fips/197/final/documents/fips-197.pdf)]) and read some Wikipedia articles.

This project was made for educational purposes, **do not use for real cryptographic use**.


## About the types used

I chose to represent a state by a list of `Nb` (`Nb = 4`) 32-bit words, which simply are integers.

The input and output are a list of bytes (integers < 256).
