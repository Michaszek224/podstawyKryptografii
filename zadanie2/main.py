import random
import sympy

def liczbaPierwszaGen(bits=16):
    """Generuje czterocyfrową liczbę pierwszą """
    p = sympy.randprime(1000, 9999)
    q = sympy.randprime(1000, 9999)
    while q == p:
        q = sympy.randprime(1000, 9999)
    return p, q

def generowanieKlucza(p, q):
    """Generuje klucz publiczny i prywatny"""
    N = p * q
    phi = (p - 1) * (q - 1)
    e = sympy.randprime(2, phi - 1)
    while sympy.gcd(e, phi) != 1:
        e = sympy.randprime(2, phi - 1)
    d = sympy.mod_inverse(e, phi)
    return (e, N), (d, N)

def generowanieWiadomosci(dlugosc=50):
    """Generuje wiadomość złożoną z losowych znaków"""
    wiadomosc = []
    for _ in range(dlugosc):
        wiadomosc.append(chr(random.randint(97, 122)))
    return wiadomosc

def zamianaNaLiczbe(wiadomosc):
    """Zamienia wiadomość na liczbę"""
    for i in range(len(wiadomosc)):
        wiadomosc[i] = ord(wiadomosc[i])
    return wiadomosc

def zamianaNaZnaki(liczba):
    """Zamienia liczbę na znaki"""
    for i in range(len(liczba)):
        liczba[i] = chr(liczba[i])
    return liczba

def szyfrowanie(wiadomosc, klucz):
    """Szyfruje wiadomość za pomocą klucza publicznego"""
    wiadomosc = zamianaNaLiczbe(wiadomosc)
    e, N = klucz
    for i in range(len(wiadomosc)):
        wiadomosc[i] = pow(wiadomosc[i], e, N)
    return wiadomosc

def deszyfrowanie(zaszyfrowana, klucz):
    """Deszyfruje wiadomość za pomocą klucza prywatnego"""
    d, N = klucz
    for i in range(len(zaszyfrowana)):
        zaszyfrowana[i] = pow(zaszyfrowana[i], d, N)
    zaszyfrowana = zamianaNaZnaki(zaszyfrowana)
    return zaszyfrowana

def test(wiadomosc1, wiadomosc2):
    """Sprawdza czy wiadomości są identyczne"""
    if wiadomosc1 == wiadomosc2:
        print("Wiadomości są identyczne.")
    else:
        print("Wiadomości nie są identyczne.")

p, q = liczbaPierwszaGen()
public, private = generowanieKlucza(p, q)

wiadomosc = generowanieWiadomosci()
zaszyfrowana = szyfrowanie(wiadomosc, public)
odszyfrowana = deszyfrowanie(zaszyfrowana, private)

test(wiadomosc, odszyfrowana)