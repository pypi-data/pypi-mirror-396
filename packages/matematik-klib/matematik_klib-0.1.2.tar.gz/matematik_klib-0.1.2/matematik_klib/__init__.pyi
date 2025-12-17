from __future__ import annotations
from typing import Sequence, Tuple, overload



# ------------------ FUNCTIONS ------------------

@overload
def potens(grundtal: float, eksponent: float) -> float:
    """
    Beregner potens.

    Args:
        grundtal_or_list (float): Tallet(eller en liste bestående af grundtallet og eksponenten) som skal opløftes.
        eksponent (float): Det som grundtallet skal opløftes i.

    Returns:
        float: Resultatet af potensen.
    """
    ...


@overload
def potens(liste: Sequence[float]) -> float: ...


@overload
def nrod(radikanden_eller_grundtallet: float, rodeksponenten_nte_rod: float) -> float:
    """
    Finder n'te rodden af Radikanden / Grundtallet.

    Args:
        radikanden_or_list (float | Sequence[float]): Tallet(eller liste med radikand og rodeksponent) der skal findes rodden på.
        rodeksponent (float | ikke opligatiorisk): rodeksponenten hvis der bruges liste skal dette ikke udfyldes her men i listen.

    Returns:
        float: n'te rodden af radikanden.
    """
    ...


@overload
def nrod(liste: Sequence[float]) -> float: ...


# ------------------ CLASS Polynomier ------------------

class Polynomier:
    @overload
    def andengrads(self, a: float, b: float, c: float) -> Tuple[float, float]:
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
        ...

    @overload
    def andengrads(self, liste: Sequence[float]) -> Tuple[float, float]: ...

    @overload
    def tredjegrads(self, a: float, b: float, c: float, d: float) -> Tuple[float, float, float]:
        """
        Løser en tredjegrads-ligning: ax^3 + bx^2 + cx + d = 0

        Args:
            a_or_liste (float | Sequence[float]):
                - Hvis du sender separate argumenter, er dette `a`.
                - Hvis du sender en liste eller tuple, skal den indeholde [a, b, c, d].
            b (float, ikke obligatiorisk): Koeffisienten for x^2. Obligatorisk hvis a_or_liste er et enkelt tal.
            c (float, ikke obligatiorisk): Koeffisienten for x. Obligatorisk hvis a_or_liste er et enkelt tal.
            d (float, ikke obligatiorisk): Konstantleddet. Obligatorisk hvis a_or_liste er et enkelt tal.

        Returns:
            tuple[float, float, float]: Løsningene til tredjegrads-ligningen.
        """
        ...

    @overload
    def tredjegrads(self, liste: Sequence[float]) -> Tuple[float, float, float]: ...

class Areal:
    @overload
    def firkant(self, hojde_or_lengde_or_liste: float, bredde: float) -> float:
        """Finder arealet af en kvadrat ud fra højde og bredde.
            
        Args:
            hojde_or_lengde_or_liste (float | Sequence[float]): liste eller højde/længde.
            bredde (float | ikke opligatioisk): bredden skal ikke skrves for sig selv hvis der bruges 1 liste.
        Returns:
            float: areal i cm^2.
        """ 
        ...
    @overload
    def firkant(self, hojde_or_lengde_or_liste: Sequence[float], bredde: None=None) -> float: ...
    @overload
    def cirkel(self, radius: float) -> float:
        """
        finder arealet af en cirkel ud fra radius.

        Args:
            radius (float): er radiusen af cirklen du vil finde arealet på.
        Returns:
            float: areal i cm^2 er ikke helt precis da pi er taget med udgangspunkt i at det er 3,14159.
        """
        ...
    @overload
    def retvinklet_trekant(hojde_or_liste: float, bredde: float) -> float:
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
        ...
    @overload
    def retvinklet_trekant(hojde_or_liste: Sequence[float],bredde: None=None) -> float: ...
