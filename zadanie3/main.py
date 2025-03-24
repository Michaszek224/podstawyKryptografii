import hashlib
import random
import timeit
import matplotlib.pyplot as plt

def md5(tekst):
    return hashlib.md5(tekst.encode()).hexdigest()

def sha1(tekst):
    return hashlib.sha1(tekst.encode()).hexdigest()

def sha256(tekst):
    return hashlib.sha256(tekst.encode()).hexdigest()

def sha512(tekst):
    return hashlib.sha512(tekst.encode()).hexdigest()

def sha3(tekst):
    return hashlib.sha3_512(tekst.encode()).hexdigest()

def losowaWiadomosc(n):
    randomNumber = random.randint(1, n)
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=randomNumber))

def policz_kolizje(hashe):
    widziane = set()
    kolizje = 0
    for h in hashe:
        prefiks = h[:3]
        if prefiks in widziane:
            kolizje += 1
        else:
            widziane.add(prefiks)
    return kolizje

n = 1_000
teksty = []
for i in range(n):
    teksty.append(losowaWiadomosc(100))

skroty = [md5, sha1, sha256, sha512, sha3]

skrotyWygenerowane = []
sredniCzas = []

#liczenei czasu generowania skrotow

for skrot in skroty:
    tymczasowe = []
    timeStart = timeit.default_timer()
    for i in range(n):
        tymczasowe.append(skrot(teksty[i]))
    skrotyWygenerowane.append(tymczasowe)
    sredniCzas.append([skrot.__name__ ,(timeit.default_timer() - timeStart) / n])

#zmienic na 3 rozne rodzaje plikow 1mb, 5mb, 10mb to powyzej

#Badanie kolizji

wybrany_skrot = md5
wybrane_skróty = [wybrany_skrot(tekst) for tekst in teksty]
liczba_kolizji = policz_kolizje(wybrane_skróty)

print(f"Liczba kolizji na pierwszych 12 bitach dla {wybrany_skrot.__name__}: {liczba_kolizji}")



# print(sredniCzas)
plt.bar([skrot.__name__ for skrot in skroty], [czas[1] for czas in sredniCzas])
plt.show()