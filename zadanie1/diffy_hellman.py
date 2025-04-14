import random
import sympy

def diffie_hellman(p, g):
    """Funkcja implementująca algorytm Diffiego-Hellmana. """
    
    # Strona A wybiera tajny klucz x (1 < x < p-1)
    x = random.randint(2, p-2)
    # Obliczenie publicznej wartości X = g^x mod p
    X = pow(g, x, p)
    
    # Strona B wybiera tajny klucz y (1 < y < p-1)
    y = random.randint(2, p-2)
    # Obliczenie publicznej wartości Y = g^y mod p
    Y = pow(g, y, p)
    
    # Wymiana wartości publicznych: A otrzymuje Y, B otrzymuje X
    
    # Strona A oblicza wspólny klucz k = Y^x mod p
    k_A = pow(Y, x, p)
    # Strona B oblicza wspólny klucz k = X^y mod p
    k_B = pow(X, y, p)
    
    return {
        'tajny_A': x,
        'publiczny_A': X,
        'tajny_B': y,
        'publiczny_B': Y,
        'klucz_sesji_A': k_A,
        'klucz_sesji_B': k_B
    }

p = sympy.randprime(2**(253), 2**254)  # Generowanie liczby pierwszej p
g = sympy.primitive_root(p) # Generowanie pierwiastka pierwotnego g dla p

wynik = diffie_hellman(p, g)

print("Strona A:")
print("  Tajny klucz (x):", wynik['tajny_A'])
print("  Wartość publiczna (X):", wynik['publiczny_A'])

print("\nStrona B:")
print("  Tajny klucz (y):", wynik['tajny_B'])
print("  Wartość publiczna (Y):", wynik['publiczny_B'])

print("\nWspólny klucz sesji:")
print("  Obliczony przez A:", wynik['klucz_sesji_A'])
print("  Obliczony przez B:", wynik['klucz_sesji_B'])

# Sprawdzenie, czy obliczony klucz sesji jest taki sam
if wynik['klucz_sesji_A'] == wynik['klucz_sesji_B']:
    print("\nObie strony uzyskały ten sam klucz sesji!")
else:
    print("\nBłąd w uzyskiwaniu wspólnego klucza sesji!")
