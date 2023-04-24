"""
TODO
"""

from math import nan, isnan
""" Standardbibliothek Imports """

from core.metrics import Metrics
""" Lokale Imports """

from pprint import pprint
import pandas as pd
import numpy as np
""" Third Party Imports """

TEXT = 0
LABEL = 1
""" Globale Variablen und Konstanten """

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)
""" Pandas-Optionen, um die vollständigen Tabellen zu printen """

class CreateAnalyses():
    def __init__(self, intra_id_list, inter_id_list, intra_metrics, inter_metrics, scale_format, categories, weights, data):
        # Daten, die von der Klasse für die Analyse gebraucht werden
        self.debug = True
        self.intra_id_list = intra_id_list
        self.inter_id_list = inter_id_list
        self.intra_metrics = intra_metrics
        self.inter_metrics = inter_metrics
        self.scale_format = scale_format
        self.categories = categories
        self.weights = weights
        self.data = data                            # Format entspricht dem labels-Format in der FileValidation-Klasse

        # Ergebnisse der Analyse
        """
        self.results = {
            "intra": {
                5: {                    # ID
                    "metrik 1": {
                        1: 0.87,        # 1 Replikat
                        2: 0.31,        # 2 Replikate
                        ...
                    },
                    "metrik 2": {
                        1: 0.66,
                        2: 0.24,
                        ...
                    },
                    ...
                },
                ...
            },
            "inter": {
                "metrik 1": {
                    1: 0.56,        # 1 Replikat
                    2: 0.34,        # 2 Replikate
                    ...
                },
                "metrik 2": {
                    1: 0.77,
                    2: 0.45,
                    ...
                },
                ...
            },
            ...
        }
        """
        self.results = {
            "intra": {},
            "inter": {}
        }
        if self.intra_id_list and self.intra_metrics:
            if self.debug:
                print("Enter intra analysis")
            self.create_intra_analyses()

        if self.inter_id_list and self.inter_metrics:
            if self.debug:
                print("Enter inter analysis")
            self.create_inter_analyses()

        if self.debug:
            print("Intra ID's:")
            print(self.intra_id_list)
            print("Intra Metrics:")
            print(self.intra_metrics)
            print()

            print("Inter ID's:")
            print(self.inter_id_list)
            print("Inter Metrics:")
            print(self.inter_metrics)
            print()

            print("Skalenformat")
            print(self.scale_format)
            print()

            print("Kategorien")
            print(self.categories)
            print()

            print("Gewichte")
            print(self.weights)
            print()

            print("Daten")
            print(self.data)
            print()

            print("Results")
            print(self.results)
            print()


    def create_intra_analyses(self):
        for id in self.intra_id_list:
            self.results["intra"][id] = {}

            ratings = self.find_intra_ratings(id)

            if self.debug:
                print("Intra Ratings for ID " + str(id)+ ":")
                print(ratings)
                print()

            calculations = Metrics(self.scale_format, self.categories, ratings, self.weights)
            self.results["intra"][id] = calculations.analysis

            if self.debug:
                print("Intra Analyse for ID " + str(id)+ ":")
                print(self.results["intra"][id])
                print()

    def create_inter_analyses(self):
        ratings = self.find_inter_ratings()
        if self.debug:
            print("Inter Ratings:")
            print(ratings)
            print()
        
        calculations = Metrics(self.scale_format, self.categories, ratings, self.weights)
        self.results["inter"] = calculations.analysis

    def find_intra_ratings(self, id):
        """
        Sucht aus dem self.data-Objekt die Ratings raus vom user (id).

        Beispiel ret Dictionary:
        {'Subject 1': ['Positiv', 'Positiv', 'Positiv', 'Positiv'], 
        'Subject 2': ['Positiv', 'Neutral', 'Positiv', 'Positiv'], 
        'Subject 3': ['Positiv', 'Neutral', 'Positiv', 'Positiv'], 
        'Subject 4': ['Positiv', 'Neutral', 'Positiv'], 
        'Subject 5': ['Positiv', 'Neutral', 'Positiv']
        }

        Output:
        Pandas dataframe
        Subject 1   Positiv | Positiv | Positiv | Positiv
        Subject 2   Positiv | Neutral | Positiv | Positiv
        Subject 3   Positiv | Neutral | Positiv | Positiv
        Subject 4   Positiv | Neutral | Positiv | None
        Subject 5   Positiv | Neutral | Positiv | None
        """
        ret = {}
        for rating in self.data[id]:
            if not isinstance(rating[LABEL], str) or rating[LABEL] == "":
                # Nullwerte überspringen
                continue
            if rating[TEXT] in ret:
                # Falls das Subject rating[TEXT] schon im dictionary vorhanden ist, füge
                # das Label vom Repilkat hinzu.
                ret[rating[TEXT]].append(rating[LABEL])
            else:
                # Andernfalls füge das erste Label hinzu
                ret[rating[TEXT]] = [rating[LABEL]]
        if self.debug:
            # Keys entfernen, die nur einmal bewertet worden sind. Die sind nicht relevant für intrarater.
            ret_rmv = {k: v for k, v in ret.items() if len(v) >= 2}
        return pd.DataFrame.from_dict(ret_rmv, orient="index")


    def find_inter_ratings(self):
        ret = {}
        for i, id in enumerate(self.inter_id_list):
            for rating in self.data[id]:
                if rating[TEXT] in ret:
                    # Duplikate überspringen; sind nur für Intra-Rater-Analyse relevant
                    if len(ret[rating[TEXT]]) > i:
                        continue

                    # Falls das Subject rating[TEXT] schon im dictionary vorhanden ist, füge
                    # das Label vom Repilkat hinzu.
                    ret[rating[TEXT]].append(rating[LABEL])
                else:
                    # Andernfalls füge das erste Label hinzu
                    ret[rating[TEXT]] = [rating[LABEL]]

        return pd.DataFrame.from_dict(ret, orient="index")                

