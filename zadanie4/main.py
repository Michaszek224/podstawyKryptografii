from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import time
import os
import matplotlib.pyplot as plt


# Stałe
rozmiarBloku = 16  # Rozmiar bloku AES w bajtach
rozmiarKlucza = 16  # Rozmiar klucza AES w bajtach

def zmierzCzasSzyfrowaniaIDeszyfrowania(tryb, sciezkaPliku, klucz, iv=None):
    with open(sciezkaPliku, 'rb') as f:
        tekstJawny = f.read()

    szyfr = AES.new(klucz, tryb, iv) if iv else AES.new(klucz, tryb)
    czasStart = time.time()
    if tryb == AES.MODE_CTR:
        tekstSzyfrowany = szyfr.encrypt(tekstJawny)
    elif tryb in [AES.MODE_CBC, AES.MODE_ECB, AES.MODE_CFB, AES.MODE_OFB]:
        tekstSzyfrowany = szyfr.encrypt(pad(tekstJawny, rozmiarBloku))
    czasSzyfrowania = time.time() - czasStart
    if tryb == AES.MODE_CTR:
        szyfrDeszyfrujacy = AES.new(klucz, tryb, nonce=szyfr.nonce)
    else:
        szyfrDeszyfrujacy = AES.new(klucz, tryb, iv) if iv else AES.new(klucz, tryb)
    czasStart = time.time()
    if tryb == AES.MODE_CTR:
        tekstDeszyfrowany = szyfrDeszyfrujacy.decrypt(tekstSzyfrowany)
    elif tryb in [AES.MODE_CBC, AES.MODE_ECB, AES.MODE_CFB, AES.MODE_OFB]:
        tekstDeszyfrowany = unpad(szyfrDeszyfrujacy.decrypt(tekstSzyfrowany), rozmiarBloku)
    czasDeszyfrowania = time.time() - czasStart

    assert tekstJawny == tekstDeszyfrowany, "Deszyfrowanie nie powiodło się!"
    return czasSzyfrowania, czasDeszyfrowania

def analizujTryby(rozmiaryPlikow):
    klucz = get_random_bytes(rozmiarKlucza)
    iv = get_random_bytes(rozmiarBloku)

    tryby = {
        "ECB": AES.MODE_ECB,
        "CBC": AES.MODE_CBC,
        "OFB": AES.MODE_OFB,
        "CFB": AES.MODE_CFB,
        "CTR": AES.MODE_CTR
    }

    wyniki = {}
    for rozmiar in rozmiaryPlikow:
        sciezkaPliku = f"plik_testowy_{rozmiar}.bin"
        with open(sciezkaPliku, 'wb') as f:
            f.write(os.urandom(rozmiar))

        wyniki[rozmiar] = {}
        for nazwaTrybu, tryb in tryby.items():
            if nazwaTrybu in ["CBC", "OFB", "CFB"]:
                czasSzyfrowania, czasDeszyfrowania = zmierzCzasSzyfrowaniaIDeszyfrowania(tryb, sciezkaPliku, klucz, iv)
            elif nazwaTrybu == "CTR":
                czasSzyfrowania, czasDeszyfrowania = zmierzCzasSzyfrowaniaIDeszyfrowania(tryb, sciezkaPliku, klucz, iv=None)
            else:
                czasSzyfrowania, czasDeszyfrowania = zmierzCzasSzyfrowaniaIDeszyfrowania(tryb, sciezkaPliku, klucz)

            wyniki[rozmiar][nazwaTrybu] = (czasSzyfrowania, czasDeszyfrowania)

        os.remove(sciezkaPliku)

    return wyniki

def zaimplementujCbcUzywajacEcb(tekstJawny, klucz, iv):
    szyfrEcb = AES.new(klucz, AES.MODE_ECB)
    tekstSzyfrowany = b""
    poprzedniBlok = iv

    for i in range(0, len(tekstJawny), rozmiarBloku):
        blok = tekstJawny[i:i + rozmiarBloku]
        if len(blok) < rozmiarBloku:
            blok = pad(blok, rozmiarBloku)
        blokXor = bytes([_a ^ _b for _a, _b in zip(blok, poprzedniBlok)])
        zaszyfrowanyBlok = szyfrEcb.encrypt(blokXor)
        tekstSzyfrowany += zaszyfrowanyBlok
        poprzedniBlok = zaszyfrowanyBlok

    return tekstSzyfrowany

def deszyfrujCbcUzywajacEcb(tekstSzyfrowany, klucz, iv):
    szyfrEcb = AES.new(klucz, AES.MODE_ECB)
    tekstJawny = b""
    poprzedniBlok = iv

    for i in range(0, len(tekstSzyfrowany), rozmiarBloku):
        blok = tekstSzyfrowany[i:i + rozmiarBloku]
        odszyfrowanyBlok = szyfrEcb.decrypt(blok)
        blokXor = bytes([_a ^ _b for _a, _b in zip(odszyfrowanyBlok, poprzedniBlok)])
        tekstJawny += blokXor
        poprzedniBlok = blok

    return unpad(tekstJawny, rozmiarBloku)

def analizujPropagacjeBledow(tryb, tekstJawny, klucz, iv=None):
    # Szyfrowanie
    szyfr = AES.new(klucz, tryb, iv) if iv else AES.new(klucz, tryb)
    if tryb == AES.MODE_CTR:
        tekstSzyfrowany = szyfr.encrypt(tekstJawny)
        nonce = szyfr.nonce
    else:
        tekstSzyfrowany = szyfr.encrypt(pad(tekstJawny, rozmiarBloku))

    # Wprowadzenie błędu w szyfrogramie (zmiana jednego bajtu)
    tekstSzyfrowanyZBledem = bytearray(tekstSzyfrowany)
    tekstSzyfrowanyZBledem[len(tekstSzyfrowanyZBledem) // 2] ^= 0xFF  # Odwrócenie bitów w środku szyfrogramu

    # Deszyfrowanie
    if tryb == AES.MODE_CTR:
        szyfrDeszyfrujacy = AES.new(klucz, tryb, nonce=nonce)
        try:
            tekstDeszyfrowany = szyfrDeszyfrujacy.decrypt(tekstSzyfrowanyZBledem)
        except Exception as e:
            tekstDeszyfrowany = f"Błąd deszyfrowania: {e}"
    else:
        szyfrDeszyfrujacy = AES.new(klucz, tryb, iv) if iv else AES.new(klucz, tryb)
        try:
            tekstDeszyfrowany = unpad(szyfrDeszyfrujacy.decrypt(tekstSzyfrowanyZBledem), rozmiarBloku)
        except Exception as e:
            tekstDeszyfrowany = f"Błąd deszyfrowania: {e}"

    return tekstSzyfrowany, tekstSzyfrowanyZBledem, tekstDeszyfrowany


if __name__ == "__main__":
    
    # Generowanie plików testowych
    rozmiaryPlikow = [102400, 1024000, 10240000]
    for rozmiar in rozmiaryPlikow:
        sciezkaPliku = f"plik_testowy_{rozmiar}.bin"
        with open(sciezkaPliku, 'wb') as f:
            f.write(os.urandom(rozmiar))
    print("Pliki testowe wygenerowane pomyślnie.")
    
    # Zadanie 1
    wyniki = analizujTryby(rozmiaryPlikow)
    for rozmiar, wynikiTrybow in wyniki.items():
        print(f"Rozmiar pliku: {rozmiar} bajtów")
        for tryb, czasy in wynikiTrybow.items():
            print(f"  Tryb: {tryb}, Czas szyfrowania: {czasy[0]:.6f}s, Czas deszyfrowania: {czasy[1]:.6f}s")

    # Zadanie 2
    klucz = get_random_bytes(rozmiarKlucza)
    iv = get_random_bytes(rozmiarBloku)
    tekstJawny = b"To jest testowa wiadomosc dla analizy propagacji bledow."
    tekstJawny = pad(tekstJawny, rozmiarBloku)

    tryby = {
        "ECB": AES.MODE_ECB,
        "CBC": AES.MODE_CBC,
        "OFB": AES.MODE_OFB,
        "CFB": AES.MODE_CFB,
        "CTR": AES.MODE_CTR
    }

    print("\nAnaliza propagacji błędów:")
    for nazwaTrybu, tryb in tryby.items():
        print(f"\nTryb: {nazwaTrybu}")
        if nazwaTrybu in ["CBC", "OFB", "CFB"]:
            _, tekstSzyfrowanyZBledem, tekstDeszyfrowany = analizujPropagacjeBledow(tryb, tekstJawny, klucz, iv)
        elif nazwaTrybu == "CTR":
            _, tekstSzyfrowanyZBledem, tekstDeszyfrowany = analizujPropagacjeBledow(tryb, tekstJawny, klucz, iv=None)
        else:
            _, tekstSzyfrowanyZBledem, tekstDeszyfrowany = analizujPropagacjeBledow(tryb, tekstJawny, klucz)

        print(f"  Szyfrogram z błędem: {tekstSzyfrowanyZBledem}")
        print(f"  Wynik deszyfrowania: {tekstDeszyfrowany}")

    # Zadanie 3
    klucz = get_random_bytes(rozmiarKlucza)
    iv = get_random_bytes(rozmiarBloku)
    tekstJawny = b"To jest testowa wiadomosc dla implementacji trybu CBC."
    tekstJawny = pad(tekstJawny, rozmiarBloku)

    tekstSzyfrowany = zaimplementujCbcUzywajacEcb(tekstJawny, klucz, iv)
    odszyfrowanyTekst = deszyfrujCbcUzywajacEcb(tekstSzyfrowany, klucz, iv)

    assert unpad(tekstJawny, rozmiarBloku) == odszyfrowanyTekst, "Implementacja CBC nie powiodła się!"
    print("Implementacja CBC przy użyciu trybu ECB zakończona sukcesem.")
    

    #Wizualizacja wyników
    tryby = ["ECB", "CBC", "OFB", "CFB", "CTR"]

    czasySzyfrowania = {tryb: [] for tryb in tryby}
    czasyDeszyfrowania = {tryb: [] for tryb in tryby}

    for rozmiar in rozmiaryPlikow:
        for tryb in tryby:
            czasySzyfrowania[tryb].append(wyniki[rozmiar][tryb][0])
            czasyDeszyfrowania[tryb].append(wyniki[rozmiar][tryb][1])

    # Wykres czasów szyfrowania
    plt.figure(figsize=(10, 5))
    for tryb in tryby:
        plt.plot(rozmiaryPlikow, czasySzyfrowania[tryb], label=f"{tryb} Szyfrowanie")
    plt.xlabel("Rozmiar pliku (bajty)")
    plt.ylabel("Czas (sekundy)")
    plt.title("Czasy szyfrowania dla różnych trybów")
    plt.legend()
    plt.grid()
    plt.xscale("log")
    plt.show()

    # Wykres czasów deszyfrowania
    plt.figure(figsize=(10, 5))
    for tryb in tryby:
        plt.plot(rozmiaryPlikow, czasyDeszyfrowania[tryb], label=f"{tryb} Deszyfrowanie")
    plt.xlabel("Rozmiar pliku (bajty)")
    plt.ylabel("Czas (sekundy)")
    plt.title("Czasy deszyfrowania dla różnych trybów")
    plt.legend()
    plt.grid()
    plt.xscale("log")
    plt.show()