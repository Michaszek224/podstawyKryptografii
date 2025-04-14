import numpy as np
import matplotlib.pyplot as plt
import random

wymiary = 100

def generowanieDwojki():
    """Generuje losowa liczbe od 0 do 1"""
    x1, x2 = random.randint(0,1), random.randint(0,1)
    return x1, x2


def shamirWizualny(orygialny):
    """"Funkcja implementująca algorytm Shamira"""
    obraz1 = np.zeros((wymiary, wymiary * 2), dtype=int)
    obraz2 = np.zeros((wymiary, wymiary * 2), dtype=int)

    for i in range(wymiary):
        for j in range(wymiary):
            bit = orygialny[i, j]
            pattern = random.choice([[1, 0], [0, 1]])

            if bit == 0:
                # Biały: ten sam wzór w obu
                obraz1[i, j*2] = pattern[0]
                obraz1[i, j*2+1] = pattern[1]
                obraz2[i, j*2] = pattern[0]
                obraz2[i, j*2+1] = pattern[1]
            else:
                # Czarny: odwrotny wzór
                obraz1[i, j*2] = pattern[0]
                obraz1[i, j*2+1] = pattern[1]
                obraz2[i, j*2] = pattern[1]
                obraz2[i, j*2+1] = pattern[0]
    return obraz1, obraz2

oryginalny = np.zeros((wymiary, wymiary), dtype=int)
oryginalny[10,10:90] = 1 # pozioma linia gora
oryginalny[90,10:90] = 1 # pozioma linia dol
oryginalny[10:90,10] = 1 # pionowa linia lewo
oryginalny[10:91,90] = 1 # pionowa linia prawo


losowy = np.zeros((wymiary, 2*wymiary), dtype=int)
for i in range(wymiary):
    for j in range(wymiary):
        x1, x2 = generowanieDwojki()
        losowy[i,j] = x1
        losowy[i,j+wymiary] = x2

zakodowany = shamirWizualny(oryginalny, losowy)

fig, axs = plt.subplots(2, 2)
axs[0,0].imshow(oryginalny, cmap='gray')
axs[0,0].set_title('Oryginalny obraz')
axs[0,0].axis('off')
axs[0,1].imshow(losowy, cmap='gray')
axs[0,1].set_title('Losowy obraz')
axs[0,1].axis('off')
axs[1,0].imshow(zakodowany, cmap='gray')
axs[1,0].set_title('Zakodowany obraz')
axs[1,0].axis('off')
axs[1,1].imshow(losowy, cmap='gray')
axs[1,1].set_title('Odkodowany obraz')
axs[1,1].axis('off')
plt.show()