import hashlib
import random
import timeit
import matplotlib.pyplot as plt
import os

def md5(tekst):
    return hashlib.md5(tekst).hexdigest()

def sha1(tekst):
    return hashlib.sha1(tekst).hexdigest()

def sha256(tekst):
    return hashlib.sha256(tekst).hexdigest()

def sha512(tekst):
    return hashlib.sha512(tekst).hexdigest()

def sha3(tekst):
    return hashlib.sha3_512(tekst).hexdigest()

def generujplik(nazwapliku, rozmiarmb):
    with open(nazwapliku, 'wb') as f:
        f.write(os.urandom(rozmiarmb * 1024 * 1024))

def czytajplik(nazwapliku):
    with open(nazwapliku, 'rb') as f:
        return f.read()

def policzkolizje(hashe):
    widziane = set()
    kolizje = 0
    for h in hashe:
        prefiks = h[:3]
        if prefiks in widziane:
            kolizje += 1
        else:
            widziane.add(prefiks)
    return kolizje

def sac_test(funkcjaskrotu, dane):
    oryginalny_hash = funkcjaskrotu(dane)
    oryginalne_bity = bin(int(oryginalny_hash, 16))[2:].zfill(len(oryginalny_hash)*4)  # Hex na bity
    zmienione_bity = 0
    for i in range(len(dane)):
        dane_zmienione = bytearray(dane)
        dane_zmienione[i] ^= 1  
        nowy_hash = funkcjaskrotu(bytes(dane_zmienione))
        nowe_bity = bin(int(nowy_hash, 16))[2:].zfill(len(nowy_hash)*4)
        zmienione_bity += sum(a != b for a, b in zip(oryginalne_bity, nowe_bity))
    return zmienione_bity / (len(dane) * len(oryginalne_bity))

skroty = [md5, sha1, sha256, sha512, sha3]
rozmiary = [1, 5, 10]
pliki = {}

for rozmiar in rozmiary:
    nazwapliku = f"plik_{rozmiar}MB.bin"
    generujplik(nazwapliku, rozmiar)
    pliki[rozmiar] = czytajplik(nazwapliku)

tabelaczasow = {rozmiar: [] for rozmiar in rozmiary}

for rozmiar in rozmiary:
    dane = pliki[rozmiar]
    for funkcjaskrotu in skroty:
        czasstart = timeit.default_timer()
        funkcjaskrotu(dane)
        czaswykonania = timeit.default_timer() - czasstart
        tabelaczasow[rozmiar].append((funkcjaskrotu.__name__, czaswykonania))


#Analiza kolizji
wybranaskrot = sha512 
haszewybrane = [wybranaskrot(pliki[1])[:3] for _ in range(1000)]
liczbakolizji = policzkolizje(haszewybrane)
print(f"Liczba kolizji na pierwszych 12 bitach dla {wybranaskrot.__name__}: {liczbakolizji}")


#Analiza SAC
dane_testowe = os.urandom(64)
sac_wynik = sac_test(wybranaskrot, dane_testowe)
print(f"Współczynnik SAC dla {wybranaskrot.__name__}: {sac_wynik:.4f}")

# Wykresy
plt.figure()
for rozmiar in rozmiary:
    plt.plot([h[0] for h in tabelaczasow[rozmiar]], [h[1] for h in tabelaczasow[rozmiar]], marker='o', label=f"{rozmiar}MB")

plt.xlabel("Funkcja skrótu")
plt.ylabel("Czas (sekundy)")
plt.title("Czas obliczania skrótu dla różnych rozmiarów plików")
plt.legend()
plt.show()