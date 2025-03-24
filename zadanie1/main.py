import random
import sympy

def liczbaPierwszaGen(bits=512):
    """Generuje dużą liczbę pierwszą przystającą do 3 modulo 4."""
    while True:
        p = sympy.randprime(2**(bits-1), 2**bits)
        if p % 4 == 3:
            return p

def startBBs():
    """Inicjalizuje generator BBS wybierając odpowiednie liczby p, q oraz x0."""
    p = liczbaPierwszaGen()
    q = liczbaPierwszaGen()
    N = p * q
    x0 = random.randint(2, N - 1)
    while sympy.gcd(x0, N) != 1:
        x0 = random.randint(2, N - 1)
    return N, x0

def BBsAlgorytm(N, x0, length=20000):
    """Generuje ciąg bitów o zadanej długości."""
    x = x0
    bits = []
    for _ in range(length):
        x = pow(x, 2, N)
        bits.append(x % 2)
    return bits

def testPojedynczychBitow(bits):
    """Testuje pojedyncze bity ciągu."""
    print("\nTest pojedynczych bitów:")
    ones = bits.count(1)
    print(f"Jedynek: {ones}")
    if 9725 <= ones <= 10275:
        print("Test zaliczony.")
    else:
        print("Test niezaliczony.")

def testDlugiejSerii(bits):
    """Testuje serii bitów ciągu."""
    print("\nTest serii:")
    ones = 0
    max_ones = 0
    for bit in bits:
        if bit == 1:
            ones += 1
            if ones > max_ones:
                max_ones = ones
        else:
            ones = 0
    print(f"Najdłuższa seria jedynek: {max_ones}")
    if max_ones <= 26:
        print("Test zaliczony.")
    else:
        print("Test niezaliczony.")

def testPoker(bits):
    """Testuje występowanie różnych kombinacji 4-bitowych."""
    print("\nTest pokera:")

    segmenty = [tuple(bits[i:i+4]) for i in range(0, len(bits), 4)]
    licznikSegmentow = {}
    for segment in segmenty:
        if segment in licznikSegmentow:
            licznikSegmentow[segment] += 1
        else:
            licznikSegmentow[segment] = 1

    x = 0
    for segment in licznikSegmentow:
        x += pow(licznikSegmentow[segment],2)

    x *= 16 / 5000
    x -= 5000
    print(f"Wartość x: {x}")
    if 2.16 < x < 46.17:
        print("Test zaliczony.\n")
    else:
        print("Test niezaliczony.\n")

    # print("\nRozkład segmentów:")
    # for segment in licznikSegmentow:
    #     print(f"{segment}: {licznikSegmentow[segment]}")

def testowanie(bits):
    """Stosuje testy na ciągu bitów."""
    testPojedynczychBitow(bits)
    testDlugiejSerii(bits)
    testPoker(bits)

N, x0 = startBBs()
bits = BBsAlgorytm(N, x0, 20000)

testowanie(bits)