from __future__ import annotations

from typing import Sequence, Tuple

# ------------------ POLYNOMIER CLASS ------------------

class Polynomier:
    @staticmethod
    def andengrads(a_or_liste, b=None, c=None) -> Tuple[float, float]:
        """
        Løser andengrads polynomier når de er = 0.

        Args:
            a_or_liste (float | Sequence[float]):
                - Hvis du sender separate argumenter, er dette `a` (koefficienten for x^2).
                - Hvis du sender en liste eller tuple, skal den indeholde [a, b, c].
            b (float, ikke obligatiorisk): Koefficienten for x. Obligatiorisk hvis `a_or_liste` er et enkelt tal.
            c (float, ikke obligatiorisk): Konstantleddet. Obligatiorisk hvis `a_or_liste` er et enkelt tal.
        Returns:
            tuple[float, float]: Løsningerne til andengrads-ligningen.
        """
        if b is None and c is None:
            a, b, c = a_or_liste
        d = b**2 - 4*a*c
        return ((-b + d**0.5)/(2*a), (-b - d**0.5)/(2*a))

    @staticmethod
    def tredjegrads(a_or_liste, b=None, c=None, d=None) -> Tuple[float, float, float]:
        """
        Løser en tredjegrads-ligning: ax^3 + bx^2 + cx + d = 0

        Args:
            a_or_liste (float | Sequence[float]):
                - Hvis du sender separate argumenter, er dette `a`.
                - Hvis du sender en liste eller tuple, skal den inneholde [a, b, c, d].
            b (float, ikke obligatiorisk): Koeffisienten for x^2. Obligatorisk hvis a_or_liste er et enkelt tal.
            c (float, ikke obligatiorisk): Koeffisienten for x. Obligatorisk hvis a_or_liste er et enkelt tal.
            d (float, ikke obligatiorisk): Konstantleddet. Obligatorisk hvis a_or_liste er et enkelt tal.

        Returns:
            tuple[float, float, float]: Løsningene til tredjegrads-ligningen.
        """
        if b is None and c is None and d is None:
            a, b, c, d = a_or_liste
        else:
            a = a_or_liste

        f = ((3 * c / a) - (b ** 2) / (a ** 2)) / 3
        g = ((2 * (b ** 3) / (a ** 3)) - (9 * b * c) / (a ** 2) + (27 * d) / a) / 27
        h = (g ** 2) / 4 + (f ** 3) / 27

        if h > 0:
            R = -(g / 2) + h ** 0.5
            S = R ** (1 / 3)
            T = -(g / 2) - h ** 0.5
            U = abs(T) ** (1 / 3)
            root1 = (S + U) - b / (3 * a)
            root2 = root3 = float('nan')
        else:
            import math
            i = (g ** 2 / 4 - h) ** 0.5
            j = i ** (1 / 3)
            k = math.acos(-(g / (2 * i)))
            L = -j
            M = math.cos(k / 3)
            N = math.sqrt(3) * math.sin(k / 3)
            root1 = 2 * j * math.cos(k / 3) - b / (3 * a)
            root2 = L * (M + N) - b / (3 * a)
            root3 = L * (M - N) - b / (3 * a)
        return (root1, root2, root3)

# ------------------ FUNCTIONS ------------------

def potens(grundtal_or_list: float | Sequence[float], eksponent: float | None = None) -> float:
    """
    Beregner potens.

    Args:
        grundtal_or_list (float): Tallet(eller en liste bestående af grundtallet og eksponenten) som skal opløftes.
        eksponent (float): Det som grundtallet skal opløftes i.

    Returns:
        float: Resultatet af potensen.
    """
    if eksponent is None:
        grundtal, eksponent = grundtal_or_list
    else:
        grundtal = grundtal_or_list
    return grundtal ** eksponent

def nrod(radikanden_or_list: float | Sequence[float], rodeksponent: float | None = None) -> float:
    """
    Finder n'te rodden af Radikanden / Grundtallet.

    Args:
        radikanden_or_list (float | Sequence[float]): Tallet(eller liste med radikand og rodeksponent) der skal findes rodden på.
        rodeksponent (float | ikke opligatiorisk): rodeksponenten hvis der bruges liste skal dette ikke udfyldes her men i listen.
    Returns:
        float: n'te rodden af radikanden.
    """
    if rodeksponent is None:
        radikanden, rodeksponent = radikanden_or_list
    else:
        radikanden = radikanden_or_list
    return radikanden ** (1/rodeksponent)
class Areal:
    @staticmethod
    def firkant(hojde_or_lengde_or_liste: float | Sequence[float], bredde: float | None=None) -> float:
        """Finder arealet af en kvadrat ud fra højde og bredde.
            
        Args:
            hojde_or_lengde_or_liste (float | Sequence[float]): liste eller højde/længde.
            bredde (float | ikke opligatioisk): bredden skal ikke skrves for sig selv hvis der bruges 1 liste.
        Returns:
            float: areal i cm^2.
        """
        if bredde is None:
            hob, bredde = hojde_or_lengde_or_liste
        else:
            hob = hojde_or_lengde_or_liste
        return hob * bredde
    @staticmethod
    def cirkel(radius: float) -> float:
        """
        finder arealet af en cirkel ud fra radius.

        Args:
            radius (float): er radiusen af cirklen du vil finde arealet på.
        Returns:
            float: areal i cm^2 er ikke helt precis da pi er taget med udgangspunkt i at det er 3,14159.
        """
        return ((radius**2)*3.14159)
    @staticmethod
    def retvinklet_trekant(hojde_or_liste: float | Sequence[float], bredde: float | None=None) -> float:
        """
        finder arealet af en Retvinklet trekant.

        Args:
            hojde_or_liste (float | Sequence[float]): 
                - højden af trekanten.
                - liste med højde, bredde.
            bredde (float | ikke opligatiorisk): er bredden af trekanten.
        Returns:
            float: areal i cm^2
        """
        if bredde is None:
            hojde, bredde = hojde_or_liste
        else:
            hojde = hojde_or_liste
        return (hojde*bredde)/2

# ------------------ ALIASES ------------------

pot = potens
rod = nrod
