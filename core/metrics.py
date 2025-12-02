"""
In dem Modul wird eine Klasse definiert, die alle Metriken beinhaltet, die im Programm verwendet werden
TODO ...
"""

import irrCAC as ir
from irrCAC.raw import CAC 
import pingouin as pg
import pandas as pd
import numpy as np
""" Third Party Imports """

import decimal as dec
import math
from math import isnan
""" Standardbibliothek Imports """

def _compute_weight_matrix(n, mode="linear"):
    """Compute a weight matrix of size n x n.
    
    Args:
        n: Size of the matrix.
        mode: Mode of computation. Can be 'linear', 'quadratic' or any other string.
    
    Returns:
        A 2D list representing the weight matrix.
    """
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if mode == "linear":
                matrix[i][j] = 1 - abs(i - j) / (n - 1)
            elif mode == "quadratic":
                matrix[i][j] = 1 - ((i - j) ** 2) / ((n - 1) ** 2)
            else:
                matrix[i][j] = 1 if i == j else 0
    return matrix

FIRST_REPLIACTE = 0
SECOND_REPLICATE = 1
""" Globale Variablen und Konstanten """


class Metrics():
    """
    Die Klasse berechnet in Abhängigkeit vom Skalenformat, den Kategorien, den Gewichten und den Ratings Reliabilitätswerte.
    Die Ratings werden in einem Pandas-Dataframe-Objekt übergeben, der das folgende Format hat (Units-Spalte ist eine
    Indexspalte und somit kein eigener Header):

            Rater1  Rater2  Rater3  Rater4
    Units
    0         1.0     1.0     NaN     1.0
    1         2.0     2.0     3.0     2.0
    2         3.0     3.0     3.0     3.0
    3         3.0     3.0     3.0     3.0
    4         2.0     2.0     2.0     2.0
    5         1.0     2.0     3.0     4.0
    6         4.0     4.0     4.0     4.0
    7         1.0     1.0     2.0     1.0
    8         2.0     2.0     2.0     2.0
    9         NaN     5.0     5.0     5.0
    10        NaN     NaN     1.0     1.0
    11        NaN     NaN     3.0     NaN
    """
    def __init__(
        self,
        scale_format: str,
        categories: list,
        ratings: pd.DataFrame,
        weights: list
    ) -> None:
        """Initialize the Metrics object.
        
        Args:
            scale_format: The scale format.
            categories: List of categories.
            ratings: DataFrame of ratings.
            weights: List of weights.
        """
        self.debug = False
        self.scale_format = scale_format
        self.categories = categories
        self.ratings = ratings
        self.quantity_subjects = len(self.ratings)
        self.replications = 2
        self.weights = weights
        self.analysis = None
        if scale_format in ("ordinal", "nominal"):
            try:
                self.analysis = CAC(ratings=self.ratings, weights=self.weights, categories=self.categories, digits=4)
            except Exception as e:
                print(f"Exception creating irrCAC analysis: {e}")
        else:
            try:
                self.analysis = self.icc()
            except Exception as e:
                print(f"Exception creating pingouin analysis: {e}")

        dec.setcontext(dec.Context(prec=34))

        if self.debug:
            print("Ratings")
            print("len(ratings): " + str(len(self.ratings)))
            print("len(ratings.columns): " + str(len(self.ratings.columns)))
            print(self.ratings)
            print()

            print("Analyse")
            print(self.analysis)
            print()

            if self.scale_format == "ordinal" or self.scale_format == "nominal":
                print("Cohen's Kappa")
                print(self.analysis.conger())
                print()

                print("Fleiss Kappa")
                print(self.analysis.fleiss())
                print()

                print("Gwet's AC")
                print(self.analysis.gwet())
                print()

                print("Krippendorff's Alpha")
                print(self.analysis.krippendorff())
                print()



    def cohens_kappa(self):
        """Calculate Cohen's Kappa for nominal data.
        
        Returns:
            The calculated Cohen's Kappa value.
        """
        return self.analysis.conger()["est"]["coefficient_value"]

    def fleiss_kappa(self):
        """Calculate Fleiss' Kappa.
        
        Returns:
            The calculated Fleiss' Kappa value.
        """
        return self.analysis.fleiss()["est"]["coefficient_value"]

    def gwets_ac(self):
        """Calculate Gwet's AC.
        
        Returns:
            The calculated Gwet's AC value.
        """
        return self.analysis.gwet()["est"]["coefficient_value"]


    def krippendorfs_alpha(self):
        """Calculate Krippendorff's Alpha.
        
        Returns:
            The calculated Krippendorff's Alpha value.
        """
        return self.analysis.krippendorff()["est"]["coefficient_value"]

    def g_index(self):
        """Calculate G_Index for nominal data.
        
        Returns:
            The calculated G_Index value.
        """
        #TODO Vorraussetzungen checken
        q = len(self.categories)
        p_a = self.overall_agreement()

        g_index = (p_a - (dec.Decimal("1") / q)) / (dec.Decimal("1") - (dec.Decimal("1") / q))

        return float(round(g_index, 4))

    def icc(self):
        """Calculate the different ICC values with the pingouin package.
        
        Returns:
            A DataFrame with the calculated ICC values.
        """
        pg_targets = []
        pg_raters = []
        pg_ratings = []
        for i in range(len(self.ratings.columns)):
            for j in range(len(self.ratings)):
                pg_targets.append(j)
                pg_raters.append(self.ratings.columns[i])
            pg_ratings += list(self.ratings[self.ratings.columns[i]])

        df = pd.DataFrame({'pg_targets': pg_targets,
                        'pg_raters': pg_raters,
                        'pg_ratings': pg_ratings})

        if self.debug:
            print("pg_targets")
            print(pg_targets)
            print()
            print("pg_raters")
            print(pg_raters)
            print()
            print("pg_ratings")
            print(pg_ratings)
            print()
        icc = pg.intraclass_corr(data=df, targets="pg_targets", raters="pg_raters", ratings="pg_ratings", nan_policy="omit").round(4)
        # get coef. value: icc.iloc[2]["ICC"]
        return icc

    # Helper functions
    def overall_agreement(self):
        """Calculate the overall agreement.
        
        Returns:
            The calculated overall agreement value.
        """
        q = len(self.categories)
        p_a = dec.Decimal("0")
        if self.replications == 2:
            # Quelle: INTRARATER RELIABILITY, KILEM L. GWET, STATAXIS Consulting, Gaithersburg, Maryland
            # Paper S. 8 - Gleichung (12)
            for k in range(q):
                # p_a berechnet den Anteil wo die beiden Replikate bei den Subjects gleich bewertet worden sind.
                current_cat = self.categories[k]
                subject_kk = dec.Decimal("0")

                for subject in self.ratings:
                    if self.ratings[subject][FIRST_REPLIACTE] == current_cat and self.ratings[subject][FIRST_REPLIACTE] == self.ratings[subject][SECOND_REPLICATE]:
                        subject_kk += dec.Decimal("1")
                p_kk = subject_kk
                p_a += p_kk / self.quantity_subjects

            return p_a
        elif self.replications > 2:
            # m subjects, n replications per subject, q categories.
            # Quelle: INTRARATER RELIABILITY, KILEM L. GWET, STATAXIS Consulting, Gaithersburg, Maryland
            # Paper S. 9 - Gleichung (16)
            m = self.quantity_subjects
            n = self.replications

            for i in self.ratings:
                for k in range(q):
                    n_i_k = dec.Decimal("0")

                    for replicate_label in self.ratings[i]:
                        # Anzahl der Replikate in subject i berechnen, die der Kategorie k zugewiesen worden sind.
                        if replicate_label == self.categories[k]:
                            n_i_k += dec.Decimal("1")
                    
                    p_a += n_i_k * (n_i_k - 1) / (n * (n - 1))
            
            return p_a / m
        else:
            raise ValueError("Not enough replications per subject to calculate an overall agreement.")
    

def map_metrics(metric):
    """Map metric names to function names.
    
    Args:
        metric: The name of the metric.
    
    Returns:
        The name of the function that calculates the metric.
    """
    if metric == "Cohen's-|Conger's κ":
        return "conger"
    elif metric == "Fleiss' κ":
        return "fleiss"
    elif metric == "Krippendorff's α":
        return "krippendorff"
    elif metric == "Gwet's AC":
        return "gwet"