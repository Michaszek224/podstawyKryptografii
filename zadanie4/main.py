from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import time
import os
import matplotlib.pyplot as plt

# Stałe
ROZMIAR_BLOKU = 16  # Rozmiar bloku AES w bajtach
ROZMIAR_KLUCZA = 16  # Rozmiar klucza AES w bajtach

def zmierz_czas_szyfrowania_i_deszyfrowania(tryb, sciezka_pliku, klucz, iv=None):
    with open(sciezka_pliku, 'rb') as f:
        original_tekst = f.read()  # Zachowaj oryginalne dane bez paddingu

    tekst_jawny = original_tekst
    nonce = None

    # Inicjalizacja szyfru
    if tryb == AES.MODE_CTR:
        nonce = get_random_bytes(8)
        szyfr = AES.new(klucz, tryb, nonce=nonce)
    else:
        szyfr = AES.new(klucz, tryb, iv=iv) if iv else AES.new(klucz, tryb)

    # Szyfrowanie (tylko dla trybów blokowych z paddingiem)
    start = time.time()
    if tryb in [AES.MODE_ECB, AES.MODE_CBC]:
        tekst_jawny = pad(original_tekst, ROZMIAR_BLOKU)
    tekst_szyfrowany = szyfr.encrypt(tekst_jawny)
    czas_szyfrowania = time.time() - start

    # Deszyfrowanie
    if tryb == AES.MODE_CTR:
        szyfr_deszyf = AES.new(klucz, tryb, nonce=nonce)
    else:
        szyfr_deszyf = AES.new(klucz, tryb, iv=iv) if iv else AES.new(klucz, tryb)
    
    start = time.time()
    tekst_deszyfrowany = szyfr_deszyf.decrypt(tekst_szyfrowany)
    
    # Usuwanie paddingu tylko dla trybów blokowych
    if tryb in [AES.MODE_ECB, AES.MODE_CBC]:
        tekst_deszyfrowany = unpad(tekst_deszyfrowany, ROZMIAR_BLOKU)
    czas_deszyfrowania = time.time() - start

    # Porównaj z oryginalnym tekstem (bez paddingu)
    assert original_tekst == tekst_deszyfrowany, "Błąd deszyfrowania!"
    return czas_szyfrowania, czas_deszyfrowania

def analizuj_tryby(rozmiary_plikow):
    klucz = get_random_bytes(ROZMIAR_KLUCZA)
    iv = get_random_bytes(ROZMIAR_BLOKU)  # Tylko dla trybów wymagających IV

    tryby = {
        "ECB": AES.MODE_ECB,
        "CBC": AES.MODE_CBC,
        "OFB": AES.MODE_OFB,
        "CFB": AES.MODE_CFB,
        "CTR": AES.MODE_CTR
    }

    wyniki = {}
    for rozmiar in rozmiary_plikow:
        sciezka = f"test_{rozmiar}.bin"
        with open(sciezka, 'wb') as f:
            f.write(os.urandom(rozmiar))

        wyniki[rozmiar] = {}
        for nazwa, tryb in tryby.items():
            iv_param = iv if tryb in [AES.MODE_CBC, AES.MODE_OFB, AES.MODE_CFB] else None
            czasy = zmierz_czas_szyfrowania_i_deszyfrowania(tryb, sciezka, klucz, iv_param)
            wyniki[rozmiar][nazwa] = czasy
        os.remove(sciezka)

    return wyniki

def zaimplementujCbcUzywajacEcb(tekstJawny, klucz, iv):
    szyfrEcb = AES.new(klucz, AES.MODE_ECB)
    tekstSzyfrowany = b""
    poprzedniBlok = iv

    for i in range(0, len(tekstJawny), ROZMIAR_BLOKU):
        blok = tekstJawny[i:i + ROZMIAR_BLOKU]
        if len(blok) < ROZMIAR_BLOKU:
            blok = pad(blok, ROZMIAR_BLOKU)
        blokXor = bytes([_a ^ _b for _a, _b in zip(blok, poprzedniBlok)])
        zaszyfrowanyBlok = szyfrEcb.encrypt(blokXor)
        tekstSzyfrowany += zaszyfrowanyBlok
        poprzedniBlok = zaszyfrowanyBlok

    return tekstSzyfrowany

def deszyfrujCbcUzywajacEcb(tekstSzyfrowany, klucz, iv):
    szyfrEcb = AES.new(klucz, AES.MODE_ECB)
    tekstJawny = b""
    poprzedniBlok = iv

    for i in range(0, len(tekstSzyfrowany), ROZMIAR_BLOKU):
        blok = tekstSzyfrowany[i:i + ROZMIAR_BLOKU]
        odszyfrowanyBlok = szyfrEcb.decrypt(blok)
        blokXor = bytes([_a ^ _b for _a, _b in zip(odszyfrowanyBlok, poprzedniBlok)])
        tekstJawny += blokXor
        poprzedniBlok = blok

    return unpad(tekstJawny, ROZMIAR_BLOKU)

def analizujPropagacjeBledow(tryb, tekstJawny, klucz, iv=None):
    # Szyfrowanie
    szyfr = AES.new(klucz, tryb, iv) if iv else AES.new(klucz, tryb)
    if tryb == AES.MODE_CTR:
        tekstSzyfrowany = szyfr.encrypt(tekstJawny)
        nonce = szyfr.nonce
    else:
        tekstSzyfrowany = szyfr.encrypt(pad(tekstJawny, ROZMIAR_BLOKU))

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
            tekstDeszyfrowany = unpad(szyfrDeszyfrujacy.decrypt(tekstSzyfrowanyZBledem), ROZMIAR_BLOKU)
        except Exception as e:
            tekstDeszyfrowany = f"Błąd deszyfrowania: {e}"

    return tekstSzyfrowany, tekstSzyfrowanyZBledem, tekstDeszyfrowany


if __name__ == "__main__":
    ROZMIARY_PLIKOW = [1024 * 100, 1024 * 1000, 1024 * 10000]
    wyniki = analizuj_tryby(ROZMIARY_PLIKOW)
    
    # Generowanie plików testowych
    for rozmiar in ROZMIARY_PLIKOW:
        sciezkaPliku = f"plik_testowy_{rozmiar}.bin"
        with open(sciezkaPliku, 'wb') as f:
            f.write(os.urandom(rozmiar))
    print("Pliki testowe wygenerowane pomyślnie.")
    
    # Zadanie 1
    wyniki = analizuj_tryby(ROZMIARY_PLIKOW)
    for rozmiar, wynikiTrybow in wyniki.items():
        print(f"Rozmiar pliku: {rozmiar} bajtów")
        for tryb, czasy in wynikiTrybow.items():
            print(f"  Tryb: {tryb}, Czas szyfrowania: {czasy[0]:.6f}s, Czas deszyfrowania: {czasy[1]:.6f}s")

    # Zadanie 2
    klucz = get_random_bytes(ROZMIAR_KLUCZA)
    iv = get_random_bytes(ROZMIAR_BLOKU)
    tekstJawny = b"To jest testowa wiadomosc dla analizy propagacji bledow."
    tekstJawny = pad(tekstJawny, ROZMIAR_BLOKU)

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
    klucz = get_random_bytes(ROZMIAR_KLUCZA)
    iv = get_random_bytes(ROZMIAR_BLOKU)
    tekstJawny = b"To jest testowa wiadomosc dla implementacji trybu CBC."
    tekstJawny = pad(tekstJawny, ROZMIAR_BLOKU)

    tekstSzyfrowany = zaimplementujCbcUzywajacEcb(tekstJawny, klucz, iv)
    odszyfrowanyTekst = deszyfrujCbcUzywajacEcb(tekstSzyfrowany, klucz, iv)

    assert unpad(tekstJawny, ROZMIAR_BLOKU) == odszyfrowanyTekst, "Implementacja CBC nie powiodła się!"
    print("Implementacja CBC przy użyciu trybu ECB zakończona sukcesem.")
    

    #Wizualizacja wyników
    tryby = ["ECB", "CBC", "CTR"]

    czasySzyfrowania = {tryb: [] for tryb in tryby}
    czasyDeszyfrowania = {tryb: [] for tryb in tryby}

    for rozmiar in ROZMIARY_PLIKOW:
        for tryb in tryby:
            czasySzyfrowania[tryb].append(wyniki[rozmiar][tryb][0])
            czasyDeszyfrowania[tryb].append(wyniki[rozmiar][tryb][1])

    # Wykres czasów szyfrowania
    plt.figure(figsize=(10, 5))
    for tryb in tryby:
        plt.plot(ROZMIARY_PLIKOW, czasySzyfrowania[tryb], label=f"{tryb} Szyfrowanie")
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
        plt.plot(ROZMIARY_PLIKOW, czasyDeszyfrowania[tryb], label=f"{tryb} Deszyfrowanie")
    plt.xlabel("Rozmiar pliku (bajty)")
    plt.ylabel("Czas (sekundy)")
    plt.title("Czasy deszyfrowania dla różnych trybów")
    plt.legend()
    plt.grid()
    plt.xscale("log")
    plt.show()