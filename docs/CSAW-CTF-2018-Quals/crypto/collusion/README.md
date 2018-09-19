
# Details
A while ago I found a construction of collusion-secure, identity-based encryption built solely from RSA. A small group of cryptographers were confident enough in it to write a paper and publish it. But at the same time, the cryptanalysis is constant-time and can be done with undergrad-level number theory. This makes it an attractive CTF problem, in my mind. The system is as follows:

KeyGen():
    Generate two safe primes p, q for an RSA modulus N=pq. Set Phi(N) = (p-1)(q-1).
    Choose x, a random even integer greater than zero and less than Phi(N).
    Choose g, a generator of Z/NZ.
    Return:
        Master public key = { N, g, g^x (mod N) }
        Master private key = { p, q, x }.

IssueKey(Master private key, Decrypter name):
    With a public hash function, compute n (an odd integer greater than zero and less than N) as the hash of the decrypter's name.
    Return:
        Decrypter private key = { 1/(x+n) (mod Phi(N)) }.

Encrypt(Master public key, Decrypter name, Message):
    With the same method as IssueKey, compute n as the hash of the decrypter's name.
    Choose r, a random integer greater than zero and less than N.
    Compute K = g^r (mod N) and A = (g^x * g^n)^r.
    Compute C = Encrypt_K(Message)
    Return:
        Ciphertext = { A, C }.

Decrypt(Decrypter private key, Ciphertext):
    Compute K = A^(1/(x+n)) (mod N).
    Return:
        Decrypt_K(C).

We give somebody the master public key, a ciphertext encrypted to A, and decrypter keys for B, C. The challenge is to decrypt the message to A.
